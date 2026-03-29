"""
laporan.py — Router untuk Laporan Perkembangan (F003, F005, F006, F007)
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Pengguna, Murid
from app.schemas.schemas import (
    LaporanCreate, LaporanUpdate, LaporanResponse, KirimLaporanRequest
)
from app.services.auth_service import require_pengajar, get_current_user
from app.services.report_service import (
    generate_laporan, get_laporan_by_id, get_laporan_by_murid,
    get_laporan_pending, update_laporan, finalize_laporan,
    generate_pdf, kirim_laporan_email,
)

router = APIRouter(prefix="/laporan", tags=["Laporan"])


# ── GET ───────────────────────────────────────────────────────────────────────

@router.get("/pending", response_model=List[LaporanResponse])
def laporan_pending(
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil laporan yang belum dikirim untuk semua kelas pengajar ini."""
    return get_laporan_pending(db, current_user.id)


@router.get("/murid/{murid_id}", response_model=List[LaporanResponse])
def laporan_murid(
    murid_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current_user: Pengguna = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    F007 — Lihat laporan perkembangan seorang murid.
    Bisa diakses oleh pengajar, murid itu sendiri, atau orang tua.
    """
    return get_laporan_by_murid(db, murid_id, skip, limit)


@router.get("/{laporan_id}", response_model=LaporanResponse)
def get_laporan(
    laporan_id: str,
    current_user: Pengguna = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lap = get_laporan_by_id(db, laporan_id)
    if not lap:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return lap


@router.get("/{laporan_id}/pdf")
def download_pdf(
    laporan_id: str,
    current_user: Pengguna = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download laporan dalam format PDF."""
    lap = get_laporan_by_id(db, laporan_id)
    if not lap:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")

    # Generate PDF jika belum ada
    if not lap.pdf_path:
        pdf_path = generate_pdf(lap)
        if not pdf_path:
            raise HTTPException(status_code=500, detail="Gagal generate PDF")
        lap.pdf_path = pdf_path
        db.commit()
    else:
        import os
        if not os.path.exists(lap.pdf_path):
            lap.pdf_path = generate_pdf(lap)
            db.commit()

    return FileResponse(
        path=lap.pdf_path,
        media_type="application/pdf",
        filename=f"laporan_{laporan_id}.pdf",
    )


# ── POST ──────────────────────────────────────────────────────────────────────

@router.post("/generate", response_model=LaporanResponse, status_code=201)
async def buat_laporan(
    data: LaporanCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """F003 — Generate laporan perkembangan otomatis via AI."""
    try:
        laporan = await generate_laporan(db, data)
        return laporan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate laporan: {str(e)}")


# ── PUT ───────────────────────────────────────────────────────────────────────

@router.put("/{laporan_id}", response_model=LaporanResponse)
def edit_laporan(
    laporan_id: str,
    data: LaporanUpdate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """F005 — Edit / override narasi laporan yang sudah di-generate."""
    lap = update_laporan(db, laporan_id, data)
    if not lap:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return lap


@router.put("/{laporan_id}/finalisasi", response_model=LaporanResponse)
def finalisasi(
    laporan_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Set status laporan menjadi 'final' — siap dikirim."""
    lap = finalize_laporan(db, laporan_id)
    if not lap:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return lap


# ── POST /kirim ───────────────────────────────────────────────────────────────

@router.post("/{laporan_id}/kirim")
async def kirim_laporan(
    laporan_id: str,
    req: KirimLaporanRequest,
    background_tasks: BackgroundTasks,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """
    F006 — Kirim laporan ke orang tua via email.
    PDF di-generate di background task supaya response cepat.
    """
    lap = get_laporan_by_id(db, laporan_id)
    if not lap:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    if lap.status == "draft":
        raise HTTPException(status_code=400, detail="Laporan harus difinalisasi dahulu sebelum dikirim")

    murid = db.query(Murid).filter(Murid.id == lap.murid_id).first()
    nama_murid = murid.nama if murid else "Siswa"

    # Generate PDF
    pdf_path = generate_pdf(lap)

    # Kirim email di background agar tidak blok response
    background_tasks.add_task(
        kirim_laporan_email,
        laporan=lap,
        email_tujuan=req.email_tujuan,
        nama_murid=nama_murid,
        catatan=req.catatan_tambahan,
        pdf_path=pdf_path,
        db=db,
    )

    return {
        "message": f"Laporan sedang dikirim ke {req.email_tujuan}",
        "laporan_id": laporan_id,
    }
