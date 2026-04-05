"""
main.py
Entry point FastAPI — Sistem Perencanaan Materi Adaptif & Pelaporan Otomatis
"""
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine

# Import semua model agar Alembic dan create_all mengenalinya
from app.models import models  # noqa: F401

# Import routers
from app.routers import auth, dashboard, log, laporan, plan, kelas, diagnostic, murid

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Buat folder upload jika belum ada ────────────────────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR + "pdf/", exist_ok=True)

# ── Inisialisasi tabel (dev only — production pakai Alembic) ─────────────────
if settings.APP_ENV == "development":
    Base.metadata.create_all(bind=engine)
    logger.info("Tabel database berhasil di-sync (dev mode)")

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sistem Perencanaan Materi Adaptif & Pelaporan Otomatis",
    description=(
        "Backend API untuk sistem manajemen pembelajaran adaptif berbasis AI. "
        "Mendukung: Daily Log, Rencana Studi (BKT+PSO), Laporan Narasi (LLM)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (PDF output) ─────────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Register Routers ──────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router,        prefix=PREFIX)
app.include_router(dashboard.router,   prefix=PREFIX)
app.include_router(kelas.router,       prefix=PREFIX)
app.include_router(log.router,         prefix=PREFIX)
app.include_router(laporan.router,     prefix=PREFIX)
app.include_router(plan.router,        prefix=PREFIX)
app.include_router(diagnostic.router,  prefix=PREFIX)
app.include_router(murid.router,      prefix=PREFIX)

# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "app":     "Sistem Perencanaan Materi Adaptif & Pelaporan Otomatis",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}


# ── Run (dev) ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
