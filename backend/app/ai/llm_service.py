"""
app/ai/llm_service.py

Integrasi dengan model LLM lokal (Ollama) maupun eksternal (OpenAI, Cendol).
Berisi:
  - OllamaClient   : panggil model lokal via Ollama
  - NarrativeEngine: generate laporan naratif dari data siswa
  - PlannerEngine  : generate rencana studi adaptif
"""
import re
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  PROMPT SANITIZER
#  Mencegah prompt injection (NF001)
# ═══════════════════════════════════════════════════════════════

# Pola berbahaya yang bisa disuntikkan pengguna
_INJECTION_PATTERNS = [
    r"ignore (previous|all) instructions?",
    r"system\s*:",
    r"<\s*/?system\s*>",
    r"<<\s*SYS\s*>>",
    r"\[INST\]",
    r"you are now",
    r"forget everything",
    r"act as (a|an)",
    r"jailbreak",
    r"DAN\b",
]
_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def sanitize_prompt(text: str) -> str:
    """
    Bersihkan input teks dari potensi prompt injection sebelum dikirim ke LLM.
    Teks yang mengandung pola berbahaya akan diblok / dihapus.
    """
    if not text:
        return ""

    for pattern in _COMPILED_PATTERNS:
        if pattern.search(text):
            logger.warning("Prompt injection terdeteksi dan diblokir: %s", text[:80])
            # Hapus bagian yang berbahaya, ganti dengan [DIHAPUS]
            text = pattern.sub("[DIHAPUS]", text)

    # Batasi panjang teks input untuk cegah token flood
    return text[:4000]


# ═══════════════════════════════════════════════════════════════
#  OLLAMA CLIENT  (Model Lokal)
# ═══════════════════════════════════════════════════════════════

class OllamaClient:
    """
    HTTP client untuk berkomunikasi dengan Ollama yang berjalan lokal.
    Dokumentasi API Ollama: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False,
    ) -> str:
        """
        Kirim prompt ke Ollama dan kembalikan teks respons.

        Args:
            prompt        : Prompt utama (sudah di-sanitize)
            system_prompt : Instruksi sistem (peran AI)
            temperature   : Kreativitas output (0.0 = deterministik)
            max_tokens    : Batas panjang output
            stream        : Jika True, respons di-stream (belum diimplementasi di sini)

        Returns:
            Teks hasil generate dari model
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature or settings.LLM_TEMPERATURE,
                "top_p": settings.LLM_TOP_P,
                "num_predict": max_tokens or settings.LLM_MAX_TOKENS,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()

        except httpx.ConnectError:
            logger.error("Gagal konek ke Ollama di %s — pastikan Ollama sudah berjalan", self.base_url)
            raise ConnectionError(
                f"Ollama tidak bisa diakses di {self.base_url}. "
                "Jalankan: `ollama serve` terlebih dahulu."
            )
        except httpx.HTTPStatusError as e:
            logger.error("Ollama HTTP error: %s", e)
            raise

    async def list_models(self) -> List[str]:
        """Ambil daftar model yang tersedia di Ollama lokal."""
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]

    async def health_check(self) -> bool:
        """Cek apakah Ollama berjalan."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(self.base_url)
                return response.status_code == 200
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════
#  CENDOL CLIENT  (Model Bahasa Indonesia - Eksternal)
# ═══════════════════════════════════════════════════════════════

class CendolClient:
    """
    Client untuk model Cendol — LLM berbahasa Indonesia.
    Menggunakan REST API endpoint yang disediakan pihak ketiga.
    Dokumentasi: [PLACEHOLDER_URL_DOKUMENTASI_CENDOL]
    """

    def __init__(self):
        self.api_url = settings.CENDOL_API_URL     # [PLACEHOLDER_URL_CENDOL]
        self.api_key = settings.CENDOL_API_KEY     # [PLACEHOLDER_API_KEY_CENDOL]
        self.model = settings.CENDOL_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        """
        Kirim request ke API Cendol.
        Sesuaikan payload dengan format API yang disediakan Cendol.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Format payload — sesuaikan dengan dokumentasi Cendol
        # [PLACEHOLDER: cek format request Cendol yang sesungguhnya]
        payload = {
            "model": self.model,
            "messages": [
                *([{"role": "system", "content": system_prompt}] if system_prompt else []),
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature or settings.LLM_TEMPERATURE,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
            "top_p": settings.LLM_TOP_P,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                # [PLACEHOLDER: sesuaikan key response dengan format Cendol]
                # Asumsi format mirip OpenAI:
                return data["choices"][0]["message"]["content"].strip()

        except httpx.ConnectError:
            logger.error("Gagal konek ke Cendol API di %s", self.api_url)
            raise
        except Exception as e:
            logger.error("Cendol API error: %s", e)
            raise


# ═══════════════════════════════════════════════════════════════
#  OPENAI CLIENT  (Opsional / Fallback)
# ═══════════════════════════════════════════════════════════════

class OpenAIClient:
    """
    Client untuk OpenAI API (GPT-4o, GPT-4o-mini).
    Bisa digunakan sebagai fallback jika Ollama/Cendol tidak tersedia.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY     # [PLACEHOLDER_API_KEY]
        self.model = settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                *([{"role": "system", "content": system_prompt}] if system_prompt else []),
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature or settings.LLM_TEMPERATURE,
            "max_tokens": max_tokens or settings.LLM_MAX_TOKENS,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()


# ═══════════════════════════════════════════════════════════════
#  LLM FACTORY  — pilih provider berdasarkan konfigurasi
# ═══════════════════════════════════════════════════════════════

def get_llm_client():
    """
    Kembalikan client LLM yang aktif berdasarkan LLM_PROVIDER di .env.
    Ubah nilai LLM_PROVIDER di .env untuk ganti provider:
      - "ollama"  → model lokal via Ollama
      - "cendol"  → model Cendol (bahasa Indonesia)
      - "openai"  → OpenAI GPT
    """
    provider = settings.LLM_PROVIDER.lower()
    if provider == "ollama":
        return OllamaClient()
    elif provider == "cendol":
        return CendolClient()
    elif provider == "openai":
        return OpenAIClient()
    else:
        logger.warning("LLM_PROVIDER tidak dikenal: %s. Fallback ke Ollama.", provider)
        return OllamaClient()


# ═══════════════════════════════════════════════════════════════
#  NARRATIVE ENGINE  — generate laporan perkembangan siswa
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT_NARRATIVE = """
Kamu adalah asisten pendidikan yang membantu pengajar les privat Indonesia 
membuat laporan perkembangan belajar siswa yang informatif, personal, dan mudah 
dipahami oleh orang tua. 

Aturan penting:
- Tulis dalam Bahasa Indonesia yang baik, formal namun hangat
- Fokus pada perkembangan positif dan area yang perlu dikembangkan  
- Jangan mengarang data yang tidak ada dalam input
- Laporan harus berdasarkan data nyata yang diberikan
- Gunakan kalimat yang membangun semangat siswa dan orang tua
- Panjang laporan: 300-500 kata
"""

FEW_SHOT_EXAMPLE = """
Contoh output laporan yang baik:
---
Laporan Perkembangan Belajar
Nama Siswa: Aisya Putri | Mata Pelajaran: Matematika | Periode: Februari - Maret 2025

RINGKASAN PERIODE
Aisya telah menyelesaikan 8 sesi belajar dalam periode ini dengan tingkat kehadiran 100%. 
Secara keseluruhan, ia menunjukkan perkembangan yang konsisten dan motivasi belajar yang tinggi.

CAPAIAN AKADEMIK
Matematika: Aisya berhasil menguasai konsep aljabar dasar dengan tingkat pemahaman 78%.
Persamaan linear satu variabel telah dikuasai dengan baik...

AREA PENGEMBANGAN
Beberapa topik yang masih perlu penguatan: operasi bilangan negatif dalam aljabar...

REKOMENDASI PLAN KE DEPAN
Untuk periode berikutnya, disarankan...
---
"""


class NarrativeEngine:
    """
    Service yang generate laporan naratif berbahasa Indonesia
    berdasarkan data log pertemuan dan knowledge state siswa.
    """

    def __init__(self):
        self.client = get_llm_client()

    async def generate_laporan(
        self,
        data_siswa: Dict[str, Any],
        log_pertemuan: List[Dict],
        knowledge_states: List[Dict],
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
    ) -> str:
        """
        Generate laporan perkembangan siswa.

        Args:
            data_siswa      : Info murid (nama, level, dll)
            log_pertemuan   : List dict dari log pertemuan dalam periode
            knowledge_states: List dict probabilitas penguasaan per topik
            period_start    : Tanggal mulai periode
            period_end      : Tanggal akhir periode

        Returns:
            Teks laporan dalam Bahasa Indonesia
        """
        # Sanitize semua input teks dari user
        nama_siswa = sanitize_prompt(data_siswa.get("nama", ""))
        level = sanitize_prompt(data_siswa.get("level", ""))
        catatan_list = [sanitize_prompt(log.get("catatan", "")) for log in log_pertemuan]

        # Ringkasan statistik
        nilai_list = [log["nilai"] for log in log_pertemuan if log.get("nilai") is not None]
        rata_nilai = sum(nilai_list) / len(nilai_list) if nilai_list else None
        total_sesi = len(log_pertemuan)
        topik_dipelajari = list({log["topik"] for log in log_pertemuan})

        # Rangkum knowledge state
        ks_summary = "\n".join(
            f"  - {ks['topic']}: {ks['knowledge']*100:.1f}% dikuasai"
            for ks in knowledge_states
        ) or "  (belum ada data knowledge state)"

        # Susun prompt
        prompt = f"""
{FEW_SHOT_EXAMPLE}

Sekarang buatkan laporan perkembangan untuk siswa berikut:

DATA SISWA:
- Nama: {nama_siswa}
- Level/Kelas: {level}
- Periode: {period_start or "N/A"} s/d {period_end or "N/A"}

RINGKASAN SESI BELAJAR:
- Total sesi: {total_sesi} pertemuan
- Rata-rata nilai: {f"{rata_nilai:.1f}" if rata_nilai else "N/A"}
- Topik yang dipelajari: {", ".join(topik_dipelajari[:10])}

ESTIMASI PENGUASAAN MATERI (Bayesian Knowledge Tracing):
{ks_summary}

CATATAN PENGAJAR (ringkasan):
{chr(10).join(f"  - {c}" for c in catatan_list if c)[:800]}

Buatkan laporan lengkap dalam format terstruktur.
"""

        try:
            result = await self.client.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_NARRATIVE,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
            return result
        except Exception as e:
            logger.error("NarrativeEngine gagal generate: %s", e)
            # Fallback ke template sederhana
            return self._template_fallback(data_siswa, log_pertemuan, rata_nilai, total_sesi)

    def _template_fallback(
        self,
        data_siswa: dict,
        log_pertemuan: list,
        rata_nilai: Optional[float],
        total_sesi: int,
    ) -> str:
        """Template sederhana jika LLM tidak tersedia."""
        topik_list = list({log["topik"] for log in log_pertemuan})
        return (
            f"Laporan Perkembangan Belajar\n"
            f"Nama Siswa: {data_siswa.get('nama', '-')}\n\n"
            f"Dalam periode ini, siswa telah mengikuti {total_sesi} sesi belajar. "
            f"Rata-rata nilai yang diperoleh adalah {rata_nilai:.1f}. "
            f"Topik yang dipelajari meliputi: {', '.join(topik_list)}.\n\n"
            f"(Catatan: laporan ini dibuat otomatis karena AI tidak tersedia)"
        )

    async def analisa_data_pertemuan(
        self, kelas_id: str, log_pertemuan: List[Dict]
    ) -> str:
        """
        Analisis data log pertemuan sebuah kelas untuk membuat draft analisis.
        Digunakan sebagai input PlannerEngine.
        """
        total = len(log_pertemuan)
        topik_list = [sanitize_prompt(log.get("topik", "")) for log in log_pertemuan]
        nilai_list = [log["nilai"] for log in log_pertemuan if log.get("nilai") is not None]
        rata = sum(nilai_list) / len(nilai_list) if nilai_list else None

        prompt = f"""
Analisis data pembelajaran kelas berikut dan berikan insight singkat:

Kelas ID: {kelas_id}
Total log: {total} pertemuan
Rata-rata nilai: {f"{rata:.1f}" if rata else "belum ada"}
Topik yang dicover: {", ".join(set(topik_list))}

Berikan analisis dalam format JSON dengan field:
- ringkasan_kemajuan (string)
- topik_kuat (list string)
- topik_perlu_penguatan (list string)
- estimasi_sisa_kredit_cukup (boolean)
- rekomendasi_singkat (string)
"""
        try:
            result = await self.client.generate(prompt=prompt, temperature=0.3)
            return result
        except Exception as e:
            logger.error("Analisa data pertemuan gagal: %s", e)
            return json.dumps({
                "ringkasan_kemajuan": f"Total {total} sesi dengan rata-rata {rata:.1f if rata else 'N/A'}",
                "topik_kuat": [],
                "topik_perlu_penguatan": topik_list[-3:],
                "estimasi_sisa_kredit_cukup": True,
                "rekomendasi_singkat": "Lanjutkan sesuai silabus.",
            })


# ═══════════════════════════════════════════════════════════════
#  PLANNER ENGINE  — generate rencana studi adaptif
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT_PLANNER = """
Kamu adalah sistem perencanaan kurikulum adaptif untuk les privat Indonesia.
Tugasmu adalah membuat rencana studi yang optimal berdasarkan:
1. Data knowledge state siswa saat ini (probabilitas penguasaan per topik)
2. Sisa sesi/kredit yang tersedia
3. Target kurikulum yang harus dicapai

Output harus dalam format JSON yang valid.
Jangan tambahkan teks di luar JSON.
"""


class PlannerEngine:
    """
    Service yang generate rencana studi adaptif menggunakan LLM + PSO.
    Berdasarkan knowledge state siswa dari BKT dan sisa kredit sesi.
    """

    def __init__(self):
        self.client = get_llm_client()

    async def generate_rencana_studi(
        self,
        draft_analisis: str,
        knowledge_states: List[Dict],
        sisa_kredit: int,
        target_kurikulum: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate rencana studi adaptif.

        Returns:
            Dict berisi:
            - rekomendasi_materi: List topik yang direkomendasikan
            - urutan_belajar: Urutan optimal
            - estimasi_sesi_per_topik: Dict {topik: jumlah_sesi}
            - catatan_planner: Penjelasan singkat keputusan
        """
        # Susun ringkasan knowledge state
        ks_text = "\n".join(
            f"  - {ks['topic']}: {ks['knowledge']*100:.1f}% dikuasai (masih perlu {(1-ks['knowledge'])*100:.1f}%)"
            for ks in knowledge_states
        ) or "  (belum ada data)"

        target_text = "\n".join(f"  - {t}" for t in (target_kurikulum or [])) or "  (tidak ditentukan)"

        prompt = f"""
Berdasarkan data berikut, buat rencana studi adaptif optimal:

DRAFT ANALISIS KELAS:
{sanitize_prompt(draft_analisis)[:1000]}

KNOWLEDGE STATE SISWA (probabilitas penguasaan):
{ks_text}

SISA KREDIT SESI: {sisa_kredit} pertemuan

TARGET KURIKULUM:
{target_text}

Buat rencana dalam format JSON:
{{
  "rekomendasi_materi": ["topik1", "topik2", ...],
  "urutan_belajar": ["topik_prioritas_1", "topik_prioritas_2", ...],
  "estimasi_sesi_per_topik": {{"topik1": 2, "topik2": 3}},
  "fokus_adaptasi": "penjelasan singkat topik yang perlu diperkuat",
  "catatan_planner": "alasan urutan yang dipilih"
}}
"""

        try:
            result = await self.client.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_PLANNER,
                temperature=0.3,    # lebih rendah untuk output lebih konsisten
                max_tokens=800,
            )
            # Parse JSON dari output LLM
            # Bersihkan backtick jika ada
            clean = result.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(clean)

        except json.JSONDecodeError as e:
            logger.error("PlannerEngine: output LLM bukan JSON valid: %s", e)
            # Fallback: prioritaskan topik dengan penguasaan terendah
            sorted_ks = sorted(knowledge_states, key=lambda x: x.get("knowledge", 1))
            rekomendasi = [ks["topic"] for ks in sorted_ks[:sisa_kredit]]
            return {
                "rekomendasi_materi": rekomendasi,
                "urutan_belajar": rekomendasi,
                "estimasi_sesi_per_topik": {t: 2 for t in rekomendasi},
                "fokus_adaptasi": "Topik dengan penguasaan terendah diprioritaskan",
                "catatan_planner": "Fallback heuristik karena LLM output tidak valid",
            }
        except Exception as e:
            logger.error("PlannerEngine gagal: %s", e)
            raise
