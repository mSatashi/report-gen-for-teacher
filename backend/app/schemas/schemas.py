"""
schemas.py
Pydantic v2 schemas untuk request & response FastAPI.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re as _re

EducationLevel = Literal["SD-1", "SD-2", "SD-3", "SD-4", "SD-5", "SD-6", "SMP-1", "SMP-2", "SMP-3", "SMK-1", "SMK-2", "SMK-3", "SMK-4", "SMA-1", "SMA-2", "SMA-3"]
JenisKelamin   = Literal["Laki-laki", "Perempuan"]
Hari = Literal["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    email_address: EmailStr
    password: str
    tipe_pengguna: str = Field(..., pattern="^(pengajar)$")


class LoginRequest(BaseModel):
    email_address: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tipe_pengguna: str
    user_id: str
    username: str
    email_address: EmailStr



# ═══════════════════════════════════════════════════════════════════════════════
# MURID
# ═══════════════════════════════════════════════════════════════════════════════

class MuridCreate(BaseModel):
    email_address: EmailStr
    nama: str
    education_level: EducationLevel
    jenis_kelamin: JenisKelamin
    is_active: bool = True

class MuridUpdate(BaseModel):
    education_level: Optional[EducationLevel] = None

class MuridResponse(BaseModel):
    """
    Response schema untuk data murid.
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    email_address: Optional[str] = None
    nama: Optional[str] = None
    education_level: Optional[EducationLevel]= None
    jenis_kelamin: Optional[JenisKelamin] = None
    is_active: bool = True

# ═══════════════════════════════════════════════════════════════════════════════
# Mata Pelajaran
# ═══════════════════════════════════════════════════════════════════════════════
class MataPelajaranCreate(BaseModel):
    nama_mata_pelajaran: str = Field(..., min_length=1)
    topik: List[str] = Field(default_factory=list, description="Daftar topik mata pelajaran")

class MataPelajaranUpdate(BaseModel):
    nama_mata_pelajaran: Optional[str]   = None
    topik: Optional[List[str]] = None
 
class MataPelajaranResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    id:                  str
    nama_mata_pelajaran: str
    topik:               List[str] = []
    created_at:          datetime
    updated_at:          datetime

# ═══════════════════════════════════════════════════════════════════════════════
# KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class KelasCreate(BaseModel):
    nama: str 
    mata_pelajaran_id: str
    hari: Hari
    jam: str = Field(..., description="Format HH:MM")

    @field_validator("jam")
    @classmethod
    def validasi_format_jam(cls, v: str) -> str:
        if not _re.match(r"^([01]\d|2[0-3]):[0-5]\d$", v):
            raise ValueError("jam harus format HH:MM (contoh: '08:00', '13:30')")
        return v


class KelasUpdate(BaseModel):
    nama: Optional[str] = None
    mata_pelajaran_id: Optional[str] = None
    hari: Optional[Hari] = None
    jam: Optional[str] = None

    @field_validator("jam")
    @classmethod
    def validasi_format_jam(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not _re.match(r"^([01]\d|2[0-3]):[0-5]\d$", v):
            raise ValueError("jam harus format HH:MM (contoh: '08:00', '13:30')")
        return v


class KelasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nama: str
    mata_pelajaran_id: Optional[str] = None
    mata_pelajaran: Optional[MataPelajaranResponse] = Field(None, alias="mata_pelajaran_obj")
    pengajar_id: Optional[str] = None
    hari: str
    jam: str
    created_at: datetime


class TambahMuridKeKelas(BaseModel):
    murid_id: str

# ═══════════════════════════════════════════════════════════════════════════════
# LOG PERTEMUAN
# ═══════════════════════════════════════════════════════════════════════════════

class LogPertemuanCreate(BaseModel):
    kelas_id: str
    murid_id: str
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
    murid_id: str
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
    username: str       
    email_address: str   
    total_siswa: int
    log_hari_ini: int
    plan_aktif: int
    report_pending: int
    aktivitas_terbaru: List[Dict[str, Any]] = []
    progress_siswa: List[Dict[str, Any]] = []
