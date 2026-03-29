from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import register_user, login_user

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
