"""
diagnostic.py — Router untuk Tes Diagnostik Awal (F008) - CRUD LENGKAP
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Pengguna, DiagnosticResult, KnowledgeState
from app.schemas.schemas import DiagnosticCreate, DiagnosticUpdate, DiagnosticResponse
from app.services.auth_service import require_pengajar

router = APIRouter(prefix="/diagnostic", tags=["Diagnostik"])

# 1. CREATE
@router.post("/", response_model=DiagnosticResponse, status_code=201)
def simpan_diagnostic(
    data: DiagnosticCreate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """
    F008 — Simpan hasil tes diagnostik awal.
    Nilai ini dipakai sebagai P(L0) pada BKT.
    """
    diag = DiagnosticResult(
        id=str(uuid.uuid4()),
        murid_id=data.murid_id,
        kelas_id=data.kelas_id,
        topik=data.topik,
        skor=data.diagnostic_score,
        diagnostic_score=data.diagnostic_score,
    )
    db.add(diag)

    # Inisialisasi/Update knowledge state dengan P(L0)
    p_l0 = data.diagnostic_score / 100.0
    existing_ks = db.query(KnowledgeState).filter(
        KnowledgeState.murid_id == data.murid_id,
        KnowledgeState.topik == data.topik,
    ).first()
    
    if existing_ks:
        existing_ks.p_knowledge = p_l0
    else:
        db.add(KnowledgeState(
            id=str(uuid.uuid4()),
            murid_id=data.murid_id,
            topik=data.topik,
            p_knowledge=p_l0,
        ))

    db.commit()
    db.refresh(diag)
    return diag

# 2. READ (ALL BY MURID)
@router.get("/murid/{murid_id}", response_model=List[DiagnosticResponse])
def get_diagnostics_murid(
    murid_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil semua hasil tes diagnostik untuk satu murid."""
    return db.query(DiagnosticResult).filter(
        DiagnosticResult.murid_id == murid_id
    ).order_by(DiagnosticResult.created_at.desc()).all()

# 3. UPDATE
@router.put("/{diag_id}", response_model=DiagnosticResponse)
def update_diagnostic(
    diag_id: str,
    data: DiagnosticUpdate,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Update nilai diagnostik jika ada salah input skor atau topik."""
    diag = db.query(DiagnosticResult).filter(DiagnosticResult.id == diag_id).first()
    if not diag:
        raise HTTPException(status_code=404, detail="Data diagnostik tidak ditemukan")

    # Simpan topik lama untuk update KnowledgeState nanti jika topik ikut diubah
    topik_lama = diag.topik
    murid_id = diag.murid_id

    # Update data diagnostik
    update_data = data.model_dump(exclude_unset=True)
    if "diagnostic_score" in update_data:
        diag.skor = update_data["diagnostic_score"] # update kolom skor (numeric)
    
    for key, value in update_data.items():
        setattr(diag, key, value)

    # Sinkronisasi ke KnowledgeState
    # Jika skor berubah, P(L0) di KnowledgeState harus ikut berubah
    p_l0 = diag.diagnostic_score / 100.0
    ks = db.query(KnowledgeState).filter(
        KnowledgeState.murid_id == murid_id,
        KnowledgeState.topik == diag.topik
    ).first()

    if ks:
        ks.p_knowledge = p_l0

    db.commit()
    db.refresh(diag)
    return diag

# 4. DELETE
@router.delete("/{diag_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_diagnostic(
    diag_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Hapus data diagnostik."""
    diag = db.query(DiagnosticResult).filter(DiagnosticResult.id == diag_id).first()
    if not diag:
        raise HTTPException(status_code=404, detail="Data diagnostik tidak ditemukan")
    
    db.delete(diag)
    db.commit()
    return None