"""
log.py — Router untuk Daily Log (F001, F002)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Pengguna
from app.schemas.schemas import (
    LogPertemuanCreate, LogPertemuanUpdate, LogPertemuanResponse, BulkUploadResponse
)
from app.services.auth_service import require_pengajar
from app.services.log_service import (
    create_log, get_log_by_id, get_logs_by_kelas,
    get_logs_by_murid, get_logs_hari_ini,
    update_log, delete_log, bulk_upload_log,
)
from app.services.plan_service import update_knowledge_states

router = APIRouter(prefix="/logs", tags=["Daily Log"])


# ── GET ───────────────────────────────────────────────────────────────────────

@router.get("/hari-ini", response_model=List[LogPertemuanResponse])
def log_hari_ini(
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil semua log pertemuan hari ini untuk pengajar yang login."""
    return get_logs_hari_ini(db, current_user.id)


@router.get("/kelas/{kelas_id}", response_model=List[LogPertemuanResponse])
def logs_by_kelas(
    kelas_id: str,
    murid_id: Optional[str] = Query(None, description="Filter per murid"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil log pertemuan untuk satu kelas. Opsional filter per murid."""
    return get_logs_by_kelas(db, kelas_id, murid_id, skip, limit)


@router.get("/murid/{murid_id}", response_model=List[LogPertemuanResponse])
def logs_by_murid(
    murid_id: str,
    mata_pelajaran_id: Optional[str] = Query(None, description="Filter per mata pelajaran"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil semua log untuk satu murid."""
    return get_logs_by_murid(db, murid_id, skip, limit)


@router.get("/{log_id}", response_model=LogPertemuanResponse)
def get_log(
    log_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    log = get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
    return log


# ── POST ──────────────────────────────────────────────────────────────────────

@router.post("/", response_model=LogPertemuanResponse, status_code=201)
def tambah_log(
    data: LogPertemuanCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """F001 — Tambah satu log pertemuan via form."""
    log = create_log(db, data)
    # Update BKT knowledge state jika ada nilai dan murid_id
    if log.nilai is not None and log.murid_id:
        update_knowledge_states(db, log.murid_id, log.kelas_id)
    return log


@router.post("/bulk/{kelas_id}", response_model=BulkUploadResponse, status_code=201)
async def bulk_log(
    kelas_id: str,
    file: UploadFile = File(..., description="File CSV atau Excel (.xlsx/.xls/.csv)"),
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """F002 — Upload log pertemuan massal via CSV/Excel."""
    try:
        result = await bulk_upload_log(db, kelas_id, file)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── PUT ───────────────────────────────────────────────────────────────────────

@router.put("/{log_id}", response_model=LogPertemuanResponse)
def edit_log(
    log_id: str,
    data: LogPertemuanUpdate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Edit log pertemuan yang sudah ada."""
    log = update_log(db, log_id, data)
    if not log:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
    if log.nilai is not None and log.murid_id:
        update_knowledge_states(db, log.murid_id, log.kelas_id)
    return log


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete("/{log_id}", status_code=204)
def hapus_log(
    log_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Hapus log pertemuan."""
    if not delete_log(db, log_id):
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
