"""
models.py
SQLAlchemy ORM Models — Sesuai dengan spesifikasi sistem manajemen pembelajaran adaptif.
Mengatur data pengguna, manajemen kelas, skill graph (Topik), log harian, 
hingga output engine AI (BKT untuk Knowledge State & PSO untuk Rencana Studi).
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
    Tabel induk kredensial semua pengguna sistem.
    tipe_pengguna: 'pengajar' | 'admin' | 'murid' (jika akses murid diberikan).
    """
    __tablename__ = "pengguna"

    id              = Column(String(50), primary_key=True, default=_uuid)
    username        = Column(String(100), unique=True, nullable=False)
    email_address   = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    tipe_pengguna   = Column(String(20), nullable=False)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    # Relasi polimorfik ke profil spesifik
    pengajar = relationship("Pengajar", back_populates="pengguna", uselist=False)


class Pengajar(Base):
    """
    Profil tambahan untuk pengguna bertipe pengajar.
    Menghubungkan akun pengguna dengan kelas-kelas yang diampu.
    """
    __tablename__ = "pengajar"
    id = Column(String(50), ForeignKey("pengguna.id", ondelete="CASCADE"), primary_key=True)

    pengguna = relationship("Pengguna", back_populates="pengajar")
    kelas_diampu = relationship("Kelas", back_populates="pengajar")


