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
 
logger = logging.getLogger(__name__)
 
# ── KONSTANTA — sesuai Tabel 8 & 11 laporan ──────────────────────────────────
CORRECT_THRESHOLD = 70    # nilai ≥ 70 dianggap "correct" (sesuai 02_bkt_tuning.py)
DEFAULT_LEARN     = 0.15  # P(T) — titik tengah rentang 0.1–0.3
DEFAULT_SLIP      = 0.05  # P(S) — titik tengah rentang 0.05–0.1
DEFAULT_GUESS     = 0.10  # P(G) — titik tengah rentang 0.1–0.2
PRIOR_KNOWLEDGE   = 0.20  # P(L0) — default jika belum ada diagnostik
 
# ── URUTAN SKILL KURIKULUM ────────────────────────────────────────────────────
# Dari skill_graph di 01_generate_data.py — dipakai untuk hitung difficulty
SKILL_ORDER = [
    "bilangan_bulat", "penjumlahan", "pengurangan", "perkalian", "pembagian",
    "pecahan", "persentase", "aljabar_dasar",
    "persamaan_linear_satu_variabel", "perbandingan", "aritmatika_sosial",
    "himpunan", "keliling_luas", "teorema_pythagoras", "statistika_dasar",
    "pengolahan_data_dasar", "peluang_dasar", "bangun_ruang",
    "eksponen_logaritma", "fungsi_kuadrat", "sistem_persamaan_linear",
    "matriks", "barisan_deret", "trigonometri", "limit", "turunan", "integral",
]
 
 
def _difficulty(skill_name: str) -> float:
    """
    Difficulty 0.2–1.0 berdasarkan posisi dalam SKILL_ORDER.
    Semakin lanjut → semakin sulit → difficulty lebih tinggi.
    """
    if skill_name in SKILL_ORDER:
        idx = SKILL_ORDER.index(skill_name)
        return 0.2 + 0.8 * (idx / max(len(SKILL_ORDER) - 1, 1))
    return 0.5   # default untuk skill di luar daftar
 
 
# ── SKILL PARAMETER ──────────────────────────────────────────────────────────
 
class SkillParams:
    """
    Parameter BKT per skill, disesuaikan dengan difficulty kurikulum.
    Slip naik seiring difficulty (topik sulit → lebih mudah salah walau tahu).
    """
 
    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        d = _difficulty(skill_name)
 
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
    """
 
    def __init__(self, custom_params: Optional[Dict[str, Dict]] = None):
        self._params: Dict[str, SkillParams] = {}
        self._custom = custom_params or {}
 
    def _get_params(self, skill_name: str) -> SkillParams:
        if skill_name not in self._params:
            sp = SkillParams(skill_name)
            if skill_name in self._custom:
                c = self._custom[skill_name]
                sp.override(c["learn"], c["slip"], c["guess"])
            self._params[skill_name] = sp
        return self._params[skill_name]
 
    def update(
        self,
        skill_name: str,
        p_knowledge: float,
        score: float,
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
        sp      = self._get_params(skill_name)
        correct = 1 if score >= CORRECT_THRESHOLD else 0
 
        # Bayes update (Corbett & Anderson 1995, ref [14] laporan)
        if correct == 1:
            p_post = (
                (p_knowledge * (1 - sp.slip))
                / ((p_knowledge * (1 - sp.slip)) + ((1 - p_knowledge) * sp.guess) + 1e-10)
            )
        else:
            p_post = (
                (p_knowledge * sp.slip)
                / ((p_knowledge * sp.slip) + ((1 - p_knowledge) * (1 - sp.guess)) + 1e-10)
            )
 
        # Tambahkan probabilitas belajar dari sesi ini
        p_new          = float(np.clip(p_post + (1 - p_post) * sp.learn, 0.0, 1.0))
        p_correct_pred = p_new * (1 - sp.slip) + (1 - p_new) * sp.guess
 
        return p_new, p_correct_pred
 
    def batch_update(
        self,
        skill_name: str,
        initial_knowledge: float,
        scores: List[float],
    ) -> float:
        """Update BKT dari semua skor historis secara berurutan."""
        p = initial_knowledge
        for score in scores:
            p, _ = self.update(skill_name, p, score)
        return p
 
    def get_all_params(self) -> List[Dict]:
        """Kembalikan semua parameter skill (dipakai endpoint GET /bkt/params)."""
        skills = SKILL_ORDER if not self._params else list(self._params.keys())
        result = []
        for sname in skills:
            sp = self._get_params(sname)
            result.append({
                "skill_name": sp.skill_name,
                "learn":      round(sp.learn, 4),
                "slip":       round(sp.slip,  4),
                "guess":      round(sp.guess, 4),
                "difficulty": round(_difficulty(sname), 3),
            })
        return result
 
 
# ── SINGLETON ─────────────────────────────────────────────────────────────────
bkt_engine = BKTEngine()