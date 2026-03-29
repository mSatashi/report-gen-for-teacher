"""
ai_service.py
NarrativeEngine  — generate laporan perkembangan siswa via LLM.
PlannerEngine    — generate rencana studi adaptif via LLM.
Keduanya menggunakan OllamaClient dan menerapkan:
  - Prompt sanitization (cegah injection)
  - Few-shot prompting
  - Temperature & top-p sesuai konfigurasi laporan (Section 4.3.2)
"""
import logging
import re
from typing import Any, Dict, List, Optional

from app.ai.ollama_client import narrative_client, planner_client

logger = logging.getLogger(__name__)

# ── Prompt Sanitizer ─────────────────────────────────────────────────────────

_INJECTION_PATTERNS = re.compile(
    r"(ignore previous|disregard|system:|<\|im_start\|>|forget your|jailbreak|"
    r"act as|pretend you|you are now|new instruction)",
    re.IGNORECASE,
)


def sanitize_prompt(text: str) -> str:
    """
    Membersihkan input pengguna dari pola prompt injection.
    NF001 — pengamanan query AI.
    """
    if not text:
        return ""
    cleaned = _INJECTION_PATTERNS.sub("[REMOVED]", text)
    # Batasi panjang teks input agar tidak overflow context
    return cleaned[:3000]


# ═══════════════════════════════════════════════════════════════════════════════
# NARRATIVE ENGINE — Generate Laporan
# ═══════════════════════════════════════════════════════════════════════════════

NARRATIVE_SYSTEM_PROMPT = """
Kamu adalah asisten pendidikan profesional yang bertugas menulis laporan perkembangan belajar siswa 
dalam Bahasa Indonesia yang formal namun hangat. Laporan harus:
1. Berdasarkan data yang diberikan, tidak mengarang fakta
2. Mencakup: ringkasan kemajuan, capaian akademik, perkembangan karakter, area pengembangan, rekomendasi
3. Ditulis dari sudut pandang pengajar kepada orang tua
4. Tidak mengandung data sensitif yang tidak perlu
5. Panjang sekitar 300-500 kata
Jangan tambahkan penjelasan atau komentar di luar isi laporan.
""".strip()

FEW_SHOT_LAPORAN = """
Contoh format laporan:
---
Laporan Perkembangan Belajar Siswa
Nama Siswa  : Aisya Putri
Periode     : Februari – Maret 2025
Mata Pelajaran: Matematika

RINGKASAN KEMAJUAN
Selama periode ini, Aisya menunjukkan kemajuan yang konsisten dalam memahami konsep aljabar dasar...

CAPAIAN AKADEMIK
Aisya berhasil menguasai persamaan linear satu variabel dengan tingkat pemahaman 78%...

AREA PENGEMBANGAN
Beberapa area yang masih perlu ditingkatkan: operasi bilangan negatif dan kecepatan membaca soal...

REKOMENDASI
Untuk periode berikutnya, disarankan untuk: (1) Memperkuat pemahaman bilangan negatif...
---
""".strip()


