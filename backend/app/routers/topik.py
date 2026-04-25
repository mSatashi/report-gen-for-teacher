"""
topik.py — Router untuk manajemen Topik / Skill Graph
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Topik, Pengguna
from app.schemas.schemas import TopikCreate, TopikResponse
from app.services.auth_service import require_pengajar
from app.services.topik_service import tambah_prasyarat

router = APIRouter(prefix="/topik", tags=["Topik"])


@router.post("/", response_model=TopikResponse, status_code=201)
def buat_topik(
    data: TopikCreate, 
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """
    Membuat Master Topik/Materi untuk kebutuhan Skill Graph BKT/PSO.
    Hanya bisa dilakukan oleh pengajar/admin.
    """
    topik = Topik(
        id=str(uuid.uuid4()),
        mata_pelajaran_id=data.mata_pelajaran_id,
        nama=data.nama,
        difficulty_index=data.difficulty_index
    )
    db.add(topik)
    db.commit()
    db.refresh(topik)
    
    # Jika saat buat topik langsung mengirimkan prasyarat_ids
    if data.prasyarat_ids:
        for p_id in data.prasyarat_ids:
            # Memanggil service validasi Graph DFS
            tambah_prasyarat(db, topik.id, p_id)
            
    # Refresh untuk mengambil relasi prasyarat terbaru
    db.refresh(topik)
    return topik


@router.get("/mapel/{mata_pelajaran_id}", response_model=List[TopikResponse])
def get_topik_by_mapel(
    mata_pelajaran_id: str, 
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """Mengambil semua daftar topik dalam satu mata pelajaran."""
    return db.query(Topik).filter(Topik.mata_pelajaran_id == mata_pelajaran_id).all()


@router.post("/{topik_id}/prasyarat/{prasyarat_id}")
def endpoint_tambah_prasyarat(
    topik_id: str,
    prasyarat_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar)
):
    """
    Endpoint untuk menambahkan relasi prasyarat pada sebuah topik (Membangun Skill Graph).
    Dilengkapi validasi pencegahan siklus setan (Circular Dependency).
    """
    return tambah_prasyarat(db, topik_id, prasyarat_id)