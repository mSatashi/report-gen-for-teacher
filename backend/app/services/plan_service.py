import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
 
import numpy as np
from sqlalchemy.orm import Session
 
from app.models.models import (
    DraftAnalisis, KnowledgeState, LogPertemuan,
    RencanaStudi, Kelas, Murid,
)
# [INTEGRASI] Pakai BKTEngine dengan parameter per-skill (dari bkt_engine.py)
from app.ai.bkt_engine import bkt_engine, PRIOR_KNOWLEDGE, CORRECT_THRESHOLD
 
logger = logging.getLogger(__name__)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE STATE — Query & Update dari PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
 
def update_knowledge_states(
    db: Session,
    murid_id: str,
    kelas_id: Optional[str] = None,
) -> None:
    """
    Hitung ulang knowledge_state untuk satu murid berdasarkan LogPertemuan di DB.
 
    [INTEGRASI] Menggunakan bkt_engine.batch_update() (per-skill params)
    yang logika Bayes-nya identik dengan update_bkt() di 02_bkt_tuning.py.
 
    Dipanggil setiap kali log baru ditambahkan (dari routers/log.py).
    Data disimpan ke tabel knowledge_state di PostgreSQL.
    """
    # 1. Ambil semua log dengan nilai (dari PostgreSQL, bukan CSV)
    q = db.query(LogPertemuan).filter(
        LogPertemuan.murid_id == murid_id,
        LogPertemuan.nilai.isnot(None),
    )
    if kelas_id:
        q = q.filter(LogPertemuan.kelas_id == kelas_id)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()
 
    # 2. Kelompokkan skor per topik (urutan kronologis penting untuk BKT)
    topik_scores: Dict[str, List[float]] = {}
    for log in logs:
        topik = log.topik.strip()
        nilai = float(log.nilai) if log.nilai is not None else 0.0
        topik_scores.setdefault(topik, []).append(float(nilai))
 
    # 3. Ambil P(L0) dari diagnostic_result jika ada
    from app.models.models import DiagnosticResult
    diag_rows = db.query(DiagnosticResult).filter(
        DiagnosticResult.murid_id == murid_id
    ).all()
    diag_map = {d.topik: d.diagnostic_score / 100.0 for d in diag_rows}
 
    # 4. Update per topik menggunakan BKTEngine
    for topik, scores in topik_scores.items():
        p0      = diag_map.get(topik, PRIOR_KNOWLEDGE)   # P(L0) dari diagnostik atau 0.2
        p_final = bkt_engine.batch_update(topik, p0, scores)
 
        # Upsert ke tabel knowledge_state (PostgreSQL)
        ks = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid_id,
            KnowledgeState.topik    == topik,
        ).first()
 
        sp = bkt_engine._get_params(topik, list(topik_scores.keys()))  # ambil params yang dipakai
 
        if ks:
            ks.p_knowledge = p_final
            ks.p_learn     = sp.learn
            ks.p_guess     = sp.guess
            ks.p_slip      = sp.slip
            ks.updated_at  = datetime.utcnow()
        else:
            ks = KnowledgeState(
                id=str(uuid.uuid4()),
                murid_id=murid_id,
                topik=topik,
                p_knowledge=p_final,
                p_learn=sp.learn,
                p_guess=sp.guess,
                p_slip=sp.slip,
            )
            db.add(ks)
 
    db.commit()
    logger.debug(f"Knowledge state diperbarui untuk murid {murid_id}: {len(topik_scores)} topik")
 
 
def get_knowledge_state(db: Session, murid_id: str) -> Dict[str, float]:
    """
    Ambil semua knowledge_state dari PostgreSQL untuk satu murid.
    Return: {topik: p_knowledge}
    """
    rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == murid_id).all()
    return {ks.topik: float(ks.p_knowledge) for ks in rows}
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# PLAN CRUD
# ═══════════════════════════════════════════════════════════════════════════════
 
def get_rencana_by_id(db: Session, plan_id: str) -> Optional[RencanaStudi]:
    return db.query(RencanaStudi).filter(RencanaStudi.id == plan_id).first()
 
 
def get_rencana_by_kelas(
    db: Session,
    kelas_id: str,
    murid_id: Optional[str] = None,
) -> List[RencanaStudi]:
    q = db.query(RencanaStudi).filter(RencanaStudi.kelas_id == kelas_id)
    if murid_id:
        q = q.filter(RencanaStudi.murid_id == murid_id)
    return q.order_by(RencanaStudi.waktu.desc()).all()
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE RENCANA STUDI (F004)
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_rencana_studi(
    db: Session,
    kelas_id: str,
    murid_id: Optional[str] = None,
) -> RencanaStudi:
    """
    F004 — Generate rencana studi adaptif tanpa LLM.
    Tetap gunakan BKTEngine untuk update knowledge_state.
    Isi RencanaStudi: id, kelas_id, daftar_rekomendasi_materi, jadwal_mingguan,
    estimasi_waktu_selesai, version
    """
    # 1. Validasi kelas
    kelas = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not kelas:
        raise ValueError(f"Kelas {kelas_id} tidak ditemukan")

    # 2. Ambil log pertemuan dari PostgreSQL
    q = db.query(LogPertemuan).filter(LogPertemuan.kelas_id == kelas_id)
    if murid_id:
        q = q.filter(LogPertemuan.murid_id == murid_id)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()

    # 3. Update knowledge_state via BKTEngine
    if murid_id:
        update_knowledge_states(db, murid_id, kelas_id)
        knowledge_state = get_knowledge_state(db, murid_id)
    else:
        knowledge_state = {}

    # 4. Buat rekomendasi materi sederhana dari topik yang ada di log
    topik_counts: Dict[str, int] = {}
    for log in logs:
        if log.topik is not None:
            topik_counts[log.topik.strip()] = topik_counts.get(log.topik.strip(), 0) + 1

    daftar_rekomendasi_materi: List[str] = [
        t for t, _ in sorted(topik_counts.items(), key=lambda x: x[1])
    ][:5]  # ambil 5 topik dengan frekuensi terendah

    # 5. Buat jadwal mingguan sederhana
    jadwal_mingguan = {
        "minggu_1": daftar_rekomendasi_materi[:2],
        "minggu_2": daftar_rekomendasi_materi[2:4],
        "minggu_3": daftar_rekomendasi_materi[4:],
    }

    # 6. Estimasi waktu selesai (default 4 minggu)
    estimasi_waktu_selesai = datetime.now() + timedelta(weeks=4)

    # 7. Hitung versi
    versi = db.query(RencanaStudi).filter(
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.murid_id == murid_id,
    ).count() + 1

    # 8. Simpan RencanaStudi ke PostgreSQL
    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        daftar_rekomendasi_materi=daftar_rekomendasi_materi,
        jadwal_mingguan=jadwal_mingguan,
        estimasi_waktu_selesai=estimasi_waktu_selesai,
        version=versi,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana
