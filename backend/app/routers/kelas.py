"""
kelas.py — Router untuk manajemen Kelas dan Murid
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Pengguna, Kelas, KelasMurid, Murid, MataPelajaran
from app.schemas.schemas import (
    KelasCreate, KelasUpdate, KelasResponse,
    MuridResponse, TambahMuridKeKelas,
    MuridCreate, MuridUpdate
)
from app.services.auth_service import require_pengajar

router = APIRouter(prefix="/kelas", tags=["Kelas & Murid"])


def _murid_to_response(murid: Murid) -> MuridResponse:
    return MuridResponse(
        id=murid.id,
        email_address=murid.email_address,
        nama=murid.nama,
        education_level=murid.education_level,
        jenis_kelamin=murid.jenis_kelamin,
        is_active=murid.is_active,
    )


def _cek_mata_pelajaran(db: Session, mata_pelajaran_id: str) -> MataPelajaran:
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mata_pelajaran_id).first()
    if not mapel:
        raise HTTPException(
            status_code=404,
            detail=f"Mata pelajaran dengan id '{mata_pelajaran_id}' tidak ditemukan",
        )
    return mapel

# ── Kelas CRUD ────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[KelasResponse], status_code=status.HTTP_200_OK)
def list_kelas(
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    return db.query(Kelas).filter(Kelas.pengajar_id == current_user.id).all()


@router.get("/{kelas_id}", response_model=KelasResponse, status_code=status.HTTP_200_OK)
def get_kelas(
    kelas_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    k = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    return k


@router.post("/", response_model=KelasResponse, status_code=status.HTTP_201_CREATED)
def buat_kelas(
    data: KelasCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    _cek_mata_pelajaran(db, data.mata_pelajaran_id)

    if db.query(Kelas).filter(Kelas.nama == data.nama).first():
        raise HTTPException(
            status_code=400,
            detail=f"Kelas dengan nama '{data.nama}' sudah ada",
        )

    kelas = Kelas(
        id=str(uuid.uuid4()),
        nama=data.nama,
        mata_pelajaran_id=data.mata_pelajaran_id,
        pengajar_id=current_user.id,
        hari=data.hari,
        jam=data.jam,
        kredit=getattr(data, 'kredit', 20) 
    )
    db.add(kelas)
    db.commit()
    db.refresh(kelas)
    return kelas


@router.put("/{kelas_id}", response_model=KelasResponse, status_code=status.HTTP_200_OK)
def update_kelas(
    kelas_id: str,
    data: KelasUpdate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    k = db.query(Kelas).filter(
        Kelas.id == kelas_id, Kelas.pengajar_id == current_user.id
    ).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    update_data = data.model_dump(exclude_none=True)

    if "mata_pelajaran_id" in update_data:
        _cek_mata_pelajaran(db, update_data["mata_pelajaran_id"])

    if "nama" in update_data and update_data["nama"] != k.nama:
        if db.query(Kelas).filter(Kelas.nama == update_data["nama"]).first():
            raise HTTPException(
                status_code=400,
                detail=f"Kelas dengan nama '{update_data['nama']}' sudah ada",
            )

    for field, val in update_data.items():
        setattr(k, field, val)

    db.commit()
    db.refresh(k)
    return k


@router.delete("/{kelas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_kelas(
    kelas_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    k = db.query(Kelas).filter(
        Kelas.id == kelas_id, Kelas.pengajar_id == current_user.id
    ).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    db.delete(k)
    db.commit()
    return {"message": "Kelas ini sudah dihapus oleh sistem"}


# ── Murid di dalam Kelas (Relasional) ─────────────────────────────────────────

@router.get("/{kelas_id}/murid", response_model=List[MuridResponse], status_code=status.HTTP_200_OK)
def list_murid_kelas(
    kelas_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    km_rows = db.query(KelasMurid).filter(KelasMurid.kelas_id == kelas_id).all()
    result =[]
    for km in km_rows:
        murid = db.query(Murid).filter(Murid.id == km.murid_id).first()
        if murid:
            result.append(_murid_to_response(murid))
    return result


@router.post("/{kelas_id}/murid", status_code=status.HTTP_201_CREATED)
def tambah_murid_ke_kelas(
    kelas_id: str,
    data: TambahMuridKeKelas,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    if not db.query(Kelas).filter(Kelas.id == kelas_id).first():
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    
    if not db.query(Murid).filter(Murid.id == data.murid_id).first():
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    existing = db.query(KelasMurid).filter(
        KelasMurid.kelas_id == kelas_id,
        KelasMurid.murid_id == data.murid_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Murid sudah ada di kelas ini")

    db.add(KelasMurid(kelas_id=kelas_id, murid_id=data.murid_id))
    db.commit()
    return {"message": "Murid berhasil ditambahkan ke kelas"}


@router.delete("/{kelas_id}/murid/{murid_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_murid_dari_kelas(
    kelas_id: str,
    murid_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    km = db.query(KelasMurid).filter(
        KelasMurid.kelas_id == kelas_id,
        KelasMurid.murid_id == murid_id,
    ).first()
    if not km:
        raise HTTPException(status_code=404, detail="Murid tidak ada di kelas ini")
    db.delete(km)
    db.commit()
    return {"message": "Siswa sudah dihapus dari kelas ini"}


# ── CRUD Murid (standalone) ───────────────────────────────────────────────────

@router.post("/murid/tambah", response_model=MuridResponse, status_code=status.HTTP_201_CREATED)
def tambah_murid_baru(
    data: MuridCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    if db.query(Murid).filter(Murid.email_address == data.email_address).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    uid = str(uuid.uuid4())
    murid = Murid(
        id=uid,
        email_address=data.email_address,
        nama=data.nama,
        education_level=data.education_level,
        jenis_kelamin=data.jenis_kelamin,
        is_active=data.is_active,
    )
    db.add(murid)
    db.commit()
    db.refresh(murid)

    return MuridResponse(
        id=uid,
        email_address= data.email_address,
        nama= data.nama,
        education_level= data.education_level,
        jenis_kelamin=data.jenis_kelamin,
        is_active=data.is_active,
    )


@router.put("/murid/{murid_id}", response_model=MuridResponse)
def update_murid(
    murid_id: str,
    data: MuridUpdate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(murid, field, val)
    db.commit()
    db.refresh(murid)
    return _murid_to_response(murid)