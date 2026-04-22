"""
app/routers/bkt.py
═══════════════════════════════════════════════════════════════════════════════
Router untuk inspeksi parameter BKT dan knowledge state.
 
Endpoint:
  GET /api/v1/bkt/params                         → semua parameter per skill
  GET /api/v1/bkt/knowledge-state/{murid_id}     → knowledge state detail murid
  GET /api/v1/bkt/skill-order                    → urutan skill kurikulum
 
Semua endpoint READ-ONLY dan hanya untuk pengajar.
Berguna untuk validasi hasil eksperimen (02_bkt_tuning.py) vs state di DB.
═══════════════════════════════════════════════════════════════════════════════
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
 
from app.core.database import get_db
from app.models.models import Pengguna, KnowledgeState
from app.services.auth_service import require_pengajar
from app.ai.bkt_engine import bkt_engine, SKILL_ORDER, CORRECT_THRESHOLD
 
router = APIRouter(prefix="/bkt", tags=["BKT"])
 
 
@router.get("/params", summary="Parameter BKT per skill")
def get_bkt_params(current_user: Pengguna = Depends(require_pengajar)):
    """
    Lihat parameter BKT (learn/slip/guess/difficulty) untuk setiap skill.
    Berguna untuk memvalidasi apakah params dari bkt_global_params.csv sudah ter-load.
    """
    return {
        "correct_threshold": CORRECT_THRESHOLD,
        "total_skills":      len(SKILL_ORDER),
        "params":            bkt_engine.get_all_params(),
        "keterangan": {
            "learn":      "P(T) — probabilitas belajar dalam satu sesi (0.1–0.3)",
            "slip":       "P(S) — salah meski tahu (0.05–0.1)",
            "guess":      "P(G) — benar meski tidak tahu (0.1–0.2)",
            "difficulty": "0.2=mudah, 1.0=sangat sulit (berdasarkan urutan kurikulum)",
        },
    }
 
 
@router.get("/knowledge-state/{murid_id}", summary="Knowledge state detail seorang murid")
def get_knowledge_state_detail(
    murid_id: str,
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_pengajar),
):
    """
    Knowledge state lengkap dari PostgreSQL untuk satu murid,
    beserta parameter BKT yang dipakai dan status penguasaannya.
    """
    rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == murid_id).all()
    if not rows:
        return {"murid_id": murid_id, "knowledge_states": [], "total_topik": 0}
 
    result = []
    for ks in rows:
        p   = float(ks.p_knowledge)
        pct = round(p * 100, 1)
        status = "Dikuasai" if p >= 0.7 else ("Sedang Dipelajari" if p >= 0.4 else "Perlu Perhatian")
        result.append({
            "topik":       ks.topik,
            "p_knowledge": round(p, 4),
            "persen":      pct,
            "status":      status,
            "p_learn":     round(float(ks.p_learn), 4) if ks.p_learn else None,
            "p_slip":      round(float(ks.p_slip),  4) if ks.p_slip  else None,
            "p_guess":     round(float(ks.p_guess), 4) if ks.p_guess else None,
            "updated_at":  str(ks.updated_at),
        })
 
    result.sort(key=lambda x: x["p_knowledge"])
 
    return {
        "murid_id":         murid_id,
        "total_topik":      len(result),
        "knowledge_states": result,
        "ringkasan": {
            "dikuasai":          sum(1 for r in result if r["status"] == "Dikuasai"),
            "sedang_dipelajari": sum(1 for r in result if r["status"] == "Sedang Dipelajari"),
            "perlu_perhatian":   sum(1 for r in result if r["status"] == "Perlu Perhatian"),
        },
    }
 
 
@router.get("/skill-order", summary="Urutan skill kurikulum")
def get_skill_order(current_user: Pengguna = Depends(require_pengajar)):
    """Urutan skill kurikulum yang dipakai BKT untuk menghitung difficulty."""
    return {
        "total": len(SKILL_ORDER),
        "skills": [
            {
                "urutan":     i + 1,
                "skill":      skill,
                "difficulty": round(0.2 + 0.8 * (i / max(len(SKILL_ORDER) - 1, 1)), 3),
            }
            for i, skill in enumerate(SKILL_ORDER)
        ],
    }