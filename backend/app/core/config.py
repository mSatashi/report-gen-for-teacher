"""
config.py
Konfigurasi aplikasi menggunakan pydantic-settings.
Semua variabel dibaca dari file .env
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_ENV: str  = "development"
    DEBUG:   bool = True
 
    # ── Database (PostgreSQL) ─────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/db_pendidikan"
 
    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY:                  str = "[PLACEHOLDER_SECRET_KEY]"
    ALGORITHM:                   str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
 
    # ── Ollama (LLM lokal) ────────────────────────────────────────────────────
    OLLAMA_BASE_URL:      str = "http://localhost:11434"
    OLLAMA_MODEL_NAME:    str = "Sania:2b"
    OLLAMA_MODEL:         str = "Sania:2b"  # Alias untuk compatibility
    OLLAMA_TIMEOUT:       int = 120       # Timeout dalam detik
    PLANNER_MODEL_NAME:   str = "orca-mini"
    LLM_PROVIDER:         str = "ollama"  # atau "external"
 
    # ── LLM Generation Control (Tabel 10 laporan, Section 4.3.2) ─────────────
    # [INTEGRASI] Nilai default sesuai konfigurasi yang dipakai di 04_llm_evaluation.py
    LLM_TEMPERATURE: float = 0.6    # rentang 0.5–0.7
    LLM_TOP_P:       float = 0.9    # tetap
    LLM_MAX_TOKENS:  int   = 1024   # rentang 512–1024
 
    # ── BKT Auto-load (opsional) ──────────────────────────────────────────────
    # [INTEGRASI] Jika true, backend load bkt_global_params.csv saat startup
    AUTO_LOAD_BKT_PARAMS: bool = False
    BKT_PARAMS_FILE:      str  = "experiment/models/bkt_global_params.csv"
 
    # ── LLM Eksternal (opsional fallback) ─────────────────────────────────────
    EXTERNAL_LLM_API_URL: str = "[PLACEHOLDER_URL_API_LLM_EKSTERNAL]"
    EXTERNAL_LLM_API_KEY: str = "[PLACEHOLDER_API_KEY_LLM_EKSTERNAL]"
    EXTERNAL_LLM_MODEL:   str = "[PLACEHOLDER_NAMA_MODEL_EKSTERNAL]"
 
    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST:     str = "[PLACEHOLDER_SMTP_HOST]"
    SMTP_PORT:     int = 587
    SMTP_USERNAME: str = "[PLACEHOLDER_EMAIL]"
    SMTP_PASSWORD: str = "[PLACEHOLDER_PASSWORD_EMAIL]"
    EMAIL_FROM:    str = "[PLACEHOLDER_EMAIL]"
 
    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
 
    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]
 
    # ── Upload ────────────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR:         str = "uploads/"
 
    class Config:
        env_file = ".env"
        extra    = "ignore"
 
 
settings = Settings()