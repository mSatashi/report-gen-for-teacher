import uuid
from typing import List, Optional
 
from fastapi import HTTPException
from sqlalchemy.orm import Session
 
from app.models.models import MataPelajaran
from app.schemas.schemas import (
    MataPelajaranCreate,
    MataPelajaranUpdate,
    MataPelajaranResponse,
)
 
 
def create_mata_pelajaran(
    db: Session, data: MataPelajaranCreate
) -> MataPelajaranResponse:
    """
    Buat mata pelajaran baru.
    Tolak jika kombinasi nama + hari + jam sudah ada (duplikat jadwal).
    """
    existing = (
        db.query(MataPelajaran)
        .filter(
            MataPelajaran.nama_mata_pelajaran == data.nama_mata_pelajaran,
            MataPelajaran.hari               == data.hari,
            MataPelajaran.jam                == data.jam,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Mata pelajaran '{data.nama_mata_pelajaran}' dengan jadwal "
                f"{data.hari} {data.jam} sudah ada"
            ),
        )
 
    mapel = MataPelajaran(
        id=str(uuid.uuid4()),
        nama_mata_pelajaran=data.nama_mata_pelajaran,
        kredit=data.kredit,
        hari=data.hari,
        jam=data.jam,
    )
    db.add(mapel)
    db.commit()
    db.refresh(mapel)
    return MataPelajaranResponse.model_validate(mapel)
 
 
def get_all_mata_pelajaran(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    hari: Optional[str] = None,
) -> List[MataPelajaranResponse]:
    """
    List semua mata pelajaran.
    - search : filter nama (case-insensitive, opsional)
    - hari   : filter hari jadwal, contoh 'Senin' (opsional)
    - skip / limit : paginasi
    """
    query = db.query(MataPelajaran)
 
    if search:
        query = query.filter(
            MataPelajaran.nama_mata_pelajaran.ilike(f"%{search}%")
        )
    if hari:
        query = query.filter(MataPelajaran.hari == hari)
 
    rows = (
        query
        .order_by(MataPelajaran.hari, MataPelajaran.jam)
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
 
 
def update_mata_pelajaran(
    db: Session, mapel_id: str, data: MataPelajaranUpdate
) -> MataPelajaranResponse:
    """
    Update mata pelajaran (partial update — hanya field yang dikirim).
    Jika nama/hari/jam diubah, cek tidak bentrok dengan jadwal yang sudah ada.
    """
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id).first()
    if not mapel:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")
 
    update_data = data.model_dump(exclude_none=True)
 
    # Cek konflik jadwal jika salah satu dari nama/hari/jam diubah
    if any(k in update_data for k in ("nama_mata_pelajaran", "hari", "jam")):
        nama_cek = update_data.get("nama_mata_pelajaran", mapel.nama_mata_pelajaran)
        hari_cek = update_data.get("hari", mapel.hari)
        jam_cek  = update_data.get("jam",  mapel.jam)
 
        konflik = (
            db.query(MataPelajaran)
            .filter(
                MataPelajaran.nama_mata_pelajaran == nama_cek,
                MataPelajaran.hari               == hari_cek,
                MataPelajaran.jam                == jam_cek,
                MataPelajaran.id                 != mapel_id,
            )
            .first()
        )
        if konflik:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Mata pelajaran '{nama_cek}' dengan jadwal "
                    f"{hari_cek} {jam_cek} sudah ada"
                ),
            )
 
    for field, val in update_data.items():
        setattr(mapel, field, val)
 
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