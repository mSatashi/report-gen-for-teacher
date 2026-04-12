"""
security.py
─────────────────────────────────────────────────────────────────────────────
Fungsi kriptografi: hash password, verifikasi password, buat/decode JWT token.
SECRET_KEY dan ALGORITHM dibaca dari settings (.env), bukan hardcode.
─────────────────────────────────────────────────────────────────────────────
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Hash password dengan bcrypt.

    bcrypt membatasi input maksimal 72 byte. Password yang lebih panjang
    akan dipotong otomatis, sehingga 'password_panjang_sekali_ini'
    dan 'password_panjang_sekali_itu' bisa menghasilkan hash yang sama.
    Kita batasi eksplisit di sini untuk menghindari bug keamanan ini.
    """
    # Potong di 72 byte untuk menghindari bcrypt truncation bug
    truncated = plain_password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(truncated, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi password plain terhadap hash bcrypt yang tersimpan.
    Return True jika cocok, False jika tidak.
    """
    try:
        truncated = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(truncated, hashed_password.encode("utf-8"))
    except Exception:
        # Tangkap semua error (hash rusak, format salah, dll)
        return False


# ── JWT Token ─────────────────────────────────────────────────────────────────

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Buat JWT access token.

    Args:
        data: Payload yang akan dikodekan ke dalam token.
              Minimal harus ada key "sub" (subject = user_id).
        expires_delta: Masa berlaku token. Jika None, pakai
                       ACCESS_TOKEN_EXPIRE_MINUTES dari settings.

    Returns:
        String JWT yang bisa dikirim ke client.
    """
    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode dan verifikasi JWT token.

    Returns:
        Dict payload jika token valid dan belum expired.
        None jika token tidak valid, expired, atau rusak.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
