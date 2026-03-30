"""
security.py
Fungsi keamanan: hashing password (bcrypt langsung) + JWT token.
"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# Bcrypt maksimal 72 bytes
MAX_PASSWORD_BYTES = 2056


# ── Password Hashing ──────────────────────────────────────────────────────────

def _prepare_password(password: str) -> bytes:
    """
    Encode password ke bytes dan potong maksimal 72 bytes
    (batas keras bcrypt) supaya tidak error.
    """
    return password.encode("utf-8")[:MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """Hash password menggunakan bcrypt."""
    pwd_bytes = _prepare_password(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifikasi password plain-text dengan hash yang tersimpan di DB."""
    try:
        return bcrypt.checkpw(
            _prepare_password(plain_password),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ── JWT Token ─────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Buat JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode JWT token.
    Return payload dict jika valid, None jika tidak valid atau expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
