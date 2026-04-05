# =============================================================================
# FIX 3 ► GANTI SELURUH ISI: backend/app/routers/kelas.py
#
# Root cause yang diperbaiki:
#   - list_murid_kelas() mengembalikan list Murid ORM langsung sebagai
#     response_model=List[MuridResponse], tapi Murid tidak punya
#     username/email_address → FastAPI gagal validasi response.
#   - Semua endpoint yang return Murid ORM sekarang diubah untuk
#     mengambil data Pengguna secara eksplisit dan membangun MuridResponse
#     secara manual (sama seperti pola di murid_service.py yang baru).
# =============================================================================

"""
kelas.py — Router untuk manajemen Kelas dan Murid
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Pengguna, Kelas, KelasMurid, Murid
from app.schemas.schemas import (
    KelasCreate, KelasUpdate, KelasResponse,
    MuridCreate, MuridUpdate, MuridResponse, TambahMuridKeKelas,
)
from app.services.auth_service import require_pengajar
from app.core.security import hash_password

router = APIRouter(prefix="/kelas", tags=["Kelas & Murid"])


def _murid_to_response(murid: Murid, db: Session) -> MuridResponse:
    """Helper: bangun MuridResponse dari ORM Murid + join ke Pengguna."""
    pengguna = db.query(Pengguna).filter(Pengguna.id == murid.id).first()
    return MuridResponse(
        id=murid.id,
        username=pengguna.username if pengguna else None,
        email_address=pengguna.email_address if pengguna else None,
        nama=murid.nama,
        usia=murid.usia,
        level=murid.level,
        credit_total=murid.credit_total or 0,
        credit_used=murid.credit_used or 0,
    )


# ── Kelas CRUD ────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[KelasResponse])
def list_kelas(
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil semua kelas milik pengajar yang login."""
    return db.query(Kelas).filter(Kelas.pengajar_id == current_user.id).all()


@router.get("/{kelas_id}", response_model=KelasResponse)
def get_kelas(
    kelas_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    k = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    return k


@router.post("/", response_model=KelasResponse, status_code=201)
def buat_kelas(
    data: KelasCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Buat kelas baru untuk pengajar yang login."""
    kelas = Kelas(id=str(uuid.uuid4()), pengajar_id=current_user.id, **data.model_dump())
    db.add(kelas)
    db.commit()
    db.refresh(kelas)
    return kelas


@router.put("/{kelas_id}", response_model=KelasResponse)
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
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(k, field, val)
    db.commit()
    db.refresh(k)
    return k


@router.delete("/{kelas_id}", status_code=204)
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


# ── Murid di dalam Kelas ──────────────────────────────────────────────────────

@router.get("/{kelas_id}/murid", response_model=List[MuridResponse])
def list_murid_kelas(
    kelas_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil daftar murid dalam satu kelas."""
    km_rows = db.query(KelasMurid).filter(KelasMurid.kelas_id == kelas_id).all()
    result = []
    for km in km_rows:
        murid = db.query(Murid).filter(Murid.id == km.murid_id).first()
        if murid:
            result.append(_murid_to_response(murid, db))
    return result


@router.post("/{kelas_id}/murid", status_code=201)
def tambah_murid_ke_kelas(
    kelas_id: str,
    data: TambahMuridKeKelas,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Tambahkan murid yang sudah ada ke dalam kelas."""
    existing = db.query(KelasMurid).filter(
        KelasMurid.kelas_id == kelas_id,
        KelasMurid.murid_id == data.murid_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Murid sudah ada di kelas ini")
    db.add(KelasMurid(kelas_id=kelas_id, murid_id=data.murid_id))
    db.commit()
    return {"message": "Murid berhasil ditambahkan ke kelas"}


@router.delete("/{kelas_id}/murid/{murid_id}", status_code=204)
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


# ── CRUD Murid (standalone) ───────────────────────────────────────────────────

@router.post("/murid/tambah", response_model=MuridResponse, status_code=201)
def tambah_murid_baru(
    data: MuridCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Buat akun murid baru sekaligus profilnya."""
    if db.query(Pengguna).filter(Pengguna.email_address == data.email_address).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if db.query(Pengguna).filter(Pengguna.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")

    uid = str(uuid.uuid4())
    pengguna = Pengguna(
        id=uid,
        username=data.username,
        email_address=data.email_address,
        hashed_password=hash_password(data.password),
        tipe_pengguna="murid",
        is_active=True,
    )
    murid = Murid(
        id=uid,
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
        id=uid,
        username=pengguna.username,
        email_address=pengguna.email_address,
        nama=murid.nama,
        usia=murid.usia,
        level=murid.level,
        credit_total=murid.credit_total or 0,
        credit_used=murid.credit_used or 0,
    )


@router.put("/murid/{murid_id}", response_model=MuridResponse)
def update_murid(
    murid_id: str,
    data: MuridUpdate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Update profil murid."""
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(murid, field, val)
    db.commit()
    db.refresh(murid)
    return _murid_to_response(murid, db)
