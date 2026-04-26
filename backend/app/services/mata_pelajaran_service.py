import uuid
from typing import List, Optional
from datetime import datetime
 
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.topik_service import tambah_prasyarat
from app.models.models import MataPelajaran, Topik
from app.schemas.schemas import (
    MataPelajaranCreate,
    MataPelajaranUpdate,
    MataPelajaranResponse,
)
 
 
def create_mata_pelajaran(db: Session, data: MataPelajaranCreate) -> MataPelajaranResponse:
    # 1. Cek duplikasi nama
    existing = db.query(MataPelajaran).filter(
        MataPelajaran.nama_mata_pelajaran == data.nama_mata_pelajaran
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Mata pelajaran '{data.nama_mata_pelajaran}' sudah ada")

    # 2. Simpan Mata Pelajaran
    mapel_id = str(uuid.uuid4())
    mapel = MataPelajaran(
        id=mapel_id,
        nama_mata_pelajaran=data.nama_mata_pelajaran,
    )
    db.add(mapel)
    
    # 3. Simpan Topik-topik awal (jika ada)
    if data.topik_awal:
        for t_data in data.topik_awal:
            baru_topik = Topik(
                id=str(uuid.uuid4()),
                mata_pelajaran_id=mapel_id,
                nama=t_data.nama,
                difficulty_index=t_data.difficulty_index
            )
            db.add(baru_topik)
    db.commit()
    db.refresh(mapel)
    return MataPelajaranResponse.model_validate(mapel)
 
 
def get_all_mata_pelajaran(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> List[MataPelajaranResponse]:
    """
    List semua mata pelajaran.
    - search : filter nama (case-insensitive, opsional)
    - skip / limit : paginasi
    """
    query = db.query(MataPelajaran)
 
    if search:
        query = query.filter(
            MataPelajaran.nama_mata_pelajaran.ilike(f"%{search}%")
        )
 
    rows = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [MataPelajaranResponse.model_validate(m) for m in rows]
 
 
def get_mata_pelajaran_by_id(
    db: Session, mapel_id: str
) -> MataPelajaranResponse:
    """Ambil satu mata pelajaran berdasarkan ID."""
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id).first()
    if not mapel:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")
    return MataPelajaranResponse.model_validate(mapel)
 
 
def update_mata_pelajaran(db: Session, mapel_id: str, data: MataPelajaranUpdate) -> MataPelajaranResponse:
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id).first()
    if not mapel:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    # 1. Update Nama Mata Pelajaran
    if data.nama_mata_pelajaran:
        mapel.nama_mata_pelajaran = data.nama_mata_pelajaran

    # 2. Update/Tambah Topik & Prasyarat
    if data.topik is not None:
        for t_item in data.topik:
            target_topik_id = t_item.id
            
            # A. Jika topik baru (tidak ada ID), buat dulu
            if not target_topik_id:
                target_topik_id = str(uuid.uuid4())
                baru_topik = Topik(
                    id=target_topik_id,
                    mata_pelajaran_id=mapel_id,
                    nama=t_item.nama,
                    difficulty_index=t_item.difficulty_index
                )
                db.add(baru_topik)
                db.flush() # Agar ID tersimpan sementara untuk proses prasyarat
            else:
                # B. Jika topik lama, update datanya
                t_db = db.query(Topik).filter(Topik.id == target_topik_id).first()
                if t_db:
                    t_db.nama = t_item.nama
                    t_db.difficulty_index = t_item.difficulty_index

            # C. PROSES PRASYARAT (Menggunakan fungsi dari topik_service)
            if t_item.prasyarat_ids:
                for p_id in t_item.prasyarat_ids:
                    # Memanggil fungsi existing agar validasi DFS tetap jalan
                    try:
                        tambah_prasyarat(db, target_topik_id, p_id)
                    except HTTPException:
                        # Abaikan jika prasyarat sudah ada atau terjadi siklus
                        # agar proses update lainnya tidak berhenti total
                        continue

    db.commit()
    db.refresh(mapel)
    return MataPelajaranResponse.model_validate(mapel)
 
def delete_mata_pelajaran(db: Session, mapel_id: str) -> dict:
    """Hapus permanen mata pelajaran berdasarkan ID."""
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id).first()
    if not mapel:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")
 
    db.delete(mapel)
    db.commit()
    return {"message": f"Mata pelajaran '{mapel.nama_mata_pelajaran}' berhasil dihapus"}