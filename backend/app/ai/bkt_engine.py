"""
═══════════════════════════════════════════════════════════════════════════════
BKT Engine — implementasi Bayesian Knowledge Tracing dengan parameter per-skill.
 
Hubungan dengan experiment/:
  - Logika update_bkt() dari 02_bkt_tuning.py di-refactor ke kelas BKTEngine
  - Parameter default mengikuti Tabel 8 laporan (Section 4.3.2):
      P(T) = 0.1–0.3,  P(G) = 0.1–0.2,  P(S) = 0.05–0.1
  - Parameter bisa di-override dari bkt_global_params.csv via seed_bkt_params.py
 
Digunakan oleh:
  - app/services/plan_service.py   → update_knowledge_states()
  - app/routers/bkt.py             → endpoint inspeksi parameter
  - scripts/seed_bkt_params.py     → load params hasil tuning
 
Data siswa (knowledge state) disimpan ke PostgreSQL (tabel knowledge_state),
BUKAN ke CSV. CSV hanya untuk fase eksperimen awal.
═══════════════════════════════════════════════════════════════════════════════
"""
import logging
from typing import Dict, List, Optional, Tuple
 
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import Topik
 
logger = logging.getLogger(__name__)
 
# ── KONSTANTA — sesuai Tabel 8 & 11 laporan ──────────────────────────────────
CORRECT_THRESHOLD = 70    # nilai ≥ 70 dianggap "correct" (sesuai 02_bkt_tuning.py)
DEFAULT_LEARN     = 0.15  # P(T) — titik tengah rentang 0.1–0.3
DEFAULT_SLIP      = 0.05  # P(S) — titik tengah rentang 0.05–0.1
DEFAULT_GUESS     = 0.10  # P(G) — titik tengah rentang 0.1–0.2
PRIOR_KNOWLEDGE   = 0.20  # P(L0) — default jika belum ada diagnostik
 

 
# ── SKILL PARAMETER ──────────────────────────────────────────────────────────

class SkillParams:
    """
    Parameter BKT per skill, disesuaikan dengan difficulty kurikulum.
    Slip naik seiring difficulty (topik sulit → lebih mudah salah walau tahu).
    """

    def __init__(self, skill_name: str, difficulty: float = 0.5):
        self.skill_name = skill_name
        d = difficulty # Menggunakan difficulty dari parameter database

        self.learn = DEFAULT_LEARN
        self.slip  = float(np.clip(DEFAULT_SLIP  + d * 0.05, 0.01, 0.15))
        self.guess = float(np.clip(DEFAULT_GUESS + (1 - d) * 0.05, 0.05, 0.20))

    def override(self, learn: float, slip: float, guess: float) -> "SkillParams":
        """Override dari file CSV hasil tuning (seed_bkt_params.py)."""
        self.learn = float(np.clip(learn, 0.01, 0.5))
        self.slip  = float(np.clip(slip,  0.01, 0.3))
        self.guess = float(np.clip(guess, 0.01, 0.4))
        return self
 
 
# ── BKT ENGINE ───────────────────────────────────────────────────────────────

class BKTEngine:
    """
    Engine BKT dengan parameter per-skill.
 
    Perbedaan dengan BKTModule lama di plan_service.py:
      - BKTModule: satu set parameter global untuk semua skill
      - BKTEngine: parameter berbeda per skill, disesuaikan difficulty kurikulum
    """
    def __init__(self, custom_params: Optional[Dict[str, Dict]] = None):
        self._params: Dict[str, SkillParams] = {}
        self._custom = custom_params or {}

    def _get_params(self, db: Session, skill_name: str) -> SkillParams:
        # Pengecekan dilakukan langsung ke database
        if skill_name not in self._params:
            topik_db = db.query(Topik).filter(Topik.nama == skill_name).first()
            difficulty = topik_db.difficulty_index if topik_db else 0.5
            
            sp = SkillParams(skill_name, difficulty)
            if skill_name in self._custom:
                c = self._custom[skill_name]
                sp.override(c["learn"], c["slip"], c["guess"])
            self._params[skill_name] = sp
        return self._params[skill_name]

    def update(
        self,
        db: Session,
        skill_name: str,
        p_knowledge: float,
        score: float,
        topik_list: List[str],
    ) -> Tuple[float, float]:
        """
        Update P(knowledge) untuk satu observasi.
        Formula identik dengan update_bkt() di 02_bkt_tuning.py.
 
        Args:
            skill_name  : Nama topik
            p_knowledge : P(L_{n-1}) — penguasaan sebelum sesi ini
            score       : Nilai 0–100
 
        Returns:
            (p_knowledge_baru, p_correct_pred)
        """
        sp      = self._get_params(db, skill_name)
        correct = 1 if score >= CORRECT_THRESHOLD else 0
 
        # Bayes update
        if correct == 1:
            p_post = (p_knowledge * (1 - sp.slip)) / ((p_knowledge * (1 - sp.slip)) + ((1 - p_knowledge) * sp.guess) + 1e-10)
        else:
            p_post = (p_knowledge * sp.slip) / ((p_knowledge * sp.slip) + ((1 - p_knowledge) * (1 - sp.guess)) + 1e-10)
 
        p_new          = float(np.clip(p_post + (1 - p_post) * sp.learn, 0.0, 1.0))
        p_correct_pred = p_new * (1 - sp.slip) + (1 - p_new) * sp.guess
 
        return p_new, p_correct_pred

    def batch_update(
        self,
        db: Session,
        skill_name: str,
        initial_knowledge: float,
        scores: List[float],
        topik_list: List[str],
    ) -> float:
        """Update BKT dari semua skor historis secara berurutan."""
        p = initial_knowledge
        for score in scores:
            p, _ = self.update(db, skill_name, p, score)
        return p

    def get_all_params(self, db: Session) -> List[Dict]:
        """Kembalikan semua parameter skill dari database."""
        topik_list = db.query(Topik).all()
        result = []
        for t in topik_list:
            sp = self._get_params(db, t.nama)
            result.append({
                "skill_name": sp.skill_name,
                "learn":      round(sp.learn, 4),
                "slip":       round(sp.slip,  4),
                "guess":      round(sp.guess, 4),
                "difficulty": round(t.difficulty_index, 3),
            })
        return result
 
 
# ── SINGLETON ─────────────────────────────────────────────────────────────────
bkt_engine = BKTEngine()