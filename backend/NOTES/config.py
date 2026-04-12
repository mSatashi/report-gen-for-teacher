"""
config.py
─────────────────────────────────────────────────────────────────────────────
Semua konfigurasi aplikasi dibaca dari file .env di root folder backend.
Tidak ada nilai yang di-hardcode di sini kecuali nilai default fallback
yang aman untuk development lokal.

Cara pakai:
    from app.core.config import settings
    print(settings.DATABASE_URL)
    print(settings.SECRET_KEY)
─────────────────────────────────────────────────────────────────────────────
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Pydantic BaseSettings membaca nilai dari:
      1. Environment variable sistem (os.environ)
      2. File .env di root folder backend (otomatis di-load)

    Urutan prioritas: env variable > .env file > nilai default di sini.
    """

    # ── Database ─────────────────────────────────────────────────────────────
    # Contoh untuk PostgreSQL lokal:
    #   DATABASE_URL=postgresql://postgres:password@localhost:5432/adaptive_db
    # Contoh untuk Docker (nama service = postgres):
    #   DATABASE_URL=postgresql://postgres:password@postgres:5432/adaptive_db
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/adaptive_db"

    # ── JWT / Security ────────────────────────────────────────────────────────
    # Ganti dengan string acak yang panjang dan tidak mudah ditebak.
    # Generate contoh: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = "ganti-ini-dengan-secret-key-yang-kuat-minimal-32-karakter"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # default 24 jam

    # ── Ollama / AI ───────────────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # ── SMTP (untuk kirim email laporan) ──────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None       # isi dengan email pengirim
    SMTP_PASSWORD: Optional[str] = None   # isi dengan app password Gmail / SMTP
    SMTP_FROM: Optional[str] = None       # isi dengan email pengirim (bisa sama dengan SMTP_USER)

    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "Sistem Perencanaan Materi Adaptif"
    DEBUG: bool = False

    # ── Pydantic v2: baca dari file .env ─────────────────────────────────────
    # env_file = ".env" → cari file .env di direktori kerja saat app dijalankan
    # env_file_encoding = "utf-8" → pastikan karakter khusus terbaca dengan benar
    # extra = "ignore" → abaikan variabel .env yang tidak ada di class ini
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instance tunggal yang dipakai di seluruh aplikasi
settings = Settings()
