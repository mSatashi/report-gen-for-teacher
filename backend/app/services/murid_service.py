import uuid
from typing import List, Optional
 
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.models import Murid, Pengguna, KelasMurid
from app.schemas.schemas import MuridCreate, MuridResponse
 
def create_murid(db: Session, data: MuridCreate) -> MuridResponse:
    """
    Buat siswa baru: tulis ke tabel pengguna + murid sekaligus.
    Melempar 400 jika email atau username sudah terdaftar.
    """
    if db.query(Pengguna).filter(Pengguna.email_address == data.email_address).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if db.query(Pengguna).filter(Pengguna.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")

    new_id = str(uuid.uuid4())

    pengguna = Pengguna(
        id=new_id,
        username=data.username,
        email_address=data.email_address,
        hashed_password=hash_password(data.password),
        tipe_pengguna="murid",
        is_active=True,
    )
    murid = Murid(
        id=new_id,
        nama=data.nama,
        usia=data.usia,
        level=data.level,
        credit_total=data.credit_total or 0,
        credit_used=0,
    )

    db.add(pengguna)
    db.add(murid)
    db.commit()
    db.refresh(murid)

    return MuridResponse(
        id=murid.id,
        username=pengguna.username,
        email_address=pengguna.email_address,
        nama=murid.nama,
        usia=murid.usia,
        level=murid.level,
        credit_total=murid.credit_total or 0,
        credit_used=murid.credit_used or 0,
    )

def get_all_murid(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> List[MuridResponse]:
    """
    Ambil semua data siswa (master data).
    - skip & limit : untuk paginasi
    - search       : filter nama siswa (opsional, case-insensitive)
    """
    query = (
        db.query(Murid, Pengguna)
        .join(Pengguna, Pengguna.id == Murid.id)
        .filter(Pengguna.is_active == True)
    )
 
    if search:
        query = query.filter(Murid.nama.ilike(f"%{search}%"))
 
    rows = query.offset(skip).limit(limit).all()
 
    result = []
    for murid, pengguna in rows:
        result.append(
            MuridResponse(
                id=murid.id,
                username=pengguna.username,
                email_address=pengguna.email_address,
                nama=murid.nama,
                usia=murid.usia,
                level=murid.level,
                credit_total=murid.credit_total or 0,
                credit_used=murid.credit_used or 0,
            )
        )
    return result
 
 
def get_murid_by_id(db: Session, murid_id: str) -> MuridResponse:
    """Ambil data 1 siswa berdasarkan ID."""
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
    pengguna = db.query(Pengguna).filter(Pengguna.id == murid_id).first()
 
    if not murid or not pengguna or not pengguna.is_active:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
 
    return MuridResponse(
        id=murid.id,
        username=pengguna.username,
        email_address=pengguna.email_address,
        nama=murid.nama,
        usia=murid.usia,
        level=murid.level,
        credit_total=murid.credit_total or 0,
        credit_used=murid.credit_used or 0,
    )
 
 
def delete_murid(db: Session, murid_id: str) -> dict:
    """
    Hapus permanen data siswa dari database.
    Karena Pengguna → Murid pakai ondelete="CASCADE",
    cukup hapus baris Pengguna dan Murid ikut terhapus otomatis.
 
    Jika ingin soft-delete saja (tidak hapus permanen), ganti dengan:
        pengguna.is_active = False
        db.commit()
    """
    pengguna = db.query(Pengguna).filter(Pengguna.id == murid_id).first()
    if not pengguna or pengguna.tipe_pengguna != "murid":
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
 
    # Hapus dari kelas dulu (opsional, CASCADE sudah handle ini jika diset di DB)
    db.query(KelasMurid).filter(KelasMurid.murid_id == murid_id).delete()
 
    # Hapus pengguna — Murid terhapus otomatis via CASCADE
    db.delete(pengguna)
    db.commit()
 
    return {"message": f"Siswa dengan ID {murid_id} berhasil dihapus"}