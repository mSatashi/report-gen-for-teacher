"""
schemas.py
Pydantic v2 schemas untuk request & response FastAPI.
Sinkron dengan tabel PostgreSQL (BKT & PSO Engine).
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re as _re

# Tipe data khusus untuk konsistensi input
EducationLevel = Literal["SD-1", "SD-2", "SD-3", "SD-4", "SD-5", "SD-6", "SMP-1", "SMP-2", "SMP-3", "SMK-1", "SMK-2", "SMK-3", "SMK-4", "SMA-1", "SMA-2", "SMA-3"]
JenisKelamin   = Literal["Laki-laki", "Perempuan"]
Hari           = Literal["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    email_address: EmailStr
    password: str
    tipe_pengguna: str = Field(..., pattern="^(pengajar|admin)$")

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
    nama: Optional[str] = None
    email_address: Optional[EmailStr] = None
    jenis_kelamin: Optional[JenisKelamin] = None
    education_level: Optional[EducationLevel] = None
    is_active: Optional[bool] = None

class MuridResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email_address: str
    nama: Optional[str] = None
    education_level: Optional[str] = None
    jenis_kelamin: Optional[str] = None
    diagnostic_level: Optional[str] = None
    is_active: bool

# ═══════════════════════════════════════════════════════════════════════════════
# MATA PELAJARAN & TOPIK (Skill Graph)
# ═══════════════════════════════════════════════════════════════════════════════

class TopikCreate(BaseModel):
    mata_pelajaran_id: str
    nama: str
    difficulty_index: float = Field(0.5, ge=0.0, le=1.0, description="0.0 mudah, 1.0 sangat sulit")
    prasyarat_ids: Optional[List[str]] = Field(default_factory=list, description="ID topik lain yang harus dikuasai dulu")

class TopikUpdate(BaseModel):
    mata_pelajaran_id: Optional[str] = None
    nama: Optional[str] = None
    difficulty_index: Optional[float] = Field(None, ge=0.0, le=1.0)

class TopikResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nama: str
    difficulty_index: float
    prasyarat: List["TopikResponse"] = []

class MataPelajaranCreate(BaseModel):
    nama_mata_pelajaran: str
    hari: Optional[Hari] = None
    jam: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")

class MataPelajaranResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nama_mata_pelajaran: str
    hari: Optional[str] = None
    jam: Optional[str] = None
    topik_list: List[TopikResponse] = []

# ═══════════════════════════════════════════════════════════════════════════════
# KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class KelasCreate(BaseModel):
    nama: str 
    mata_pelajaran_id: str
    hari: Hari
    jam: str = Field(..., description="Format HH:MM")
    kredit: int = Field(20, ge=1, description="Saldo/Jumlah pertemuan maksimal") 

    @field_validator("jam")
    @classmethod
    def validasi_format_jam(cls, v: str) -> str:
        if not _re.match(r"^([01]\d|2[0-3]):[0-5]\d$", v):
            raise ValueError("jam harus format HH:MM (contoh: '08:00', '13:30')")
        return v

class KelasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nama: str
    mata_pelajaran_id: Optional[str] = None
    pengajar_id: Optional[str] = None
    hari: str
    jam: str
    kredit: int
    created_at: datetime

# ═══════════════════════════════════════════════════════════════════════════════
# LOG PERTEMUAN (Input Utama BKT)
# ═══════════════════════════════════════════════════════════════════════════════

class LogPertemuanCreate(BaseModel):
    """
    Input manual guru. Kolom 'nilai' akan memicu kalkulasi BKT.
    """
    kelas_id: str
    murid_id: str
    # mata_pelajaran_id: str  <-- HAPUS ATAU COMMENT BARIS INI
    tanggal: date
    topik: str  
    nilai: Optional[float] = Field(None, ge=0, le=100)
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
    kelas_id: str | None = None
    murid_id: str
    # mata_pelajaran_id: str <-- HAPUS ATAU COMMENT BARIS INI
    tanggal: date
    topik: str
    nilai: Optional[float]
    catatan: Optional[str]
    created_at: datetime


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



# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE STATE (Output BKT)
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeStateResponse(BaseModel):
    """
    Schema untuk melihat estimasi penguasaan siswa hasil olah data BKT.
    """
    model_config = ConfigDict(from_attributes=True)
    murid_id: str
    topik: str
    p_knowledge: float = Field(..., description="P(L) - Probabilitas penguasaan (0.0 - 1.0)")
    updated_at: datetime

# ═══════════════════════════════════════════════════════════════════════════════
# RENCANA STUDI (Output PSO)
# ═══════════════════════════════════════════════════════════════════════════════

class RencanaStudiResponse(BaseModel):
    """
    Schema hasil perencanaan optimasi PSO.
    """
    model_config = ConfigDict(from_attributes=True)
    id: str
    murid_id: Optional[str] = None
    daftar_rekomendasi_materi: Optional[List[str]] = Field(None, description="Urutan topik hasil optimasi PSO")
    jadwal_mingguan: Optional[List[Dict[str, Any]]] = None  # <--- UBAH DI SINI
    catatan_analisa: Optional[str] = None
    estimasi_waktu_selesai: Optional[datetime] = None
    is_outdated: bool = False
    version: int = 1

# ═══════════════════════════════════════════════════════════════════════════════
# LAPORAN & DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

class LaporanCreate(BaseModel):
    murid_id: str
    kelas_id: Optional[str] = None
    periode_mulai: Optional[date] = None
    periode_selesai: Optional[date] = None
    report_style: str = "Konstruktif dan Memotivasi"

class LaporanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    konten: str
    status: str
    pdf_path: Optional[str] = None
    tanggal: datetime
    is_ai_generated: bool

class DiagnosticCreate(BaseModel):
    murid_id: str
    kelas_id: Optional[str] = None # <--- Tambahkan baris ini
    topik: str
    diagnostic_score: float = Field(..., ge=0, le=100)

class DiagnosticUpdate(BaseModel):
    diagnostic_score: Optional[float] = Field(None, ge=0, le=100)
    topik: Optional[str] = None
    kelas_id: Optional[str] = None

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
    total_siswa: int
    log_hari_ini: int
    plan_aktif: int
    report_pending: int
    aktivitas_terbaru: List[Dict[str, Any]] = []
    progress_siswa: List[Dict[str, Any]] = []

# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA TAMBAHAN (UPDATE & REQUEST KHUSUS)
# ═══════════════════════════════════════════════════════════════════════════════

# -- Mata Pelajaran --
class MataPelajaranUpdate(BaseModel):
    nama_mata_pelajaran: Optional[str] = None
    hari: Optional[Hari] = None
    jam: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")

# -- Kelas --
class KelasUpdate(BaseModel):
    nama: Optional[str] = None
    mata_pelajaran_id: Optional[str] = None
    hari: Optional[str] = None
    jam: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    kredit: Optional[int] = Field(None, ge=1)

class TambahMuridKeKelas(BaseModel):
    murid_id: str

# -- Log Pertemuan --
class BulkUploadResponse(BaseModel):
    total_baris: int
    berhasil: int
    gagal: int
    detail_error: List[Dict[str, Any]] =[]

# -- Laporan --
class LaporanUpdate(BaseModel):
    konten: Optional[str] = None
    status: Optional[str] = None

class KirimLaporanRequest(BaseModel):
    email_tujuan: EmailStr
    catatan_tambahan: Optional[str] = None