class NarrativeEngine:
    """
    Menghasilkan narasi deskriptif laporan perkembangan siswa
    berdasarkan data log pertemuan.
    """

    async def generate_report(
        self,
        nama_murid: str,
        mata_pelajaran: str,
        log_data: List[Dict[str, Any]],
        periode_mulai: Optional[str] = None,
        periode_selesai: Optional[str] = None,
        knowledge_state: Optional[Dict[str, float]] = None,
    ) -> str:
        """
        Generate narasi laporan perkembangan.

        Args:
            nama_murid       : Nama siswa
            mata_pelajaran   : Mata pelajaran / nama kelas
            log_data         : List log pertemuan (topik, nilai, catatan, dll)
            periode_mulai    : Tanggal awal periode laporan
            periode_selesai  : Tanggal akhir periode laporan
            knowledge_state  : Dict {topik: probabilitas_penguasaan} dari BKT
        """
        # Sanitasi semua input teks
        nama_murid     = sanitize_prompt(nama_murid)
        mata_pelajaran = sanitize_prompt(mata_pelajaran)

        # Susun ringkasan data log
        log_summary = self._format_log_summary(log_data)
        bkt_summary = self._format_bkt_summary(knowledge_state or {})

        prompt = f"""
{FEW_SHOT_LAPORAN}

Sekarang buatkan laporan untuk data berikut:

Nama Siswa    : {nama_murid}
Mata Pelajaran: {mata_pelajaran}
Periode       : {periode_mulai or "tidak ditentukan"} s/d {periode_selesai or "tidak ditentukan"}

Data Log Pertemuan:
{log_summary}

Estimasi Penguasaan Materi (dari sistem BKT):
{bkt_summary}

Tuliskan laporan perkembangan lengkap sesuai format contoh di atas.
""".strip()

        try:
            result = await narrative_client.generate(
                prompt=prompt,
                system_prompt=NARRATIVE_SYSTEM_PROMPT,
                temperature=0.6,
                top_p=0.9,
                max_tokens=1024,
            )
            return result if result else self._template_fallback(nama_murid, mata_pelajaran, log_data)
        except Exception as e:
            logger.error(f"NarrativeEngine gagal: {e}")
            return self._template_fallback(nama_murid, mata_pelajaran, log_data)

    async def analyze_class_data(
        self,
        nama_kelas: str,
        log_data: List[Dict[str, Any]],
    ) -> str:
        """
        Analisis data log pertemuan sebuah kelas secara keseluruhan.
        Menghasilkan draft_analisis yang digunakan oleh PlannerEngine.
        """
        log_summary = self._format_log_summary(log_data)
        prompt = f"""
Analisis data pembelajaran berikut untuk kelas {sanitize_prompt(nama_kelas)}:

{log_summary}

Buat analisis singkat dalam Bahasa Indonesia yang mencakup:
1. Topik yang sudah dikuasai dengan baik
2. Topik yang masih perlu diperkuat
3. Rata-rata nilai dan tren kemajuan
4. Estimasi sisa kredit / sesi yang dibutuhkan
5. Catatan khusus dari pengajar yang perlu diperhatikan

Format: paragraf padat, maksimal 300 kata.
""".strip()

        try:
            return await narrative_client.generate(prompt=prompt, temperature=0.5, max_tokens=512)
        except Exception as e:
            logger.error(f"Analisis kelas gagal: {e}")
            return f"Analisis otomatis gagal. Silakan lakukan analisis manual untuk kelas {nama_kelas}."

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _format_log_summary(self, log_data: List[Dict]) -> str:
        if not log_data:
            return "Belum ada data log pertemuan."
        lines = []
        for i, log in enumerate(log_data[-20:], 1):   # ambil 20 log terbaru
            lines.append(
                f"{i}. [{log.get('tanggal', '-')}] Topik: {log.get('topik', '-')} | "
                f"Nilai: {log.get('nilai', '-')} | "
                f"Pemahaman: {log.get('tingkat_pemahaman', '-')} | "
                f"Catatan: {sanitize_prompt(str(log.get('catatan', '-')))}"
            )
        return "\n".join(lines)

    def _format_bkt_summary(self, knowledge_state: Dict[str, float]) -> str:
        if not knowledge_state:
            return "Data BKT belum tersedia."
        lines = []
        for topik, prob in knowledge_state.items():
            persen = round(prob * 100, 1)
            status = "Dikuasai" if prob >= 0.7 else ("Sedang Dipelajari" if prob >= 0.4 else "Perlu Perhatian")
            lines.append(f"- {topik}: {persen}% ({status})")
        return "\n".join(lines)

    def _template_fallback(
        self, nama: str, mapel: str, logs: List[Dict]
    ) -> str:
        """Template statis jika LLM tidak tersedia."""
        nilai_list = [l.get("nilai") for l in logs if l.get("nilai") is not None]
        rata = round(sum(nilai_list) / len(nilai_list), 1) if nilai_list else "-"
        topik_list = list({l.get("topik") for l in logs if l.get("topik")})
        return (
            f"Laporan Perkembangan Belajar — {nama}\n"
            f"Mata Pelajaran: {mapel}\n\n"
            f"Siswa telah mengikuti {len(logs)} sesi pembelajaran "
            f"dengan rata-rata nilai {rata}.\n"
            f"Topik yang dipelajari: {', '.join(topik_list[:5]) or '-'}.\n\n"
            f"(Laporan ini dibuat secara otomatis. Model AI tidak tersedia saat pembuatan.)"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PLANNER ENGINE — Generate Rencana Studi Adaptif
# ═══════════════════════════════════════════════════════════════════════════════

PLANNER_SYSTEM_PROMPT = """
Kamu adalah sistem perencanaan kurikulum adaptif untuk lembaga bimbingan belajar.
Tugasmu adalah membuat jadwal dan urutan materi belajar yang optimal berdasarkan:
- Data penguasaan siswa saat ini (dari BKT)
- Jumlah sesi yang tersisa
- Target kurikulum

Berikan output dalam format JSON yang valid.
Jangan tambahkan teks di luar JSON.
""".strip()


class PlannerEngine:
    """
    Menghasilkan rencana studi adaptif berdasarkan draft analisis
    dan knowledge state siswa (output BKT + PSO).
    """

    async def generate_rencana_studi(
        self,
        nama_murid: str,
        mata_pelajaran: str,
        draft_analisis: str,
        knowledge_state: Dict[str, float],
        sisa_sesi: int,
        target_kurikulum: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate rencana studi adaptif.

        Returns:
            dict dengan keys:
                - rekomendasi_materi: List[str]
                - jadwal_mingguan: Dict (hari -> list materi)
                - catatan_analisa: str
                - estimasi_selesai_minggu: int
        """
        bkt_summary = "\n".join(
            [f"- {t}: {round(p*100,1)}%" for t, p in knowledge_state.items()]
        ) or "Data BKT belum tersedia."

        target_str = ", ".join(target_kurikulum) if target_kurikulum else "Sesuai silabus standar"

        prompt = f"""
Buat rencana studi adaptif untuk:
- Siswa     : {sanitize_prompt(nama_murid)}
- Pelajaran : {sanitize_prompt(mata_pelajaran)}
- Sisa Sesi : {sisa_sesi} pertemuan

Analisis kondisi belajar siswa:
{sanitize_prompt(draft_analisis)}

Status penguasaan materi (BKT):
{bkt_summary}

Target kurikulum yang harus dicapai:
{sanitize_prompt(target_str)}

Buat rencana studi dalam format JSON berikut (isi semua field):
{{
  "rekomendasi_materi": ["topik1", "topik2", ...],
  "jadwal_mingguan": {{
    "Minggu 1": ["topik untuk minggu 1", ...],
    "Minggu 2": ["topik untuk minggu 2", ...]
  }},
  "catatan_analisa": "penjelasan singkat mengapa urutan ini dipilih",
  "estimasi_selesai_minggu": 4,
  "prioritas_perhatian": ["topik yang paling perlu diperkuat"]
}}
""".strip()

        try:
            raw = await planner_client.generate(
                prompt=prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.4,   # lebih rendah agar output JSON konsisten
                top_p=0.9,
                max_tokens=1024,
            )
            return self._parse_json_response(raw)
        except Exception as e:
            logger.error(f"PlannerEngine gagal: {e}")
            return self._fallback_plan(mata_pelajaran, sisa_sesi, knowledge_state)

    def _parse_json_response(self, raw: str) -> Dict[str, Any]:
        """Parse JSON dari response LLM, handle jika ada teks tambahan."""
        import json
        # Cari blok JSON dalam response
        match = re.search(r"\{[\s\S]+\}", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        logger.warning("Gagal parse JSON dari PlannerEngine, pakai fallback")
        return {}

    def _fallback_plan(
        self,
        mata_pelajaran: str,
        sisa_sesi: int,
        knowledge_state: Dict[str, float],
    ) -> Dict[str, Any]:
        """Rencana studi statis jika LLM gagal."""
        topik_lemah = [t for t, p in knowledge_state.items() if p < 0.5]
        topik_kuat  = [t for t, p in knowledge_state.items() if p >= 0.7]
        rekomendasi = topik_lemah + [t for t in knowledge_state if t not in topik_lemah]
        return {
            "rekomendasi_materi": rekomendasi[:sisa_sesi],
            "jadwal_mingguan": {},
            "catatan_analisa": (
                f"Rencana dibuat secara statis (AI tidak tersedia). "
                f"Prioritaskan topik yang penguasaannya di bawah 50%: {', '.join(topik_lemah[:3]) or '-'}. "
                f"Topik yang sudah dikuasai: {', '.join(topik_kuat[:3]) or '-'}."
            ),
            "estimasi_selesai_minggu": max(1, sisa_sesi // 2),
            "prioritas_perhatian": topik_lemah[:3],
        }


# ── Singleton instances ───────────────────────────────────────────────────────
narrative_engine = NarrativeEngine()
planner_engine   = PlannerEngine()
