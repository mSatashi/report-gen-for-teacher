"""
models.py
SQLAlchemy ORM Models — sesuai ERD dan struktur AI-Driven Personalized Learning.
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
# 1. USER & ROLES
# ═══════════════════════════════════════════════════════════════════════════════
class Pengguna(Base):
    __tablename__ = "pengguna"
    id              = Column(String(50), primary_key=True, default=_uuid)
    username        = Column(String(100), unique=True, nullable=False)
    email_address   = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    tipe_pengguna   = Column(String(20), nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    pengajar = relationship("Pengajar", back_populates="pengguna", uselist=False)

class Pengajar(Base):
    __tablename__ = "pengajar"
    id = Column(String(50), ForeignKey("pengguna.id", ondelete="CASCADE"), primary_key=True)
    
    pengguna = relationship("Pengguna", back_populates="pengajar")
    kelas_diampu = relationship("Kelas", back_populates="pengajar")

class Murid(Base):
    __tablename__ = "murid"
    id               = Column(String(50), primary_key=True, default=_uuid)
    email_address    = Column(String(100), unique=True, nullable=False)
    nama             = Column(String(150))
    education_level  = Column(String(50))
    jenis_kelamin    = Column(String(20))
    diagnostic_level = Column(String(50))
    is_active        = Column(Boolean, default=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    kelas              = relationship("KelasMurid", back_populates="murid")
    laporan            = relationship("Laporan", back_populates="murid")
    knowledge_states   = relationship("KnowledgeState", back_populates="murid")
    diagnostic_results = relationship("DiagnosticResult", back_populates="murid")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. AKADEMIK (Mata Pelajaran & Skill Graph Topik)
# ═══════════════════════════════════════════════════════════════════════════════
class MataPelajaran(Base):
    __tablename__ = "mata_pelajaran"
    id                  = Column(String(50), primary_key=True, default=_uuid)
    nama_mata_pelajaran = Column(String(150), nullable=False)
    kredit              = Column(Integer, nullable=False, default=0)
    hari                = Column(String(10))
    jam                 = Column(String(5))
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kelas_list = relationship("Kelas", back_populates="mata_pelajaran_obj")
    topik_list = relationship("Topik", back_populates="mata_pelajaran", cascade="all, delete-orphan")

class TopikPrasyarat(Base):
    __tablename__ = "topik_prasyarat"
    topik_id     = Column(String(50), ForeignKey("topik.id", ondelete="CASCADE"), primary_key=True)
    prasyarat_id = Column(String(50), ForeignKey("topik.id", ondelete="CASCADE"), primary_key=True)

class Topik(Base):
    __tablename__ = "topik"
    id                = Column(String(50), primary_key=True, default=_uuid)
    mata_pelajaran_id = Column(String(50), ForeignKey("mata_pelajaran.id", ondelete="CASCADE"), nullable=False)
    nama              = Column(String(150), nullable=False)
    difficulty_index  = Column(Float, default=0.5)
    created_at        = Column(DateTime, default=datetime.utcnow)

    mata_pelajaran = relationship("MataPelajaran", back_populates="topik_list")
    prasyarat = relationship(
        "Topik",
        secondary="topik_prasyarat",
        primaryjoin="Topik.id == TopikPrasyarat.topik_id",
        secondaryjoin="Topik.id == TopikPrasyarat.prasyarat_id",
        backref="lanjutan_dari"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. KELAS & ASSIGNMENT MURID
# ═══════════════════════════════════════════════════════════════════════════════
class Kelas(Base):
    __tablename__ = "kelas"
    id                = Column(String(50), primary_key=True, default=_uuid)
    nama              = Column(String(100), nullable=False, unique=True)
    mata_pelajaran_id = Column(String(50), ForeignKey("mata_pelajaran.id", ondelete="SET NULL")) 
    pengajar_id       = Column(String(50), ForeignKey("pengajar.id", ondelete="SET NULL"))
    hari              = Column(String(10), nullable=False)
    jam               = Column(String(5), nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)

    pengajar           = relationship("Pengajar", back_populates="kelas_diampu")
    mata_pelajaran_obj = relationship("MataPelajaran", back_populates="kelas_list")
    murid_list         = relationship("KelasMurid", back_populates="kelas")
    log_pertemuan      = relationship("LogPertemuan", back_populates="kelas")
    rencana_studi      = relationship("RencanaStudi", back_populates="kelas")

class KelasMurid(Base):
    __tablename__ = "kelas_murid"
    __table_args__ = (UniqueConstraint("kelas_id", "murid_id"),)
    kelas_id  = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"), primary_key=True)
    murid_id  = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    kelas = relationship("Kelas", back_populates="murid_list")
    murid = relationship("Murid", back_populates="kelas")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. LOG PERTEMUAN & AI BKT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
class LogPertemuan(Base):
    __tablename__ = "log_pertemuan"
    id                       = Column(String(50), primary_key=True, default=_uuid)
    kelas_id                 = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"), nullable=False)
    murid_id                 = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"), nullable=False)
    tanggal                  = Column(Date, nullable=False)
    topik                    = Column(String(255), nullable=False)
    nilai                    = Column(Numeric(5, 2))
    tingkat_pemahaman        = Column(String(50))
    tingkat_keterlibatan     = Column(String(50))
    kompetensi_dicapai       = Column(Text)
    target_materi_berikutnya = Column(Text)
    kendala                  = Column(Text)
    catatan                  = Column(Text)
    durasi_menit             = Column(Integer)
    metode_belajar           = Column(String(100))
    created_at               = Column(DateTime, default=datetime.utcnow)

    kelas = relationship("Kelas", back_populates="log_pertemuan")
    murid = relationship("Murid")

class KnowledgeState(Base):
    __tablename__ = "knowledge_state"
    id          = Column(String(50), primary_key=True, default=_uuid)
    murid_id    = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"), nullable=False)
    topik       = Column(String(255), nullable=False)
    p_knowledge = Column(Float, nullable=False, default=0.2)
    p_learn     = Column(Float, nullable=False, default=0.15)
    p_guess     = Column(Float, nullable=False, default=0.1)
    p_slip      = Column(Float, nullable=False, default=0.05)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    murid = relationship("Murid", back_populates="knowledge_states")

class DiagnosticResult(Base):
    __tablename__ = "diagnostic_result"
    id               = Column(String(50), primary_key=True, default=_uuid)
    murid_id         = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"), nullable=False)
    kelas_id         = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    topik            = Column(String(255))
    skor             = Column(Float)
    diagnostic_score = Column(Float)
    created_at       = Column(DateTime, default=datetime.utcnow)

    murid = relationship("Murid", back_populates="diagnostic_results")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. AI PLANNER (PSO) & LAPORAN (LLM)
# ═══════════════════════════════════════════════════════════════════════════════
class DraftAnalisis(Base):
    __tablename__ = "draft_analisis"
    id       = Column(String(50), primary_key=True, default=_uuid)
    kelas_id = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    murid_id = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    konten   = Column(Text, nullable=False)
    tanggal  = Column(DateTime, default=datetime.utcnow)

    rencana_studi = relationship("RencanaStudi", back_populates="draft_analisis")

class RencanaStudi(Base):
    __tablename__ = "rencana_studi"
    id                        = Column(String(50), primary_key=True, default=_uuid)
    kelas_id                  = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    murid_id                  = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"), nullable=True) # Null = Rencana Kelas
    draft_analisis_id         = Column(String(50), ForeignKey("draft_analisis.id", ondelete="SET NULL"))
    daftar_rekomendasi_materi = Column(JSON, default=list)
    jadwal_mingguan           = Column(JSON, default=dict)
    catatan_analisa           = Column(Text)
    estimasi_waktu_selesai    = Column(DateTime)
    is_outdated               = Column(Boolean, default=False)
    version                   = Column(Integer, nullable=False, default=1)
    waktu                     = Column(DateTime, default=datetime.utcnow)

    kelas          = relationship("Kelas", back_populates="rencana_studi")
    draft_analisis = relationship("DraftAnalisis", back_populates="rencana_studi")

class Laporan(Base):
    __tablename__ = "laporan"
    id              = Column(String(50), primary_key=True, default=_uuid)
    murid_id        = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"), nullable=False)
    kelas_id        = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    konten          = Column(Text, nullable=False)
    tipe_laporan    = Column(String(50), default="perkembangan")
    status          = Column(String(20), default="draft")
    pdf_path        = Column(String(255))
    tanggal         = Column(DateTime, default=datetime.utcnow)
    tanggal_dikirim = Column(DateTime)
    is_ai_generated = Column(Boolean, default=True)
    periode_mulai   = Column(Date)
    periode_selesai = Column(Date)

    murid = relationship("Murid", back_populates="laporan")