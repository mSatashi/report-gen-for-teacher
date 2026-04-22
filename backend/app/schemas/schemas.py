# =============================================================================
# FIX 1 ► GANTI SELURUH ISI: backend/app/schemas/schemas.py
#
# Root cause yang diperbaiki:
#   - Pydantic v2 tidak lagi pakai `class Config: from_attributes = True`
#     → diganti `model_config = ConfigDict(from_attributes=True)`
#   - MuridResponse tidak bisa di-serialize langsung dari ORM object Murid
#     karena field username/email_address ada di tabel Pengguna, bukan Murid.
#     → field dibuat Optional dengan default None agar serialisasi tidak crash
#       saat endpoint kelas.py mengembalikan Murid ORM langsung.
# =============================================================================

"""
schemas.py
Pydantic v2 schemas untuk request & response FastAPI.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    email_address: EmailStr
    password: str
    tipe_pengguna: str = Field(..., pattern="^(pengajar|murid)$")


class LoginRequest(BaseModel):
    email_address: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tipe_pengguna: str
    user_id: str


# ═══════════════════════════════════════════════════════════════════════════════
# MURID
# ═══════════════════════════════════════════════════════════════════════════════

class MuridCreate(BaseModel):
    username: str
    email_address: EmailStr
    password: str
    nama: str
    usia: Optional[int] = None
    level: Optional[str] = None
    credit_total: int = 0


class MuridUpdate(BaseModel):
    nama: Optional[str] = None
    usia: Optional[int] = None
    level: Optional[str] = None
    credit_total: Optional[int] = None


class MuridResponse(BaseModel):
    """
    Response schema untuk data murid.
    username & email_address dibuat Optional karena beberapa endpoint
    (mis. list_murid_kelas di kelas.py) mengisi field ini secara manual
    dari join query, sedangkan endpoint lain mengembalikan ORM Murid
    yang tidak punya field tersebut secara langsung.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: Optional[str] = None
    email_address: Optional[str] = None
    nama: Optional[str] = None
    usia: Optional[int] = None
    level: Optional[str] = None
    credit_total: int = 0
    credit_used: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class KelasCreate(BaseModel):
    nama: str
    mata_pelajaran: Optional[str] = None
    kredit: int = 0
    jadwal: Optional[str] = None


class KelasUpdate(BaseModel):
    nama: Optional[str] = None
    mata_pelajaran: Optional[str] = None
    kredit: Optional[int] = None
    jadwal: Optional[str] = None


class KelasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama: str
    mata_pelajaran: Optional[str] = None
    pengajar_id: Optional[str] = None
    kredit: int = 0
    jadwal: Optional[str] = None
    created_at: datetime


class TambahMuridKeKelas(BaseModel):
    murid_id: str


# ═══════════════════════════════════════════════════════════════════════════════
# LOG PERTEMUAN
# ═══════════════════════════════════════════════════════════════════════════════

class LogPertemuanCreate(BaseModel):
    kelas_id: str
    murid_id: Optional[str] = None
    tanggal: date
    topik: str
    nilai: Optional[float] = None
    tingkat_pemahaman: Optional[str] = None
    tingkat_keterlibatan: Optional[str] = None
    kompetensi_dicapai: Optional[str] = None
    target_materi_berikutnya: Optional[str] = None
    kendala: Optional[str] = None
    catatan: Optional[str] = None
    durasi_menit: Optional[int] = None
    metode_belajar: Optional[str] = None


class LogPertemuanUpdate(BaseModel):
    topik: Optional[str] = None
    nilai: Optional[float] = None
    tingkat_pemahaman: Optional[str] = None
    tingkat_keterlibatan: Optional[str] = None
    kompetensi_dicapai: Optional[str] = None
    target_materi_berikutnya: Optional[str] = None
    kendala: Optional[str] = None
    catatan: Optional[str] = None
    durasi_menit: Optional[int] = None
    metode_belajar: Optional[str] = None


class LogPertemuanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kelas_id: str
    murid_id: Optional[str] = None
    tanggal: date
    topik: str
    nilai: Optional[float] = None
    tingkat_pemahaman: Optional[str] = None
    tingkat_keterlibatan: Optional[str] = None
    kompetensi_dicapai: Optional[str] = None
    target_materi_berikutnya: Optional[str] = None
    kendala: Optional[str] = None
    catatan: Optional[str] = None
    durasi_menit: Optional[int] = None
    metode_belajar: Optional[str] = None
    created_at: datetime


class BulkUploadResponse(BaseModel):
    total_baris: int
    berhasil: int
    gagal: int
    detail_error: List[Dict[str, Any]] = []


# ═══════════════════════════════════════════════════════════════════════════════
# LAPORAN
# ═══════════════════════════════════════════════════════════════════════════════

class LaporanCreate(BaseModel):
    murid_id:        str
    kelas_id:        Optional[str]  = None
    periode_mulai:   Optional[date] = None
    periode_selesai: Optional[date] = None
    tipe_laporan:    str            = "perkembangan"
    # [INTEGRASI 04_llm_evaluation.py] Gaya penulisan laporan
    # Diteruskan ke NarrativeEngine sebagai instruksi gaya di prompt
    report_style:    str            = "Konstruktif dan Memotivasi"


class LaporanUpdate(BaseModel):
    konten: Optional[str] = None
    status: Optional[str] = None


class LaporanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    murid_id: str
    kelas_id: Optional[str] = None
    konten: str
    tipe_laporan: str
    status: str
    pdf_path: Optional[str] = None
    tanggal: datetime
    tanggal_dikirim: Optional[datetime] = None
    is_ai_generated: bool
    periode_mulai: Optional[date] = None
    periode_selesai: Optional[date] = None


class KirimLaporanRequest(BaseModel):
    email_tujuan: EmailStr
    catatan_tambahan: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# RENCANA STUDI
# ═══════════════════════════════════════════════════════════════════════════════

class RencanaStudiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kelas_id: str
    murid_id: Optional[str] = None
    waktu: datetime
    daftar_rekomendasi_materi: Optional[List[str]] = None
    estimasi_waktu_selesai: Optional[datetime] = None
    catatan_analisa: Optional[str] = None
    jadwal_mingguan: Optional[Dict[str, Any]] = None
    version: int = 1


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

class DiagnosticCreate(BaseModel):
    murid_id: str
    kelas_id: Optional[str] = None
    topik: str
    diagnostic_score: float = Field(..., ge=0, le=100)


class DiagnosticResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    murid_id: str
    topik: str
    diagnostic_score: float
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardSummary(BaseModel):
    total_siswa: int
    log_hari_ini: int
    plan_aktif: int
    report_pending: int
    aktivitas_terbaru: List[Dict[str, Any]] = []
    progress_siswa: List[Dict[str, Any]] = []
