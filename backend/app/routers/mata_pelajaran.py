"""
mata_pelajaran.py — Router untuk manajemen Mata Pelajaran.
 
Endpoint:
  POST   /api/v1/mata-pelajaran/           → buat mata pelajaran baru  (pengajar)
  GET    /api/v1/mata-pelajaran/           → list semua                (pengajar)
  GET    /api/v1/mata-pelajaran/{id}       → detail satu               (pengajar)
  PUT    /api/v1/mata-pelajaran/{id}       → update                    (pengajar)
  DELETE /api/v1/mata-pelajaran/{id}       → hapus permanen            (pengajar)
"""
from typing import List, Optional
 
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.models.models import Pengguna
from app.schemas.schemas import (
    MataPelajaranCreate,
    MataPelajaranUpdate,
    MataPelajaranResponse,
)
from app.services.auth_service import require_pengajar
from app.services.mata_pelajaran_service import (
    create_mata_pelajaran,
    get_all_mata_pelajaran,
    get_mata_pelajaran_by_id,
    update_mata_pelajaran,
    delete_mata_pelajaran,
)
 
router = APIRouter(prefix="/mata-pelajaran", tags=["Mata Pelajaran"])
 
 
@router.post("/", response_model=MataPelajaranResponse, status_code=201)
def buat_mata_pelajaran(
    data: MataPelajaranCreate,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    Buat mata pelajaran baru.
    kredit wajib > 0. jam harus format HH:MM.
    Kombinasi nama + hari + jam harus unik.
    """
    return create_mata_pelajaran(db, data)
 
 
@router.get("/", response_model=List[MataPelajaranResponse])
def list_mata_pelajaran(
    skip:   int           = Query(0, ge=0),
    limit:  int           = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Filter nama mata pelajaran"),    
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    List semua mata pelajaran.
    Mendukung filter nama (search) dan hari, serta paginasi (skip/limit).
    Diurutkan berdasarkan hari → jam.
    """
    return get_all_mata_pelajaran(db, skip=skip, limit=limit, search=search, hari=hari)
 
 
@router.get("/{mapel_id}", response_model=MataPelajaranResponse)
def detail_mata_pelajaran(
    mapel_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """Detail satu mata pelajaran berdasarkan ID."""
    return get_mata_pelajaran_by_id(db, mapel_id)
 
 
@router.put("/{mapel_id}", response_model=MataPelajaranResponse)
def ubah_mata_pelajaran(
    mapel_id: str,
    data: MataPelajaranUpdate,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    Update mata pelajaran (partial — hanya field yang dikirim diubah).
    """
    return update_mata_pelajaran(db, mapel_id, data)
 
 
@router.delete("/{mapel_id}")
def hapus_mata_pelajaran(
    mapel_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """Hapus permanen mata pelajaran. Hanya pengajar."""
    return delete_mata_pelajaran(db, mapel_id)