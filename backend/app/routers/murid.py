"""
murid.py — Router khusus untuk manajemen Data Master Murid
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.schemas import MuridCreate, MuridUpdate, MuridResponse
from app.services.auth_service import get_current_user, require_pengajar
from app.services.murid_service import (
    create_murid,
    get_all_murid,
    get_murid_by_id,
    update_murid,
    delete_murid
)
from app.models.models import Pengguna

router = APIRouter(prefix="/murid", tags=["Murid"])

# 1. CREATE
@router.post("/", response_model=MuridResponse, status_code=status.HTTP_201_CREATED)
def tambah_siswa(
    data: MuridCreate,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """Buat profil data murid baru. Hanya bisa dilakukan oleh pengajar."""
    return create_murid(db, data)

# 2. READ (ALL)
@router.get("/", response_model=List[MuridResponse], status_code=status.HTTP_200_OK)
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

# 3. READ (DETAIL)
@router.get("/{murid_id}", response_model=MuridResponse, status_code=status.HTTP_200_OK)
def detail_murid(
    murid_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(get_current_user),
):
    """
    Detail data 1 siswa.
    Bisa diakses oleh pengajar maupun siswa itu sendiri (jika nantinya ada fitur login siswa).
    """
    return get_murid_by_id(db, murid_id)

# 4. UPDATE
@router.put("/{murid_id}", response_model=MuridResponse, status_code=status.HTTP_200_OK)
def perbarui_murid(
    murid_id: str,
    data: MuridUpdate,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    Perbarui/Update data siswa (contoh: salah eja nama, ganti jenjang pendidikan).
    Hanya bisa dilakukan oleh pengajar.
    """
    return update_murid(db, murid_id, data)

# 5. DELETE
@router.delete("/{murid_id}", status_code=status.HTTP_200_OK)
def hapus_murid(
    murid_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    Hapus permanen data siswa.
    Hanya bisa dilakukan oleh pengajar.
    Data terkait seperti riwayat KelasMurid, LogPertemuan, dsb ikut terhapus via CASCADE database.
    """
    return delete_murid(db, murid_id)