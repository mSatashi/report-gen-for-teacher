import logging
import re
import json
from typing import Any, Dict, List, Optional
from app.ai.ollama_client import narrative_client

logger = logging.getLogger(__name__)

# ── Prompt Sanitizer (NF001) ──────────────────────────────────────────────────
_INJECTION_PATTERNS = re.compile(
    r"(ignore previous|disregard|system:|<\|im_start\|>|forget your|jailbreak|"
    r"act as|pretend you|you are now|new instruction)",
    re.IGNORECASE,
)

def sanitize_prompt(text: str) -> str:
    """Bersihkan input dari pola prompt injection."""
    if not text:
        return ""
    return _INJECTION_PATTERNS.sub("[REMOVED]", text)[:3000]

class NarrativeEngine:
    """
    Generate laporan perkembangan siswa murni menggunakan LLM.
    """

    async def generate_report(
        self,
        nama_murid: str,
        mata_pelajaran: str,
        log_data: List[Dict[str, Any]],
        periode_mulai: Optional[str] = None,
        periode_selesai: Optional[str] = None,
        knowledge_state: Optional[Dict[str, float]] = None,
        pso_recommended_route: Optional[str] = None,
        report_style: Optional[str] = None,
    ) -> str:
        # 1. Persiapan Data
        log_summary = self._format_log_summary(log_data)
        bkt_summary = self._format_bkt_summary(knowledge_state or {})
        pso_info = f"Rekomendasi PSO: {pso_recommended_route}" if pso_recommended_route else "Ikuti kurikulum standar."

        # 2. Prompt dengan "Trigger" eksplisit untuk panjang laporan
        # Prompt sekarang hanya fokus pada DATA, karena ATURAN sudah ada di Modelfile
        prompt = f"""
        DATA MURID:
        - Nama: {nama_murid}
        - Mapel: {mata_pelajaran}
        - Periode: {periode_mulai or '-'} s/d {periode_selesai or '-'}
        - Log Aktivitas Terakhir: \n{log_summary}
        - Status Penguasaan: \n\t{bkt_summary}
        - Arah Belajar: {pso_info}
        TUGAS: Berdasarkan data di atas, tuliskan laporan narasi yang detail untuk orang tua murid
        """.strip()

        logger.debug(f"Generating report for: {nama_murid}")
        logger.info(f"Final Prompt to AI:\n{prompt}")

        try:
            raw_response = await narrative_client.generate(prompt=prompt, num_predict=1000)
            
            # CLEANER: Cari teks di antara kurung kurawal { ... }
            # Ini untuk membuang "Thinking Process" yang mungkin bocor di luar JSON
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if match:
                clean_json = match.group(0)
            else:
                clean_json = raw_response

            try:
                data_json = json.loads(clean_json)
                return data_json.get("laporan_lengkap", raw_response)
            except json.JSONDecodeError:
                # Jika masih gagal JSON, bersihkan markdown code blocks jika ada
                fallback_text = raw_response.replace("```json", "").replace("```", "").strip()
                return fallback_text

        except Exception as e:
            logger.error(f"NarrativeEngine Error: {e}")
            raise RuntimeError(f"Gagal generate laporan: {str(e)}")

    def _format_log_summary(self, log_data: List[Dict]) -> str:
        if not log_data: return "Tidak ada aktivitas log."
        return "\n".join([
            f"- [{l.get('tanggal', '-')}] {l.get('topik', '-')} (Nilai: {l.get('nilai', '-')})"
            for l in log_data[-10:]
        ])

    def _format_bkt_summary(self, knowledge_state: Dict[str, float]) -> str:
        if not knowledge_state: return "Data penguasaan belum tersedia."
        return "\n".join([f"- {t}: {round(p * 100, 1)}%" for t, p in knowledge_state.items()])

narrative_engine = NarrativeEngine()