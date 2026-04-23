"""
auth_service.py
Service untuk autentikasi: register, login, get current user.
"""
import uuid
from typing import Optional, cast
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token, blacklist_token, is_token_blacklisted
from app.models.models import Pengguna, Pengajar
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse

bearer_scheme = HTTPBearer()


def register_user(db: Session, data: RegisterRequest) -> Pengguna:
    """Registrasi pengguna baru (pengajar)."""
    if db.query(Pengguna).filter(Pengguna.email_address == data.email_address).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if db.query(Pengguna).filter(Pengguna.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")

    user_id = str(uuid.uuid4())
    pengguna = Pengguna(
        id=user_id,
        username=data.username,
        email_address=data.email_address,
        hashed_password=hash_password(data.password),
        tipe_pengguna=data.tipe_pengguna,
    )
    db.add(pengguna)

    if data.tipe_pengguna == "pengajar":
        db.add(Pengajar(id=user_id))

    db.commit()
    db.refresh(pengguna)
    return pengguna


def login_user(db: Session, data: LoginRequest) -> TokenResponse:
    """Login dan kembalikan JWT token."""
    user = db.query(Pengguna).filter(Pengguna.email_address == data.email_address).first()
    if not user or not verify_password(data.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Email atau password salah")
    if not cast(bool, user.is_active):
        raise HTTPException(status_code=403, detail="Akun tidak aktif")

    token = create_access_token({"sub": user.id, "tipe": user.tipe_pengguna})
    return TokenResponse(
        access_token=token,
        tipe_pengguna=str(user.tipe_pengguna),
        user_id=str(user.id),
    )

def logout_user(token: str) -> dict:
    """
    Logout pengguna dengan memblacklist JWT token-nya.
    Karena JWT stateless, cara ini membuat token langsung tidak valid
    tanpa perlu menyimpan state ke database — cukup tambahkan ke blacklist
    in-memory (atau Redis untuk multi-worker).
    """
    blacklist_token(token)
    return {"message": "Logout berhasil. Token telah dinonaktifkan."}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> "Pengguna":
    """
    Dependency FastAPI: decode JWT, cek blacklist, kembalikan user aktif.
    Versi ini menolak token yang sudah logout.
    """
    token = credentials.credentials
 
    # Tolak jika token sudah diblacklist (sudah logout)
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token sudah tidak valid (sudah logout)")
 
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token tidak valid atau sudah expired")
 
    from app.models.models import Pengguna as PenggunaModel
    user = db.query(PenggunaModel).filter(PenggunaModel.id == payload.get("sub")).first()
    if not user or not cast(bool, user.is_active):
        raise HTTPException(status_code=401, detail="Pengguna tidak ditemukan")
    return user


def require_pengajar(current_user: Pengguna = Depends(get_current_user)) -> Pengguna:
    """Dependency: hanya pengajar yang boleh akses endpoint ini."""
    if str(current_user.tipe_pengguna) != "pengajar":
        raise HTTPException(status_code=403, detail="Hanya pengajar yang dapat mengakses fitur ini")
    return current_user
