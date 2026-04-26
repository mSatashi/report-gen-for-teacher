"""
topik.py — Router untuk manajemen Topik / Skill Graph
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Topik, Pengguna
from app.schemas.schemas import TopikCreate, TopikUpdate, TopikResponse
from app.services.auth_service import require_pengajar
from app.services.topik_service import (
    tambah_prasyarat, 
    update_topik, 
    delete_topik, 
    hapus_prasyarat
)

router = APIRouter(prefix="/topik", tags=["Topik"])

# 1. CREATE TOPIK
@router.post("", response_model=TopikResponse, status_code=status.HTTP_201_CREATED)
def buat_topik(
    data: TopikCreate, 
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Membuat Master Topik baru."""
    topik = Topik(
        id=str(uuid.uuid4()),
        mata_pelajaran_id=data.mata_pelajaran_id,
        nama=data.nama,
        difficulty_index=data.difficulty_index
    )
    db.add(topik)
    db.commit()
    db.refresh(topik)
    
    if data.prasyarat_ids:
        for p_id in data.prasyarat_ids:
            tambah_prasyarat(db, topik.id, p_id)
            
    db.refresh(topik)
    return topik

# 2. READ TOPIK
@router.get("/mapel/{mata_pelajaran_id}", response_model=List[TopikResponse])
def get_topik_by_mapel(
    mata_pelajaran_id: str, 
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Daftar topik dalam satu mata pelajaran."""
    return db.query(Topik).filter(Topik.mata_pelajaran_id == mata_pelajaran_id).all()

# 3. UPDATE TOPIK
@router.put("/{topik_id}", response_model=TopikResponse)
def perbarui_topik(
    topik_id: str,
    data: TopikUpdate,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Mengubah nama atau tingkat kesulitan topik."""
    return update_topik(db, topik_id, data)

# 4. DELETE TOPIK
@router.delete("/{topik_id}")
def hapus_topik(
    topik_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Menghapus topik secara permanen."""
    return delete_topik(db, topik_id)

# 5. MANAJEMEN PRASYARAT (RELASI)
@router.post("/{topik_id}/prasyarat/{prasyarat_id}")
def endpoint_tambah_prasyarat(
    topik_id: str,
    prasyarat_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Menghubungkan dua topik (A membutuhkan B)."""
    return tambah_prasyarat(db, topik_id, prasyarat_id)

@router.delete("/{topik_id}/prasyarat/{prasyarat_id}")
def endpoint_hapus_prasyarat(
    topik_id: str,
    prasyarat_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Memutuskan hubungan prasyarat antar topik."""
    return hapus_prasyarat(db, topik_id, prasyarat_id)