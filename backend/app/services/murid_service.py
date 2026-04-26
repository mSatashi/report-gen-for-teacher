import uuid
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Murid, KelasMurid
# Tambahkan MuridUpdate pada import di bawah ini
from app.schemas.schemas import MuridCreate, MuridUpdate, MuridResponse

def create_murid(db: Session, data: MuridCreate) -> MuridResponse: 
    # cek duplikat langsung di Murid
    if db.query(Murid).filter(Murid.email_address == data.email_address).first():
        raise HTTPException(400, "Email sudah terdaftar")

    new_id = str(uuid.uuid4())

    murid = Murid(
        id=new_id,
        email_address=data.email_address,
        nama=data.nama,
        education_level=data.education_level,
        jenis_kelamin=data.jenis_kelamin,
        is_active=data.is_active,
    )
    db.add(murid)
    db.commit()

    return MuridResponse(
        id=murid.id,
        email_address=murid.email_address,
        nama=murid.nama,
        education_level=murid.education_level,
        jenis_kelamin=murid.jenis_kelamin,
        is_active=murid.is_active,
    )

def get_all_murid(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> List[MuridResponse]:
    query = db.query(Murid).filter(Murid.is_active == True)
 
    if search:
        query = query.filter(Murid.nama.ilike(f"%{search}%"))
 
    rows = query.offset(skip).limit(limit).all()
 
    result =[]
    for murid in rows:
        result.append(
            MuridResponse(
                id=murid.id,
                email_address=murid.email_address,
                nama=murid.nama,
                education_level=murid.education_level,
                jenis_kelamin=murid.jenis_kelamin,
                is_active=murid.is_active,
            )
        )
    return result
 
def get_murid_by_id(db: Session, murid_id: str) -> MuridResponse:
    """Ambil data 1 siswa berdasarkan ID."""
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
 
    if not murid or not murid.is_active:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
 
    return MuridResponse(
        id=murid.id,
        email_address=murid.email_address,
        nama=murid.nama,
        education_level=murid.education_level,
        jenis_kelamin=murid.jenis_kelamin,
        is_active=murid.is_active,
    )

# --- FUNGSI BARU UNTUK HANDLE UPDATE (PUT) ---
def update_murid(db: Session, murid_id: str, data: MuridUpdate) -> MuridResponse:
    """Perbarui sebagian atau seluruh data siswa."""
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
    
    if not murid or not murid.is_active:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
    
    # Ambil dictionary dari data Pydantic yang hanya dikirim oleh user (menghindari overwrite nilai menjadi None)
    # Jika menggunakan Pydantic V2 gunakan data.model_dump(exclude_unset=True)
    # Jika menggunakan Pydantic V1 gunakan data.dict(exclude_unset=True)
    update_data = data.dict(exclude_unset=True) 

    # Validasi opsional: Jika email diupdate, pastikan tidak bentrok dengan user lain
    if "email_address" in update_data and update_data["email_address"] != murid.email_address:
        email_exist = db.query(Murid).filter(Murid.email_address == update_data["email_address"]).first()
        if email_exist:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar oleh siswa lain")

    # Update atribut object murid dengan data baru
    for key, value in update_data.items():
        setattr(murid, key, value)
    
    db.commit()
    db.refresh(murid)
    
    return MuridResponse(
        id=murid.id,
        email_address=murid.email_address,
        nama=murid.nama,
        education_level=murid.education_level,
        jenis_kelamin=murid.jenis_kelamin,
        is_active=murid.is_active,
    )
# ---------------------------------------------

def delete_murid(db: Session, murid_id: str) -> dict:
    """
    Hapus permanen data siswa dari database.
 
    Jika ingin soft-delete saja (tidak hapus permanen), ganti dengan:
        murid.is_active = False
        db.commit()
    """
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
    if not murid:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
 
    # Hapus dari kelas dulu (opsional, CASCADE sudah handle ini jika diset di DB)
    db.query(KelasMurid).filter(KelasMurid.murid_id == murid_id).delete(synchronize_session="fetch")
    db.flush()

    # Hapus murid — Murid terhapus otomatis via CASCADE
    db.delete(murid)
    db.commit()
 
    return {"message": f"Siswa dengan ID {murid_id} berhasil dihapus"}