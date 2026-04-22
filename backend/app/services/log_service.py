"""
log_service.py
Service layer untuk Log Pertemuan (Daily Log).
Menangani: single input (form), bulk input (CSV/Excel), CRUD.
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
from app.schemas.schemas import LogPertemuanCreate, LogPertemuanUpdate, BulkUploadResponse

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
    """F001 — Simpan satu log pertemuan dari form."""
    log = LogPertemuan(
        id=str(uuid.uuid4()),
        **data.model_dump(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
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
        q = q.filter(LogPertemuan.murid_id == murid_id)
    return q.order_by(LogPertemuan.tanggal.desc()).offset(skip).limit(limit).all()


def get_logs_by_murid(
    db: Session,
    murid_id: str,
    skip: int = 0,
    limit: int = 100,
) -> List[LogPertemuan]:
    return (
        db.query(LogPertemuan)
        .filter(LogPertemuan.murid_id == murid_id)
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


# ── Bulk Upload (CSV / Excel) ─────────────────────────────────────────────────

def _validate_extension(filename: str) -> str:
    """Validasi ekstensi file. Return ekstensi jika valid."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Format file '{ext}' tidak didukung. "
            f"Gunakan: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext


def _read_file_to_df(file_bytes: bytes, ext: str) -> pd.DataFrame:
    """Baca bytes file ke DataFrame berdasarkan ekstensi."""
    buf = io.BytesIO(file_bytes)
    if ext == ".csv":
        return pd.read_csv(buf)
    else:
        return pd.read_excel(buf, engine="openpyxl")


def _parse_row(row: Dict, kelas_id: str) -> Tuple[Optional[LogPertemuan], Optional[str]]:
    """
    Parse satu baris DataFrame menjadi objek LogPertemuan.
    Mengembalikan (LogPertemuan, None) jika berhasil,
    atau (None, pesan_error) jika gagal.
    """
    try:
        # Field wajib
        tanggal_raw = row.get("tanggal")
        topik       = str(row.get("topik", "")).strip()
        if not topik:
            return None, "Kolom 'topik' tidak boleh kosong"

        # Parse tanggal
        if isinstance(tanggal_raw, str):
            tanggal = pd.to_datetime(tanggal_raw).date()
        elif hasattr(tanggal_raw, "date"):
            tanggal = tanggal_raw.date()
        else:
            tanggal = date.today()

        # Field opsional
        nilai = float(row["nilai"]) if pd.notna(row.get("nilai")) else None
        murid_id = str(row["murid_id"]).strip()
        if not murid_id:
            return None, "Kolom 'murid_id' tidak boleh kosong"

        log = LogPertemuan(
            id=str(uuid.uuid4()),
            kelas_id=kelas_id,
            murid_id=murid_id,
            tanggal=tanggal,
            topik=topik,
            nilai=nilai,
            catatan=str(row.get("catatan", "") or ""),
            tingkat_pemahaman=str(row.get("tingkat_pemahaman", "") or "") or None,
            tingkat_keterlibatan=str(row.get("tingkat_keterlibatan", "") or "") or None,
            kompetensi_dicapai=str(row.get("kompetensi_dicapai", "") or "") or None,
            target_materi_berikutnya=str(row.get("target_materi_berikutnya", "") or "") or None,
            kendala=str(row.get("kendala", "") or "") or None,
            durasi_menit=int(row["durasi_menit"]) if pd.notna(row.get("durasi_menit")) else None,
            metode_belajar=str(row.get("metode_belajar", "") or "") or None,
        )
        return log, None
    except Exception as e:
        return None, str(e)


async def bulk_upload_log(
    db: Session,
    kelas_id: str,
    upload_file: UploadFile,
) -> BulkUploadResponse:
    """
    F002 — Import log pertemuan dari file CSV atau Excel.
    Memvalidasi setiap baris, menyimpan yang valid, melaporkan yang gagal.
    """
    # Validasi ekstensi
    ext = _validate_extension(upload_file.filename or "")

    # Baca file
    file_bytes = await upload_file.read()
    if len(file_bytes) == 0:
        raise ValueError("File kosong")

    df = _read_file_to_df(file_bytes, ext)

    if df.empty:
        raise ValueError("File tidak memiliki data")

    # Normalisasi nama kolom (lowercase & strip)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    berhasil = 0
    gagal    = 0
    errors: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        log_obj, err = _parse_row(row.to_dict(), kelas_id)
        if err:
            gagal += 1
            errors.append({"baris": int(idx) + 2, "error": err})
            continue
        try:
            db.add(log_obj)
            db.flush()   # cek constraint tanpa commit dulu
            berhasil += 1
        except Exception as e:
            db.rollback()
            gagal += 1
            errors.append({"baris": int(idx) + 2, "error": str(e)})

    if berhasil > 0:
        db.commit()

    return BulkUploadResponse(
        total_baris=len(df),
        berhasil=berhasil,
        gagal=gagal,
        detail_error=errors,
    )
