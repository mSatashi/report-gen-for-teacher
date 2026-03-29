"""
schemas.py
Pydantic schemas untuk request & response FastAPI.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


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
    id: str
    username: str
    email_address: str
    nama: Optional[str]
    usia: Optional[int]
    level: Optional[str]
    credit_total: int
    credit_used: int

    class Config:
        from_attributes = True


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
    id: str
    nama: str
    mata_pelajaran: Optional[str]
    pengajar_id: Optional[str]
    kredit: int
    jadwal: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


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
    tingkat_pemahaman: Optional[str] = None       # sangat_paham | paham | cukup | perlu_review
    tingkat_keterlibatan: Optional[str] = None    # sangat_aktif | aktif | kurang_fokus
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
    id: str
    kelas_id: str
    murid_id: Optional[str]
    tanggal: date
    topik: str
    nilai: Optional[float]
    tingkat_pemahaman: Optional[str]
    tingkat_keterlibatan: Optional[str]
    kompetensi_dicapai: Optional[str]
    target_materi_berikutnya: Optional[str]
    kendala: Optional[str]
    catatan: Optional[str]
    durasi_menit: Optional[int]
    metode_belajar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# LAPORAN
# ═══════════════════════════════════════════════════════════════════════════════

class LaporanCreate(BaseModel):
    murid_id: str
    kelas_id: Optional[str] = None
    periode_mulai: Optional[date] = None
    periode_selesai: Optional[date] = None
    tipe_laporan: str = "perkembangan"


class LaporanUpdate(BaseModel):
    konten: Optional[str] = None
    status: Optional[str] = None   # draft | final | terkirim


class LaporanResponse(BaseModel):
    id: str
    murid_id: str
    kelas_id: Optional[str]
    konten: str
    tipe_laporan: str
    status: str
    pdf_path: Optional[str]
    tanggal: datetime
    tanggal_dikirim: Optional[datetime]
    is_ai_generated: bool
    periode_mulai: Optional[date]
    periode_selesai: Optional[date]

    class Config:
        from_attributes = True


class KirimLaporanRequest(BaseModel):
    email_tujuan: EmailStr
    catatan_tambahan: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# RENCANA STUDI
# ═══════════════════════════════════════════════════════════════════════════════

class RencanaStudiResponse(BaseModel):
    id: str
    kelas_id: str
    murid_id: Optional[str]
    waktu: datetime
    daftar_rekomendasi_materi: Optional[List[str]]
    estimasi_waktu_selesai: Optional[datetime]
    catatan_analisa: Optional[str]
    jadwal_mingguan: Optional[Dict[str, Any]]
    version: int

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════════════════════

class DiagnosticCreate(BaseModel):
    murid_id: str
    kelas_id: Optional[str] = None
    topik: str
    diagnostic_score: float = Field(..., ge=0, le=100)


class DiagnosticResponse(BaseModel):
    id: str
    murid_id: str
    topik: str
    diagnostic_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# UPLOAD / BULK
# ═══════════════════════════════════════════════════════════════════════════════

class BulkUploadResponse(BaseModel):
    total_baris: int
    berhasil: int
    gagal: int
    detail_error: List[Dict[str, Any]] = []


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardSummary(BaseModel):
    total_siswa: int
    log_hari_ini: int
    plan_aktif: int
    report_pending: int
    aktivitas_terbaru: List[Dict[str, Any]]
    progress_siswa: List[Dict[str, Any]]
