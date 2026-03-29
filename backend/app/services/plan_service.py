"""
plan_service.py
Service layer untuk Rencana Studi Adaptif.
Mengintegrasikan: BKT (Bayesian Knowledge Tracing) + PlannerEngine LLM.
F004 — Generate rencana studi adaptif.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import (
    DraftAnalisis, KnowledgeState, LogPertemuan, RencanaStudi, Kelas, Murid,
)
from app.ai.ai_service import narrative_engine, planner_engine

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# BKT — Bayesian Knowledge Tracing
# ═══════════════════════════════════════════════════════════════════════════════

class BKTModule:
    """
    Implementasi Bayesian Knowledge Tracing (BKT).
    Parameter default sesuai Section 4.3.2 laporan.

    P(Ln) = P(Ln-1 | corr/incorr) — probabilitas penguasaan setelah observasi.
    """

    def __init__(
        self,
        p_learn: float = 0.2,    # P(T) — probabilitas belajar per sesi
        p_guess: float = 0.1,    # P(G) — probabilitas jawab benar meski tidak tahu
        p_slip:  float = 0.05,   # P(S) — probabilitas jawab salah meski tahu
    ):
        self.p_learn = p_learn
        self.p_guess = p_guess
        self.p_slip  = p_slip

    def update(self, p_knowledge: float, correct: bool) -> float:
        """
        Update probabilitas penguasaan berdasarkan observasi baru.

        Args:
            p_knowledge : P(L_n-1) — penguasaan sebelum observasi ini
            correct     : True jika siswa menjawab/performa baik, False jika tidak

        Returns:
            P(L_n) — probabilitas penguasaan yang telah diperbarui
        """
        if correct:
            # P(L_n | obs=1)
            numerator   = p_knowledge * (1 - self.p_slip)
            denominator = numerator + (1 - p_knowledge) * self.p_guess
        else:
            # P(L_n | obs=0)
            numerator   = p_knowledge * self.p_slip
            denominator = numerator + (1 - p_knowledge) * (1 - self.p_guess)

        p_given_obs = numerator / (denominator + 1e-10)

        # Update knowledge state
        p_next = p_given_obs + (1 - p_given_obs) * self.p_learn
        return float(np.clip(p_next, 0.0, 1.0))

    def compute_from_score(self, p_knowledge: float, score: float) -> float:
        """
        Konversi nilai numerik (0–100) ke observasi BKT dan update.
        Anggap correct jika skor >= 60.
        """
        correct = score >= 60.0
        return self.update(p_knowledge, correct)

    def batch_update(
        self,
        initial_knowledge: float,
        scores: List[float],
    ) -> float:
        """Update BKT dari list skor historis."""
        p = initial_knowledge
        for score in scores:
            p = self.compute_from_score(p, score)
        return p


bkt = BKTModule(p_learn=0.2, p_guess=0.1, p_slip=0.05)


def update_knowledge_states(db: Session, murid_id: str, kelas_id: Optional[str] = None):
    """
    Hitung ulang semua knowledge state untuk satu murid
    berdasarkan semua log pertemuan yang ada.
    Dipanggil setiap kali log baru ditambahkan.
    """
    q = db.query(LogPertemuan).filter(
        LogPertemuan.murid_id == murid_id,
        LogPertemuan.nilai.isnot(None),
    )
    if kelas_id:
        q = q.filter(LogPertemuan.kelas_id == kelas_id)

    logs = q.order_by(LogPertemuan.tanggal.asc()).all()

    # Kelompokkan per topik
    topik_scores: Dict[str, List[float]] = {}
    for log in logs:
        topik = log.topik.strip()
        if topik not in topik_scores:
            topik_scores[topik] = []
        topik_scores[topik].append(float(log.nilai))

    # Ambil diagnostic_score sebagai P(L0) jika ada
    from app.models.models import DiagnosticResult
    diag_rows = db.query(DiagnosticResult).filter(
        DiagnosticResult.murid_id == murid_id
    ).all()
    diag_map = {d.topik: d.diagnostic_score / 100.0 for d in diag_rows}

    for topik, scores in topik_scores.items():
        p0 = diag_map.get(topik, 0.1)   # default P(L0) = 0.1 jika tidak ada diagnostik
        p_final = bkt.batch_update(p0, scores)

        # Upsert ke knowledge_state
        ks = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid_id,
            KnowledgeState.topik == topik,
        ).first()

        if ks:
            ks.p_knowledge = p_final
            ks.updated_at  = datetime.utcnow()
        else:
            ks = KnowledgeState(
                id=str(uuid.uuid4()),
                murid_id=murid_id,
                topik=topik,
                p_knowledge=p_final,
                p_learn=bkt.p_learn,
                p_guess=bkt.p_guess,
                p_slip=bkt.p_slip,
            )
            db.add(ks)

    db.commit()


def get_knowledge_state(db: Session, murid_id: str) -> Dict[str, float]:
    """Ambil semua knowledge state untuk satu murid."""
    rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == murid_id).all()
    return {ks.topik: float(ks.p_knowledge) for ks in rows}


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN SERVICE
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


async def generate_rencana_studi(
    db: Session,
    kelas_id: str,
    murid_id: Optional[str] = None,
) -> RencanaStudi:
    """
    F004 — Generate rencana studi adaptif.
    Alur:
    1. Analisis data log → DraftAnalisis (NarrativeEngine)
    2. Knowledge state dari BKT
    3. Generate rencana → PlannerEngine LLM
    4. Simpan RencanaStudi ke DB
    """
    # 1. Ambil data kelas & log
    kelas = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not kelas:
        raise ValueError(f"Kelas {kelas_id} tidak ditemukan")

    q = db.query(LogPertemuan).filter(LogPertemuan.kelas_id == kelas_id)
    if murid_id:
        q = q.filter(LogPertemuan.murid_id == murid_id)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()

    log_data = [
        {
            "tanggal": str(l.tanggal),
            "topik":   l.topik,
            "nilai":   float(l.nilai) if l.nilai else None,
            "catatan": l.catatan,
        }
        for l in logs
    ]

    # 2. Analisis log → draft analisis
    draft_text = await narrative_engine.analyze_class_data(
        nama_kelas=kelas.nama,
        log_data=log_data,
    )

    draft = DraftAnalisis(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        konten=draft_text,
    )
    db.add(draft)
    db.flush()

    # 3. Knowledge state (BKT)
    if murid_id:
        update_knowledge_states(db, murid_id, kelas_id)
        knowledge_state = get_knowledge_state(db, murid_id)
    else:
        knowledge_state = {}

    # 4. Sisa kredit / sesi
    sisa_sesi = max(1, (kelas.kredit or 20) - len(logs))

    # 5. Nama murid
    nama_murid = "Seluruh Kelas"
    if murid_id:
        murid = db.query(Murid).filter(Murid.id == murid_id).first()
        if murid:
            nama_murid = murid.nama or murid.pengguna.username

    # 6. Generate rencana via PlannerEngine
    rencana_data = await planner_engine.generate_rencana_studi(
        nama_murid=nama_murid,
        mata_pelajaran=kelas.mata_pelajaran or kelas.nama,
        draft_analisis=draft_text,
        knowledge_state=knowledge_state,
        sisa_sesi=sisa_sesi,
    )

    # 7. Simpan ke DB
    versi = db.query(RencanaStudi).filter(
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.murid_id == murid_id,
    ).count() + 1

    estimasi_selesai_minggu = rencana_data.get("estimasi_selesai_minggu", 4)
    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        draft_analisis_id=draft.id,
        daftar_rekomendasi_materi=rencana_data.get("rekomendasi_materi", []),
        jadwal_mingguan=rencana_data.get("jadwal_mingguan", {}),
        catatan_analisa=rencana_data.get("catatan_analisa", draft_text),
        estimasi_waktu_selesai=datetime.utcnow() + timedelta(weeks=estimasi_selesai_minggu),
        version=versi,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana
