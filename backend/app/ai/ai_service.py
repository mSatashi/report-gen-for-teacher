import logging
import re
from typing import Any, Dict, List, Optional
 
from app.ai.ollama_client import narrative_client, planner_client
from app.ai.bkt_engine import SKILL_ORDER, PRIOR_KNOWLEDGE

logger = logging.getLogger(__name__)
 
# ── Prompt Sanitizer (NF001) ──────────────────────────────────────────────────
_INJECTION_PATTERNS = re.compile(
    r"(ignore previous|disregard|system:|<\|im_start\|>|forget your|jailbreak|"
    r"act as|pretend you|you are now|new instruction)",
    re.IGNORECASE,
)
 
 
def sanitize_prompt(text: str) -> str:
    """Bersihkan input dari pola prompt injection (NF001)."""
    if not text:
        return ""
    return _INJECTION_PATTERNS.sub("[REMOVED]", text)[:3000]
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# NARRATIVE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
 
NARRATIVE_SYSTEM_PROMPT = """
Kamu adalah asisten pendidikan profesional yang bertugas menulis laporan perkembangan belajar siswa
dalam Bahasa Indonesia yang formal namun hangat. Laporan harus:
1. Berdasarkan data yang diberikan, tidak mengarang fakta
2. Mencakup: ringkasan kemajuan, capaian akademik, area pengembangan, rencana selanjutnya, rekomendasi
3. Ditulis dari sudut pandang pengajar kepada orang tua
4. Panjang sekitar 300-500 kata
Jangan tambahkan penjelasan atau komentar di luar isi laporan.
""".strip()
 
# Few-shot example sesuai Section 4.3.2 laporan (1-2 contoh)
FEW_SHOT_LAPORAN = """
Contoh format laporan yang baik:
---
Laporan Perkembangan Belajar Siswa
Nama Siswa    : Aisya Putri
Periode       : Februari – Maret 2025
Mata Pelajaran: Matematika
 
RINGKASAN KEMAJUAN
Selama periode ini, Aisya menunjukkan kemajuan yang konsisten dalam memahami konsep aljabar dasar.
Tingkat kehadiran 100% mencerminkan komitmen yang tinggi terhadap proses belajar.
 
CAPAIAN AKADEMIK
Aisya berhasil menguasai persamaan linear satu variabel dengan tingkat pemahaman 78%.
Penguasaan topik bilangan bulat sudah sangat baik (di atas 85%).
 
AREA PENGEMBANGAN
Beberapa topik yang masih perlu ditingkatkan: operasi bilangan negatif dan kecepatan membaca soal.
 
RENCANA BELAJAR BERIKUTNYA
Berdasarkan analisis sistem BKT dan rekomendasi PSO, fokus periode berikutnya adalah
penguatan materi fungsi kuadrat dan sistem persamaan linear sebagai fondasi untuk kalkulus.
 
REKOMENDASI
(1) Latihan soal variasi bilangan negatif 2x seminggu
(2) Review aljabar dasar sebelum masuk ke topik baru
---
""".strip()
 
 
class NarrativeEngine:
    """
    Generate laporan perkembangan siswa menggunakan LLM.
    Data masukan dari PostgreSQL (via report_service.py), bukan dari CSV.
    """
 
    async def generate_report(
        self,
        nama_murid: str,
        mata_pelajaran: str,
        log_data: List[Dict[str, Any]],
        periode_mulai: Optional[str] = None,
        periode_selesai: Optional[str] = None,
        knowledge_state: Optional[Dict[str, float]] = None,
        # [INTEGRASI 04_llm_evaluation.py] Parameter baru
        pso_recommended_route: Optional[str] = None,
        report_style: Optional[str] = None,
    ) -> str:
        """
        Generate narasi laporan perkembangan.
 
        Args:
            pso_recommended_route : Output dari PlannerEngine/PSO — topik berikutnya
            report_style          : Gaya penulisan (Konstruktif/Formal/Ringkas/Detail)
        """
        nama_murid     = sanitize_prompt(nama_murid)
        mata_pelajaran = sanitize_prompt(mata_pelajaran)
 
        log_summary = self._format_log_summary(log_data)
        bkt_summary = self._format_bkt_summary(knowledge_state or {})
 
        # [INTEGRASI] Section PSO dalam prompt — sesuai pola 04_llm_evaluation.py
        pso_section = ""
        if pso_recommended_route:
            pso_section = (
                f"\nRencana Belajar Berikutnya (Rekomendasi Sistem PSO):\n"
                f"{sanitize_prompt(pso_recommended_route)}\n"
            )
 
        # [INTEGRASI] Instruksi gaya penulisan
        style_section = ""
        if report_style:
            style_section = (
                f"\nGaya penulisan yang diinginkan: {sanitize_prompt(report_style)}.\n"
                f"Pastikan nada dan struktur laporan mencerminkan gaya tersebut.\n"
            )
 
        prompt = f"""
{FEW_SHOT_LAPORAN}
 
Sekarang buatkan laporan untuk data berikut:
 
Nama Siswa    : {nama_murid}
Mata Pelajaran: {mata_pelajaran}
Periode       : {periode_mulai or "tidak ditentukan"} s/d {periode_selesai or "tidak ditentukan"}
 
Data Log Pertemuan (20 sesi terakhir):
{log_summary}
 
Estimasi Penguasaan Materi dari Sistem BKT:
{bkt_summary}
{pso_section}{style_section}
Tuliskan laporan perkembangan lengkap sesuai format contoh di atas.
""".strip()
 
        try:
            result = await narrative_client.generate(
                prompt=prompt,
                system_prompt=NARRATIVE_SYSTEM_PROMPT,
                temperature=0.6,   # Tabel 10: 0.5–0.7
                top_p=0.9,         # Tabel 10: 0.9
                max_tokens=1024,   # Tabel 10: 512–1024
            )
            return result if result else self._template_fallback(
                nama_murid, mata_pelajaran, log_data, knowledge_state, pso_recommended_route
            )
        except Exception as e:
            logger.error(f"NarrativeEngine gagal: {e}")
            return self._template_fallback(
                nama_murid, mata_pelajaran, log_data, knowledge_state, pso_recommended_route
            )
 
    async def analyze_class_data(
        self,
        nama_kelas: str,
        log_data: List[Dict[str, Any]],
    ) -> str:
        """
        Analisis log pertemuan kelas → draft_analisis untuk PlannerEngine.
        Tidak berubah dari versi sebelumnya.
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
5. Catatan khusus yang perlu diperhatikan
 
Format: paragraf padat, maksimal 300 kata.
""".strip()
 
        try:
            return await narrative_client.generate(prompt=prompt, temperature=0.5, max_tokens=512)
        except Exception as e:
            logger.error(f"Analisis kelas gagal: {e}")
            return f"Analisis otomatis gagal untuk kelas {nama_kelas}. Lakukan analisis manual."
 
    # ── Helpers ───────────────────────────────────────────────────────────────
 
    def _format_log_summary(self, log_data: List[Dict]) -> str:
        if not log_data:
            return "Belum ada data log pertemuan."
        lines = []
        for i, log in enumerate(log_data[-20:], 1):
            lines.append(
                f"{i}. [{log.get('tanggal', '-')}] {log.get('topik', '-')} | "
                f"Nilai: {log.get('nilai', '-')} | "
                f"Pemahaman: {log.get('tingkat_pemahaman', '-')} | "
                f"Catatan: {sanitize_prompt(str(log.get('catatan', '-')))}"
            )
        return "\n".join(lines)
 
    def _format_bkt_summary(self, knowledge_state: Dict[str, float]) -> str:
        if not knowledge_state:
            return "Data BKT belum tersedia."
        lines = []
        for topik, prob in sorted(knowledge_state.items(), key=lambda x: x[1]):
            persen = round(prob * 100, 1)
            status = "Dikuasai" if prob >= 0.7 else ("Sedang Dipelajari" if prob >= 0.4 else "Perlu Perhatian")
            lines.append(f"- {topik}: {persen}% ({status})")
        return "\n".join(lines)
 
    def _template_fallback(
        self,
        nama: str,
        mapel: str,
        logs: List[Dict],
        knowledge_state: Optional[Dict[str, float]] = None,
        pso_route: Optional[str] = None,
    ) -> str:
        """
        Template statis jika LLM tidak tersedia.
        [INTEGRASI] Disertakan info BKT + PSO sesuai _template_report() di 04_llm_evaluation.py.
        """
        nilai_list = [l.get("nilai") for l in logs if l.get("nilai") is not None]
        rata       = round(sum(nilai_list) / len(nilai_list), 1) if nilai_list else "-"
        topik_list = list({l.get("topik") for l in logs if l.get("topik")})
 
        bkt_line = ""
        if knowledge_state:
            dikuasai   = [t for t, p in knowledge_state.items() if p >= 0.7]
            perlu_review = [t for t, p in knowledge_state.items() if p < 0.4]
            bkt_line = (
                f"\nStatus Pemahaman (BKT): {len(dikuasai)}/{len(knowledge_state)} topik dikuasai (≥70%)."
            )
            if perlu_review:
                bkt_line += f"\nTopik perlu perhatian: {', '.join(perlu_review[:3])}."
 
        pso_line = f"\nRencana Belajar Berikutnya (PSO): {pso_route}" if pso_route else ""
 
        return (
            f"Laporan Perkembangan Belajar — {nama}\n"
            f"Mata Pelajaran: {mapel}\n\n"
            f"Siswa telah mengikuti {len(logs)} sesi pembelajaran "
            f"dengan rata-rata nilai {rata}.\n"
            f"Topik yang dipelajari: {', '.join(topik_list[:5]) or '-'}."
            f"{bkt_line}{pso_line}\n\n"
            f"(Laporan ini dibuat secara otomatis. Model AI tidak tersedia.)"
        )
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# PLANNER ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
 
