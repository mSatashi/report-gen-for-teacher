"""
plan.py — Router untuk Learning Plan / Rencana Studi (F004, F009)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.models import Pengguna
from app.schemas.schemas import RencanaStudiResponse
from app.services.auth_service import require_pengajar
from app.services.plan_service import (
    get_rencana_by_id, get_rencana_by_kelas,
    generate_rencana_studi, get_knowledge_state,
)

router = APIRouter(prefix="/plan", tags=["Learning Plan"])


@router.get("/kelas/{kelas_id}", response_model=List[RencanaStudiResponse])
def list_rencana(
    kelas_id: str,
    murid_id: Optional[str] = Query(None),
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil rencana studi untuk satu kelas. Opsional filter per murid."""
    return get_rencana_by_kelas(db, kelas_id, murid_id)


@router.get("/{plan_id}", response_model=RencanaStudiResponse)
def get_plan(
    plan_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    plan = get_rencana_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rencana studi tidak ditemukan")
    return plan


@router.post("/generate/{kelas_id}", response_model=RencanaStudiResponse, status_code=201)
async def generate_plan(
    kelas_id: str,
    murid_id: Optional[str] = Query(None, description="Kosongkan untuk generate untuk seluruh kelas"),
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """F004 — Generate rencana studi adaptif menggunakan BKT + AI."""
    if not murid_id:
        raise HTTPException(status_code=400, detail="murid_id wajib diisi untuk optimasi PSO.")
        
    try:
        rencana = await generate_rencana_studi(db=db, kelas_id=kelas_id, murid_id=murid_id)
        return rencana
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal generate rencana: {str(e)}")


@router.get("/knowledge-state/{murid_id}")
def knowledge_state(
    murid_id: str,
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil status penguasaan materi siswa dari BKT (nilai 0.0–1.0 per topik)."""
    ks = get_knowledge_state(db, murid_id)
    return {"murid_id": murid_id, "knowledge_state": ks}
