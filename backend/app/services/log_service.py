"""
log_service.py
Service layer untuk Log Pertemuan (Daily Log).
Menangani: single input (form)
"""
import io
import logging
import os
import uuid
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.models import LogPertemuan, Kelas, Murid
from app.schemas.schemas import LogPertemuanCreate, LogPertemuanUpdate
from app.services.plan_service import update_knowledge_states

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm", ".csv"}

# Mapping kolom dari file CSV/Excel ke field database
COLUMN_MAP = {
    "tanggal": "tanggal",
    "topik": "topik",
    "nilai": "nilai",
    "catatan": "catatan",
    "tingkat_pemahaman": "tingkat_pemahaman",
    "tingkat_keterlibatan": "tingkat_keterlibatan",
    "kompetensi_dicapai": "kompetensi_dicapai",
    "target_materi_berikutnya": "target_materi_berikutnya",
    "kendala": "kendala",
    "durasi_menit": "durasi_menit",
    "metode_belajar": "metode_belajar",
    "murid_id": "murid_id",
}


# ── Single Log (Form) ─────────────────────────────────────────────────────────

def create_log(db: Session, data: LogPertemuanCreate) -> LogPertemuan:
    """F001 — Simpan satu log pertemuan dari form & Trigger BKT."""
    log = LogPertemuan(
        id=str(uuid.uuid4()),
        **data.model_dump(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    # =========================================================================
    # [PENYESUAIAN] Trigger BKT Engine secara otomatis setelah log berhasil disimpan
    # =========================================================================
    try:
        update_knowledge_states(db, murid_id=data.murid_id, kelas_id=data.kelas_id)
    except Exception as e:
        logger.error(f"Gagal update BKT untuk murid {data.murid_id}: {e}")
        
    return log

def get_log_by_id(db: Session, log_id: str) -> Optional[LogPertemuan]:
    return db.query(LogPertemuan).filter(LogPertemuan.id == log_id).first()


def get_logs_by_kelas(
    db: Session,
    kelas_id: str,
    murid_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[LogPertemuan]:
    """Ambil semua log untuk satu kelas, opsional filter per murid."""
    q = db.query(LogPertemuan).filter(LogPertemuan.kelas_id == kelas_id)
    if murid_id:
        q = q.filter(LogPertemuan.murid_id == murid_id, LogPertemuan.mata_pelajaran_id.isnot(None))
    return q.order_by(LogPertemuan.tanggal.desc()).offset(skip).limit(limit).all()


def get_logs_by_murid(
    db: Session,
    murid_id: str,
    skip: int = 0,
    limit: int = 100,
) -> List[LogPertemuan]:
    return (
        db.query(LogPertemuan)
        .filter(LogPertemuan.murid_id == murid_id) # <- HAPUS filter mata_pelajaran_id di sini
        .order_by(LogPertemuan.tanggal.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_logs_hari_ini(db: Session, pengajar_id: str) -> List[LogPertemuan]:
    """Ambil log hari ini untuk semua kelas milik pengajar."""
    today = date.today()
    kelas_ids = [k.id for k in db.query(Kelas).filter(Kelas.pengajar_id == pengajar_id).all()]
    return (
        db.query(LogPertemuan)
        .filter(LogPertemuan.kelas_id.in_(kelas_ids), LogPertemuan.tanggal == today)
        .all()
    )


def update_log(db: Session, log_id: str, data: LogPertemuanUpdate) -> Optional[LogPertemuan]:
    log = get_log_by_id(db, log_id)
    if not log:
        return None
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(log, field, val)
    db.commit()
    db.refresh(log)
    return log


def delete_log(db: Session, log_id: str) -> bool:
    log = get_log_by_id(db, log_id)
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True


