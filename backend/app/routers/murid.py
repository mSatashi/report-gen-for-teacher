from typing import List, Optional
 
from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.schemas.schemas import MuridCreate, uridResponse
from app.services.auth_service import get_current_user, require_pengajar
from app.services.murid_service import create_murid, get_all_murid, get_murid_by_id, delete_murid
from app.models.models import Pengguna
 
# ── Murid router ──────────────────────────────────────────────────────────────
murid_router = APIRouter(prefix="/murid", tags=["Murid"])
 
@router.post("/", response_model=MuridResponse, status_code=201)
def tambah_siswa(
    data: MuridCreate,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """Buat akun siswa baru. Hanya bisa dilakukan oleh pengajar."""
    return create_murid(db, data)
    
@murid_router.get("/", response_model=List[MuridResponse])
def list_all_murid(
    skip: int = Query(0, ge=0, description="Offset paginasi"),
    limit: int = Query(100, ge=1, le=500, description="Jumlah maksimal data"),
    search: Optional[str] = Query(None, description="Filter nama siswa"),
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    List semua siswa (master data).
    Hanya bisa diakses oleh pengajar.
    Mendukung paginasi (skip/limit) dan pencarian nama (search).
    """
    return get_all_murid(db, skip=skip, limit=limit, search=search)
 
 
@murid_router.get("/{murid_id}", response_model=MuridResponse)
def detail_murid(
    murid_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(get_current_user),
):
    """
    Detail data 1 siswa.
    Bisa diakses oleh pengajar maupun siswa itu sendiri.
    """
    return get_murid_by_id(db, murid_id)
 
 
@murid_router.delete("/{murid_id}")
def hapus_murid(
    murid_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    Hapus permanen data siswa.
    Hanya bisa dilakukan oleh pengajar.
    Data terkait (KelasMurid, dll) ikut terhapus via CASCADE.
    """
    return delete_murid(db, murid_id)