class Murid(Base):
    """
    Data profil siswa, termasuk informasi demografis dan level pendidikan.
    Menjadi pusat data untuk analisis perkembangan belajar (Knowledge State & Report).
    """
    __tablename__ = "murid"
    id            = Column(String(50), primary_key=True, default=_uuid)
    email_address = Column(String(100), unique=True, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    nama          = Column(String(150))
    education_level = Column(String(10))   # Contoh: SD, SMP, SMA
    jenis_kelamin   = Column(String(10))
    diagnostic_level = Column(String(50))  # Level awal berdasarkan F008
    is_active       = Column(Boolean, default=True)

    # Relasi balik
    kelas              = relationship("KelasMurid", back_populates="murid")
    laporan            = relationship("Laporan", back_populates="murid")
    knowledge_states   = relationship("KnowledgeState", back_populates="murid")
    diagnostic_results = relationship("DiagnosticResult", back_populates="murid")

# ═══════════════════════════════════════════════════════════════════════════════
# MATA PELAJARAN & TOPIK
# ═══════════════════════════════════════════════════════════════════════════════

class MataPelajaran(Base):
    """
    Master data mata pelajaran.
    Menyimpan informasi umum seperti bobot kredit dan jadwal default.
    """
    __tablename__ = "mata_pelajaran"
 
    id                  = Column(String(50),  primary_key=True, default=_uuid)
    nama_mata_pelajaran = Column(String(150), nullable=False)
    kredit              = Column(Integer,     nullable=False, default=0)
    hari                = Column(String(10),  nullable=True)
    jam                 = Column(String(5),   nullable=True)  
    created_at          = Column(DateTime,    default=datetime.utcnow,  nullable=False)
    updated_at          = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    kelas_list = relationship("Kelas", back_populates="mata_pelajaran_obj")
    topik_list = relationship("Topik", back_populates="mata_pelajaran", cascade="all, delete-orphan")


class TopikPrasyarat(Base):
    """
    Tabel pivot (Self-Referential) untuk menyimpan relasi prasyarat antar topik.
    Struktur ini membangun 'Skill Graph' yang digunakan oleh PSO Planner 
    untuk menentukan urutan materi yang logis.
    """
    __tablename__ = "topik_prasyarat"
    topik_id     = Column(String(50), ForeignKey("topik.id", ondelete="CASCADE"), primary_key=True)
    prasyarat_id = Column(String(50), ForeignKey("topik.id", ondelete="CASCADE"), primary_key=True)


class Topik(Base):
    """
    Data master topik atau materi belajar.
    difficulty_index: Digunakan oleh PSO untuk menghitung beban belajar.
    Relasi prasyarat memungkinkan pembentukan graf ketergantungan materi.
    """
    __tablename__ = "topik"

    id                = Column(String(50), primary_key=True, default=_uuid)
    mata_pelajaran_id = Column(String(50), ForeignKey("mata_pelajaran.id", ondelete="CASCADE"), nullable=False)
    nama              = Column(String(150), nullable=False)
    difficulty_index  = Column(Float, default=0.5) # Skala 0.0 - 1.0
    created_at        = Column(DateTime, default=datetime.utcnow)

    mata_pelajaran = relationship("MataPelajaran", back_populates="topik_list")

    # Relasi ke prasyarat (Many-to-Many Self-Reference)
    prasyarat = relationship(
        "Topik",
        secondary="topik_prasyarat",
        primaryjoin="Topik.id == TopikPrasyarat.topik_id",
        secondaryjoin="Topik.id == TopikPrasyarat.prasyarat_id",
        backref="lanjutan_dari"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# KELAS & MANAJEMEN SISWA
# ═══════════════════════════════════════════════════════════════════════════════

class Kelas(Base):
    """
    Entitas kelas aktif yang menghubungkan Mata Pelajaran, Pengajar, dan Murid.
    Menyimpan detail operasional seperti jadwal pertemuan.
    """
    __tablename__ = "kelas"

    id           = Column(String(50), primary_key=True, default=_uuid)
    nama         = Column(String(100), nullable=False, unique=True)
    mata_pelajaran_id = Column(String(50), ForeignKey("mata_pelajaran.id", ondelete="SET NULL"), nullable=True) 
    pengajar_id  = Column(String(50), ForeignKey("pengajar.id", ondelete="SET NULL"), nullable=True)
    kredit       = Column(Integer, default=0)
    hari         = Column(String(10),  nullable=False)
    jam          = Column(String(5),   nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    pengajar           = relationship("Pengajar", back_populates="kelas_diampu")
    mata_pelajaran_obj = relationship("MataPelajaran", back_populates="kelas_list")
    murid_list         = relationship("KelasMurid", back_populates="kelas")
    log_pertemuan      = relationship("LogPertemuan", back_populates="kelas")
    rencana_studi      = relationship("RencanaStudi", back_populates="kelas")


class KelasMurid(Base):
    """
    Tabel pivot many-to-many antara Kelas dan Murid.
    Mencatat kapan seorang murid bergabung ke dalam kelas tertentu.
    """
    __tablename__ = "kelas_murid"
    __table_args__ = (UniqueConstraint("kelas_id", "murid_id"),)

    kelas_id = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"), primary_key=True)
    murid_id = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    kelas = relationship("Kelas", back_populates="murid_list")
    murid = relationship("Murid", back_populates="kelas")

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING & ANALISIS AI
# ═══════════════════════════════════════════════════════════════════════════════

class LogPertemuan(Base):
    """
    F001 & F002 — Catatan aktivitas harian per siswa di kelas.
    Data ini adalah input utama untuk BKT Engine (nilai/tingkat pemahaman)
    dan Narrative Engine (catatan/kendala).
    """
    __tablename__ = "log_pertemuan"

    id                   = Column(String(50), primary_key=True, default=_uuid)
    kelas_id             = Column(String(50), ForeignKey("kelas.id",  ondelete="CASCADE"))
    murid_id             = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"))
    tanggal              = Column(Date, nullable=False)
    topik                = Column(String(255), nullable=False)
    nilai                = Column(Numeric(5, 2))
    tingkat_pemahaman    = Column(String(50))   # 'sangat_paham' | 'paham' | dsb
    tingkat_keterlibatan = Column(String(50))
    kompetensi_dicapai   = Column(Text)
    target_materi_berikutnya = Column(Text)
    kendala              = Column(Text)
    catatan              = Column(Text)
    durasi_menit         = Column(Integer)
    metode_belajar       = Column(String(100))
    created_at           = Column(DateTime, default=datetime.utcnow)

    kelas = relationship("Kelas", back_populates="log_pertemuan")
    murid = relationship("Murid")


class DraftAnalisis(Base):
    """
    Output dari NarrativeEngine (LLM).
    Berisi narasi rangkuman perkembangan siswa berdasarkan akumulasi LogPertemuan.
    Menjadi dasar tekstual bagi Planner untuk menyusun Rencana Studi.
    """
    __tablename__ = "draft_analisis"
    id        = Column(String(50), primary_key=True, default=_uuid)
    kelas_id  = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"))
    murid_id  = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    konten    = Column(Text, nullable=False) # Teks narasi AI
    tanggal   = Column(DateTime, default=datetime.utcnow)

    rencana_studi = relationship("RencanaStudi", back_populates="draft_analisis")


class RencanaStudi(Base):
    """
    F004 — Dokumen rencana belajar adaptif (hasil PlannerEngine).
    Mengintegrasikan daftar materi (hasil PSO) dan jadwal optimal.
    is_outdated: Menandai jika rencana perlu di-generate ulang karena ada log baru.
    """
    __tablename__ = "rencana_studi"
    id = Column(String(50), primary_key=True, default=_uuid)
    kelas_id = Column(String(50), ForeignKey("kelas.id"))
    murid_id = Column(String(50), ForeignKey("murid.id"))
    draft_analisis_id = Column(String(50), ForeignKey("draft_analisis.id"))
    daftar_rekomendasi_materi = Column(JSON, default=list) # List urutan topik hasil PSO
    jadwal_mingguan = Column(JSON, default=dict)
    catatan_analisa = Column(Text)
    estimasi_waktu_selesai = Column(DateTime)
    version = Column(Integer, default=1)
    waktu = Column(DateTime, default=datetime.utcnow)
    is_outdated = Column(Boolean, default=False)

    kelas         = relationship("Kelas", back_populates="rencana_studi")
    draft_analisis = relationship("DraftAnalisis", back_populates="rencana_studi")

# ═══════════════════════════════════════════════════════════════════════════════
# REPORTING & ENGINE STATE
# ═══════════════════════════════════════════════════════════════════════════════

class Laporan(Base):
    """
    F003, F005-F007 — Output laporan akhir untuk wali murid/admin.
    Berisi narasi final, status pengiriman, dan periode laporan.
    """
    __tablename__ = "laporan"
    id              = Column(String(50), primary_key=True, default=_uuid)
    murid_id        = Column(String(50), ForeignKey("murid.id",  ondelete="CASCADE"))
    kelas_id        = Column(String(50), ForeignKey("kelas.id",  ondelete="CASCADE"), nullable=True)
    konten          = Column(Text, nullable=False)
    tipe_laporan    = Column(String(50), default="perkembangan")
    status          = Column(String(20), default="draft") # draft | final | terkirim
    pdf_path        = Column(String(255), nullable=True)
    tanggal         = Column(DateTime, default=datetime.utcnow)
    tanggal_dikirim = Column(DateTime, nullable=True)
    is_ai_generated = Column(Boolean, default=True)
    periode_mulai   = Column(Date, nullable=True)
    periode_selesai = Column(Date, nullable=True)

    murid = relationship("Murid", back_populates="laporan")


class KnowledgeState(Base):
    """
    Parameter Bayesian Knowledge Tracing (BKT) per siswa per topik.
    p_knowledge (Ln): Probabilitas siswa telah menguasai materi saat ini.
    Data ini diupdate setiap kali ada LogPertemuan baru.
    """
    __tablename__ = "knowledge_state"
    id          = Column(String(50), primary_key=True, default=_uuid)
    murid_id    = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    topik       = Column(String(255), nullable=False)
    p_knowledge = Column(Float, default=0.0) # P(Ln)
    p_learn     = Column(Float, default=0.2) # P(T)
    p_guess     = Column(Float, default=0.1) # P(G)
    p_slip      = Column(Float, default=0.05)# P(S)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    murid = relationship("Murid", back_populates="knowledge_states")


class DiagnosticResult(Base):
    """
    F008 — Hasil observasi atau tes awal siswa.
    skor/diagnostic_score: Digunakan sebagai prior (L0) dalam kalkulasi BKT
    agar sistem tidak mulai dari nol (cold start problem).
    """
    __tablename__ = "diagnostic_result"
    id               = Column(String(50), primary_key=True, default=_uuid)
    murid_id         = Column(String(50), ForeignKey("murid.id", ondelete="CASCADE"))
    kelas_id         = Column(String(50), ForeignKey("kelas.id", ondelete="CASCADE"), nullable=True)
    topik            = Column(String(255))
    skor             = Column(Float)
    diagnostic_score = Column(Float) # Skala 0-100
    sequence_number  = Column(Integer, default=1)
    model_ai         = Column(String(100), nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    murid = relationship("Murid", back_populates="diagnostic_results")