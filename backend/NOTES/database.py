"""
database.py
─────────────────────────────────────────────────────────────────────────────
Setup koneksi database SQLAlchemy.
DATABASE_URL dibaca dari settings (yang membaca dari .env), bukan hardcode.
─────────────────────────────────────────────────────────────────────────────
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# ── Pilih DATABASE_URL ────────────────────────────────────────────────────────
# Saat unit test berjalan, test file akan set os.environ["DATABASE_URL"]
# ke SQLite in-memory SEBELUM import apapun dari app. Kita baca ulang dari
# env di sini supaya test bisa override tanpa mengganti file .env.
DATABASE_URL = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

# ── Engine ────────────────────────────────────────────────────────────────────
# check_same_thread=False hanya dibutuhkan untuk SQLite (dipakai saat testing).
# Untuk PostgreSQL, argumen ini diabaikan secara otomatis.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # Pool settings untuk PostgreSQL production
    pool_pre_ping=True,      # ping koneksi sebelum dipakai supaya tidak stale
    pool_recycle=1800,        # daur ulang koneksi setiap 30 menit
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yield satu sesi database per request,
    lalu tutup otomatis setelah request selesai.

    Cara pakai di router:
        from app.core.database import get_db
        def my_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
