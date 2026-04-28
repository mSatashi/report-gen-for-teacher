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
 
 
from app.services.topik_service import tambah_prasyarat, hapus_prasyarat
from app.models.models import Topik, TopikPrasyarat

def update_mata_pelajaran(db: Session, mapel_id: str, data: MataPelajaranUpdate) -> MataPelajaranResponse:
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id).first()
    if not mapel:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    # 1. Update Identitas Mapel
    if data.nama_mata_pelajaran:
        setattr(mapel, "nama_mata_pelajaran", data.nama_mata_pelajaran)

    if data.topik_list is not None:
        # 2. Ambil data topik yang ada saat ini di DB
        topik_lama_db = db.query(Topik).filter(Topik.mata_pelajaran_id == mapel_id).all()
        # Mapping untuk mempermudah pencarian (ID -> Objek) dan (Nama -> Objek)
        map_id_to_topik: dict[str, Topik] = {str(t.id): t for t in topik_lama_db}
        map_nama_to_topik: dict[str, Topik] = {t.nama.lower(): t for t in topik_lama_db}
        
        id_topik_yang_dipertahankan = set()

        # 3. Proses Sinkronisasi (Update atau Create)
        for t_item in data.topik_list:
            target_topik = None
            
            # Cek berdasarkan ID dulu (jika ada)
            if t_item.id:
                target_topik = map_id_to_topik.get(str(t_item.id))
            # Jika ID tidak ada/null, cek berdasarkan Nama (untuk mencegah duplikasi)
            elif t_item.nama.lower() in map_nama_to_topik:
                target_topik = map_nama_to_topik[t_item.nama.lower()]
            
            if target_topik:
                # Update data yang sudah ada
                target_topik.nama = t_item.nama
                target_topik.difficulty_index = t_item.difficulty_index
                id_topik_yang_dipertahankan.add(target_topik.id)
            else:
                # Benar-benar topik baru
                new_id = str(uuid.uuid4())
                target_topik = Topik(
                    id=new_id,
                    mata_pelajaran_id=mapel_id,
                    nama=t_item.nama,
                    difficulty_index=t_item.difficulty_index
                )
                db.add(target_topik)
                id_topik_yang_dipertahankan.add(new_id)
            
            db.flush() # Penting agar ID baru terdaftar di session untuk relasi prasyarat

        # 4. Hapus Topik yang tidak dikirim lagi oleh Frontend
        for t_old in topik_lama_db:
            if t_old.id not in id_topik_yang_dipertahankan:
                db.delete(t_old)

        db.flush()

        # 5. Proses Prasyarat (setelah semua ID topik stabil/tidak berubah)
        for t_item in data.topik_list:
            # Cari objek topik yang sedang diproses
            current_topik = None
            if t_item.id:
                current_topik = db.query(Topik).filter(Topik.id == t_item.id).first()
            else:
                current_topik = db.query(Topik).filter(
                    Topik.mata_pelajaran_id == mapel_id, 
                    Topik.nama == t_item.nama
                ).first()

            if current_topik and t_item.prasyarat_ids is not None:
                # Bersihkan relasi prasyarat lama agar tidak duplikat
                db.query(TopikPrasyarat).filter(TopikPrasyarat.topik_id == current_topik.id).delete()
                
                for p_id in t_item.prasyarat_ids:
                    try:
                        # Panggil fungsi existing untuk validasi graf
                        tambah_prasyarat(db, current_topik.id, p_id)
                    except Exception:
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