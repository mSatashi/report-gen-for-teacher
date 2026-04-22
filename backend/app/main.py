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
from app.models import models  # noqa: F401
from app.routers import (
    auth, 
    dashboard, 
    log, 
    laporan, 
    plan, 
    kelas, 
    diagnostic, 
    murid, 
    bkt, 
    mata_pelajaran,
    ks,
    ai,
)
 
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
 
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR + "pdf/", exist_ok=True)
 
if settings.APP_ENV == "development":
    Base.metadata.create_all(bind=engine)
    logger.info("Tabel database berhasil di-sync (dev mode)")
 
# [OPSIONAL] Auto-load BKT params dari file tuning saat startup
if getattr(settings, "AUTO_LOAD_BKT_PARAMS", False):
    params_file = getattr(settings, "BKT_PARAMS_FILE", "experiment/models/bkt_global_params.csv")
    try:
        from scripts.seed_bkt_params import load_tuned_params
        if load_tuned_params(params_file):
            logger.info(f"BKT params auto-loaded dari {params_file}")
        else:
            logger.warning("BKT params tidak ter-load, pakai default")
    except Exception as e:
        logger.warning(f"Gagal auto-load BKT params: {e}")
 
app = FastAPI(
    title="Sistem Perencanaan Materi Adaptif & Pelaporan Otomatis",
    description=(
        "Backend API — BKT + PSO + LLM Narrative Engine. "
        "Mendukung: Daily Log (F001/F002), Rencana Studi (F004), "
        "Laporan (F003/F005/F006/F007), Diagnostik (F008)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
 
PREFIX = "/api/v1"
 
app.include_router(auth.router,        prefix=PREFIX)
app.include_router(dashboard.router,   prefix=PREFIX)
app.include_router(kelas.router,       prefix=PREFIX)
app.include_router(log.router,         prefix=PREFIX)
app.include_router(laporan.router,     prefix=PREFIX)
app.include_router(plan.router,        prefix=PREFIX)
app.include_router(diagnostic.router,  prefix=PREFIX)
app.include_router(murid.router,       prefix=PREFIX)
app.include_router(bkt.router,         prefix=PREFIX)
app.include_router(mata_pelajaran.router, prefix=PREFIX)
app.include_router(ks.router,          prefix=PREFIX)
app.include_router(ai.router,          prefix=PREFIX)
 
 
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
 
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)