PLANNER_SYSTEM_PROMPT = """
Kamu adalah sistem perencanaan kurikulum adaptif untuk lembaga bimbingan belajar.
Tugasmu membuat rencana studi optimal berdasarkan:
- Data penguasaan siswa saat ini dari BKT (probabilitas per topik)
- Jumlah sesi yang tersisa
- Target kurikulum yang harus dicapai
 
Output dalam format JSON yang valid. Jangan tambahkan teks di luar JSON.
""".strip()
 
 
class PlannerEngine:
    """
    Generate rencana studi adaptif berdasarkan BKT + PSO via LLM.
    Data masukan dari PostgreSQL (via plan_service.py), bukan dari CSV.
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
        if not knowledge_state:
            knowledge_state = {skill: PRIOR_KNOWLEDGE for skill in SKILL_ORDER}
            logger.info(
                f"knowledge_state kosong untuk {nama_murid}, "
                f"menggunakan PRIOR_KNOWLEDGE ({PRIOR_KNOWLEDGE}) dari SKILL_ORDER bkt_engine"
            )

        bkt_summary = "\n".join(
            [f"- {t}: {round(p*100,1)}%" for t, p in sorted(knowledge_state.items(), key=lambda x: x[1])]
        ) or "Data BKT belum tersedia."
 
        target_str = ", ".join(target_kurikulum) if target_kurikulum else "Sesuai silabus standar"
 
        prompt = f"""
Buat rencana studi adaptif untuk:
- Siswa     : {sanitize_prompt(nama_murid)}
- Pelajaran : {sanitize_prompt(mata_pelajaran)}
- Sisa Sesi : {sisa_sesi} pertemuan
 
Analisis kondisi belajar (dari log dan BKT):
{sanitize_prompt(draft_analisis)}
 
Status penguasaan materi saat ini (BKT — urutan dari terendah):
{bkt_summary}
 
Target kurikulum:
{sanitize_prompt(target_str)}
 
Buat rencana dalam format JSON berikut:
{{
  "rekomendasi_materi": ["topik1", "topik2", ...],
  "jadwal_mingguan": {{
    "Minggu 1": ["topik untuk minggu 1"],
    "Minggu 2": ["topik untuk minggu 2"]
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
                temperature=0.4,   # lebih rendah agar JSON konsisten
                top_p=0.9,
                max_tokens=1024,
            )
            return self._parse_json_response(raw)
        except Exception as e:
            logger.error(f"PlannerEngine gagal: {e}")
            return self._fallback_plan(mata_pelajaran, sisa_sesi, knowledge_state)
 
    def _parse_json_response(self, raw: str) -> Dict[str, Any]:
        import json

        if not raw:
            logger.warning("PlannerEngine: response kosong dari LLM")
            return {}

        # Langkah 1: hapus fences ```json ... ``` atau ``` ... ```
        cleaned = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE).replace("```", "").strip()

        # Langkah 2: coba parse langsung
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Langkah 3: cari blok JSON pertama yang valid (greedy dari { sampai } terakhir)
        # Ini lebih andal dari regex \{[\s\S]+\} untuk JSON dengan nested objects
        brace_start = cleaned.find("{")
        brace_end   = cleaned.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            candidate = cleaned[brace_start : brace_end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        logger.warning(f"Gagal parse JSON dari PlannerEngine. Raw response (100 char): {raw[:100]}")
        return {}
 
    def _fallback_plan(
        self, mata_pelajaran: str, sisa_sesi: int, knowledge_state: Dict[str, float]
    ) -> Dict[str, Any]:
        if knowledge_state:
            # Prioritaskan topik belum dikuasai, urut dari p_knowledge terendah
            topik_lemah = sorted(
                [(t, p) for t, p in knowledge_state.items() if p < 0.7],
                key=lambda x: x[1]
            )
            rekomendasi = [t for t, _ in topik_lemah[:max(sisa_sesi, 5)]]
            topik_kuat  = [t for t, p in knowledge_state.items() if p >= 0.7]
        else:
            rekomendasi = SKILL_ORDER[:max(sisa_sesi, 5)]
            topik_kuat  = []

        # Buat jadwal mingguan sederhana — bagi rekomendasi per minggu (2 topik/minggu)
        jadwal: Dict[str, List[str]] = {}
        for i in range(0, len(rekomendasi), 2):
            minggu = f"Minggu {i // 2 + 1}"
            jadwal[minggu] = rekomendasi[i : i + 2]

        return {
            "rekomendasi_materi":      rekomendasi,
            "jadwal_mingguan":         jadwal,
            "catatan_analisa":         (
                f"Rencana statis (LLM tidak tersedia). "
                f"Prioritaskan: {', '.join(rekomendasi[:3]) or '-'}. "
                f"Sudah dikuasai: {', '.join(topik_kuat[:3]) or '-'}."
            ),
            "estimasi_selesai_minggu": max(1, sisa_sesi // 2),
            "prioritas_perhatian":     rekomendasi[:3],
        }
 
 
# ── Singleton instances ───────────────────────────────────────────────────────
narrative_engine = NarrativeEngine()
planner_engine   = PlannerEngine()