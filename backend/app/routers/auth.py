from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import register_user, login_user, logout_user

bearer_scheme = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Registrasi pengguna baru (pengajar atau murid)."""
    user = register_user(db, data)
    return {"message": "Registrasi berhasil", "user_id": user.id, "tipe": user.tipe_pengguna}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login dan dapatkan JWT token."""
    return login_user(db, data)

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Logout pengguna.
    Token JWT langsung diblacklist — tidak bisa dipakai lagi meski belum expired.
    Tidak butuh koneksi database.
    """
    return logout_user(credentials.credentials)