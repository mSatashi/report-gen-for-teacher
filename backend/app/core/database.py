"""
database.py
Koneksi ke PostgreSQL menggunakan SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # cek koneksi sebelum dipakai
    pool_size=10,             # jumlah koneksi di pool
    max_overflow=20,          # koneksi tambahan jika pool penuh
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency FastAPI: menyediakan sesi database per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
