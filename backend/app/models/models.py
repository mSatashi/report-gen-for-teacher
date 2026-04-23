"""
models.py
SQLAlchemy ORM Models — sesuai ERD pada laporan desain sistem.
Tabel: pengguna, murid, pengajar, kelas, kelas_murid,
       log_pertemuan, draft_analisis, rencana_studi, laporan,
       knowledge_state, diagnostic_result, lesson_log, lesson_plan
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float,
    ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════════════════════
# USER & ROLES
# ═══════════════════════════════════════════════════════════════════════════════

class Pengguna(Base):
    """
    Tabel induk semua pengguna sistem.
    tipe_pengguna: 'pengajar' | 'admin'
    """
    __tablename__ = "pengguna"

    id              = Column(String(50), primary_key=True, default=_uuid)
    username        = Column(String(100), unique=True, nullable=False)
    email_address   = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    tipe_pengguna   = Column(String(20), nullable=False)   # 'pengajar' | 'murid'
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relasi polimorfik
    pengajar = relationship("Pengajar", back_populates="pengguna", uselist=False)


class Pengajar(Base):
    """Profil tambahan untuk pengguna bertipe pengajar."""
    __tablename__ = "pengajar"

    id = Column(String(50), ForeignKey("pengguna.id", ondelete="CASCADE"), primary_key=True)

    pengguna = relationship("Pengguna", back_populates="pengajar")
    kelas_diampu = relationship("Kelas", back_populates="pengajar")


class Murid(Base):
    __tablename__ = "murid"
    id            = Column(String(50), primary_key=True, default=_uuid)
    email_address = Column(String(100), unique=True, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    nama          = Column(String(150))
    education_level = Column(String(10))
    jenis_kelamin   = Column(String(10))
    diagnostic_level = Column(String(50))
    is_active       = Column(Boolean, default=True)

    kelas              = relationship("KelasMurid", back_populates="murid")
    laporan            = relationship("Laporan", back_populates="murid")
    knowledge_states   = relationship("KnowledgeState", back_populates="murid")
    diagnostic_results = relationship("DiagnosticResult", back_populates="murid")

# ═══════════════════════════════════════════════════════════════════════════════
# Mata Pelajaran
# ═══════════════════════════════════════════════════════════════════════════════
class MataPelajaran(Base):
    __tablename__ = "mata_pelajaran"
 
    id                  = Column(String(50),  primary_key=True, default=_uuid)
    nama_mata_pelajaran = Column(String(150), nullable=False)
    topik               = Column(JSON,        nullable=False, default=list)  # list of string
    created_at          = Column(DateTime,    default=datetime.utcnow,  nullable=False)
    updated_at          = Column(DateTime,    default=datetime.utcnow,
                                              onupdate=datetime.utcnow, nullable=False)

    # Relasi balik — satu mata pelajaran bisa ada di banyak kelas
    kelas_list = relationship("Kelas", back_populates="mata_pelajaran_obj")


# ═══════════════════════════════════════════════════════════════════════════════
# KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class Kelas(Base):
    __tablename__ = "kelas"

    id           = Column(String(50), primary_key=True, default=_uuid)
    nama         = Column(String(100), nullable=False, unique=True)
    mata_pelajaran_id = Column(String(50), ForeignKey("mata_pelajaran.id", ondelete="SET NULL"), nullable=True) 
    pengajar_id  = Column(String(50), ForeignKey("pengajar.id", ondelete="SET NULL"), nullable=True)
    kredit       = Column(Integer, default=0)
    hari                = Column(String(10),  nullable=False)  # Senin–Minggu
    jam                 = Column(String(5),   nullable=False)  # HH:MM
    created_at   = Column(DateTime, default=datetime.utcnow)

    pengajar     = relationship("Pengajar", back_populates="kelas_diampu")
    mata_pelajaran_obj = relationship("MataPelajaran", back_populates="kelas_list")
    murid_list   = relationship("KelasMurid", back_populates="kelas")
    log_pertemuan = relationship("LogPertemuan", back_populates="kelas")
    rencana_studi = relationship("RencanaStudi", back_populates="kelas")


class KelasMurid(Base):
    """Tabel pivot kelas <-> murid (many-to-many)."""
    __tablename__ = "kelas_murid"
    __table_args__ = (UniqueConstraint("kelas_id", "murid_id"),)

    kelas_id = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"), primary_key=True)
    murid_id = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    kelas = relationship("Kelas", back_populates="murid_list")
    murid = relationship("Murid", back_populates="kelas")


# ═══════════════════════════════════════════════════════════════════════════════
# LOG PERTEMUAN (Daily Log)
# ═══════════════════════════════════════════════════════════════════════════════

class LogPertemuan(Base):
    """
    F001 & F002 — Input log harian (single form & bulk CSV/Excel).
    Menyimpan catatan tiap sesi belajar: topik, nilai, catatan guru.
    """
    __tablename__ = "log_pertemuan"

    id                   = Column(String(50), primary_key=True, default=_uuid)
    kelas_id             = Column(String(50), ForeignKey("kelas.id",  ondelete="CASCADE"))
    murid_id             = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"))
    tanggal              = Column(Date, nullable=False)
    topik                = Column(String(255), nullable=False)
    nilai                = Column(Numeric(5, 2))
    tingkat_pemahaman    = Column(String(50))   # 'sangat_paham' | 'paham' | 'cukup' | 'perlu_review'
    tingkat_keterlibatan = Column(String(50))   # 'sangat_aktif' | 'aktif' | 'kurang_fokus'
    kompetensi_dicapai   = Column(Text)
    target_materi_berikutnya = Column(Text)
    kendala              = Column(Text)
    catatan              = Column(Text)
    durasi_menit         = Column(Integer)
    metode_belajar       = Column(String(100))
    created_at           = Column(DateTime, default=datetime.utcnow)

    kelas = relationship("Kelas", back_populates="log_pertemuan")
    murid = relationship("Murid")


# ═══════════════════════════════════════════════════════════════════════════════
# AI — DRAFT ANALISIS
# ═══════════════════════════════════════════════════════════════════════════════

class DraftAnalisis(Base):
    """
    Hasil analisis data log pertemuan oleh NarrativeEngine LLM.
    Digunakan sebagai input untuk PlannerEngine.
    """
    __tablename__ = "draft_analisis"

    id        = Column(String(50), primary_key=True, default=_uuid)
    kelas_id  = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    murid_id  = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    konten    = Column(Text, nullable=False)
    tanggal   = Column(DateTime, default=datetime.utcnow)

    rencana_studi = relationship("RencanaStudi", back_populates="draft_analisis")


# ═══════════════════════════════════════════════════════════════════════════════
# RENCANA STUDI (Learning Plan)
# ═══════════════════════════════════════════════════════════════════════════════

class RencanaStudi(Base):
    """
    F004 — Rencana studi adaptif yang dihasilkan PlannerEngine (BKT + PSO).
    """
    __tablename__ = "rencana_studi"

    id                        = Column(String(50), primary_key=True, default=_uuid)
    kelas_id                  = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    murid_id                  = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    draft_analisis_id         = Column(String(50), ForeignKey("draft_analisis.id", ondelete="SET NULL"), nullable=True)
    waktu                     = Column(DateTime, default=datetime.utcnow)
    daftar_rekomendasi_materi = Column(JSON)       # list of strings
    estimasi_waktu_selesai    = Column(DateTime,   nullable=True)
    catatan_analisa           = Column(Text)
    jadwal_mingguan           = Column(JSON)       # JSON jadwal per hari
    version                   = Column(Integer, default=1)

    kelas         = relationship("Kelas", back_populates="rencana_studi")
    draft_analisis = relationship("DraftAnalisis", back_populates="rencana_studi")


# ═══════════════════════════════════════════════════════════════════════════════
# LAPORAN (Report)
# ═══════════════════════════════════════════════════════════════════════════════

class Laporan(Base):
    """
    F003, F005, F006, F007 — Laporan perkembangan siswa.
    Status: 'draft' | 'final' | 'terkirim'
    """
    __tablename__ = "laporan"

    id              = Column(String(50), primary_key=True, default=_uuid)
    murid_id        = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"))
    kelas_id        = Column(String(50), ForeignKey("kelas.id",  ondelete="CASCADE"), nullable=True)
    konten          = Column(Text, nullable=False)   # narasi deskriptif dari LLM
    tipe_laporan    = Column(String(50), default="perkembangan")
    status          = Column(String(20), default="draft")   # draft | final | terkirim
    pdf_path        = Column(String(255), nullable=True)
    tanggal         = Column(DateTime, default=datetime.utcnow)
    tanggal_dikirim = Column(DateTime, nullable=True)
    is_ai_generated = Column(Boolean, default=True)
    periode_mulai   = Column(Date, nullable=True)
    periode_selesai = Column(Date, nullable=True)

    murid = relationship("Murid", back_populates="laporan")


# ═══════════════════════════════════════════════════════════════════════════════
# BKT — KNOWLEDGE STATE
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeState(Base):
    """
    Menyimpan probabilitas penguasaan materi siswa per topik (output BKT).
    p_knowledge: P(Ln) — probabilitas siswa menguasai topik ini sekarang.
    """
    __tablename__ = "knowledge_state"

    id          = Column(String(50), primary_key=True, default=_uuid)
    murid_id    = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    topik       = Column(String(255), nullable=False)
    p_knowledge = Column(Float, default=0.0)   # 0.0 – 1.0
    p_learn     = Column(Float, default=0.2)
    p_guess     = Column(Float, default=0.1)
    p_slip      = Column(Float, default=0.05)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    murid = relationship("Murid", back_populates="knowledge_states")


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC RESULT (F008)
# ═══════════════════════════════════════════════════════════════════════════════

class DiagnosticResult(Base):
    """
    F008 — Hasil tes diagnostik awal siswa (pertemuan pertama).
    Digunakan sebagai P(L0) awal untuk BKT.
    """
    __tablename__ = "diagnostic_result"

    id               = Column(String(50), primary_key=True, default=_uuid)
    murid_id         = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    kelas_id         = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"), nullable=True)
    topik            = Column(String(255))
    skor             = Column(Float)
    diagnostic_score = Column(Float)   # nilai 0–100 dari tes diagnostik
    sequence_number  = Column(Integer, default=1)
    model_ai         = Column(String(100), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    murid = relationship("Murid", back_populates="diagnostic_results")
