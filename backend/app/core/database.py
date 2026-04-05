# =============================================================================
# FIX 2 ► GANTI SELURUH ISI: backend/app/core/database.py
#
# Root cause yang diperbaiki:
#   - `pool_size` dan `max_overflow` adalah argumen khusus QueuePool (PostgreSQL).
#     SQLite pakai StaticPool/NullPool — argumen tersebut menyebabkan
#     FastAPIError saat test engine SQLite dibuat.
#   - Solusi: deteksi DATABASE_URL, pakai connect_args dan pool_class
#     yang tepat untuk SQLite, biarkan default untuk PostgreSQL.
# =============================================================================

"""
database.py
Koneksi database menggunakan SQLAlchemy.
Mendukung PostgreSQL (production) dan SQLite (testing).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

_url = settings.DATABASE_URL
_is_sqlite = _url.startswith("sqlite")

if _is_sqlite:
    # SQLite: tidak pakai pool_size/max_overflow, tambah check_same_thread=False
    engine = create_engine(
        _url,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL / production
    engine = create_engine(
        _url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
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
