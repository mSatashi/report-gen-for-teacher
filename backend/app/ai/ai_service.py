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
        prompt = f"""
TULIS LAPORAN PERKEMBANGAN MURID SEKARANG.
Gunakan identitas asisten 'Sania'.

DATA INPUT:
Nama Siswa: {nama_murid}
Mata Pelajaran: {mata_pelajaran}
Periode: {periode_mulai or 'N/A'} s/d {periode_selesai or 'N/A'}

LOG AKTIVITAS:
{log_summary}

PENGUASAAN MATERI (BKT):
{bkt_summary}

{pso_info}

INSTRUKSI KHUSUS:
- Tulis minimal500 kata.
- Format output HARUS JSON dengan field: "nama_siswa", "laporan_lengkap", "status".
- Isi field "laporan_lengkap" dengan narasi laporan yang hangat dan mendetail.
""".strip()

        try:
            # 3. Panggil Ollama
            raw_response = await narrative_client.generate(prompt=prompt, num_predict=2048)
            
            if not raw_response:
                raise ValueError("Model AI memberikan respons kosong.")

            # 4. Parsing JSON dari respons model
            try:
                data_json = json.loads(raw_response)
                # Ambil hanya isi laporannya saja untuk disimpan ke field 'konten' di DB
                return data_json.get("laporan_lengkap", raw_response)
            except json.JSONDecodeError:
                # Jika model gagal memberikan JSON tapi memberikan teks biasa, tetap ambil teksnya
                logger.warning("AI tidak memberikan format JSON yang valid, mengambil teks mentah.")
                return raw_response

        except Exception as e:
            logger.error(f"NarrativeEngine Error: {e}")
            # Raise exception agar router 'laporan.py' menangkap ini sebagai error 500
            # Bukan mengembalikan string yang malah disimpan sebagai laporan sukses
            raise RuntimeError(f"Gagal generate laporan: {str(e)}")

    def _format_log_summary(self, log_data: List[Dict]) -> str:
        if not log_data: return "Tidak ada aktivitas log."
        return "\n".join([
            f"- [{l.get('tanggal', '-')}] {l.get('topik', '-')} (Nilai: {l.get('nilai', '-')})"
            for l in log_data[-20:]
        ])

    def _format_bkt_summary(self, knowledge_state: Dict[str, float]) -> str:
        if not knowledge_state: return "Data penguasaan belum tersedia."
        return "\n".join([f"- {t}: {round(p * 100, 1)}%" for t, p in knowledge_state.items()])

narrative_engine = NarrativeEngine()