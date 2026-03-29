"""
diagnostic.py — Router untuk Tes Diagnostik Awal (F008)
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Pengguna, DiagnosticResult, KnowledgeState
from app.schemas.schemas import DiagnosticCreate, DiagnosticResponse
from app.services.auth_service import require_pengajar

router = APIRouter(prefix="/diagnostic", tags=["Diagnostik"])


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
    # Simpan diagnostic result
    diag = DiagnosticResult(
        id=str(uuid.uuid4()),
        murid_id=data.murid_id,
        kelas_id=data.kelas_id,
        topik=data.topik,
        skor=data.diagnostic_score,
        diagnostic_score=data.diagnostic_score,
    )
    db.add(diag)

    # Inisialisasi knowledge state dengan P(L0) dari diagnostic
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


@router.get("/murid/{murid_id}", response_model=List[DiagnosticResponse])
def get_diagnostics(
    murid_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil semua hasil tes diagnostik untuk satu murid."""
    return db.query(DiagnosticResult).filter(
        DiagnosticResult.murid_id == murid_id
    ).order_by(DiagnosticResult.created_at.desc()).all()
