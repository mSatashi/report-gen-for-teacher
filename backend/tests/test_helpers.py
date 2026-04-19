import uuid
from datetime import date, datetime
from unittest.mock import MagicMock
 
 
# ─────────────────────────────────────────────────────────────────────────────
# PRIMITIVES
# ─────────────────────────────────────────────────────────────────────────────
 
def fake_id() -> str:
    """Hasilkan UUID string unik — dipakai sebagai ID palsu di semua test."""
    return str(uuid.uuid4())
 
 
# ─────────────────────────────────────────────────────────────────────────────
# FAKE ORM OBJECTS
# ─────────────────────────────────────────────────────────────────────────────
 
def fake_pengguna(
    tipe: str = "pengajar",
    is_active: bool = True,
    username: str = "fake-pengguna",
    email: str = "fake-pengguna@email.com",
    uid: str = None,
) -> MagicMock:
    """
    Mock objek Pengguna ORM.
    Prefix 'fake-' pada semua string untuk membedakan dari data nyata.
    """
    obj = MagicMock()
    obj.id              = uid or fake_id()
    obj.username        = username
    obj.email_address   = email
    obj.hashed_password = "$2b$12$fake-hashed-password-tidak-nyata"
    obj.tipe_pengguna   = tipe
    obj.is_active       = is_active
    obj.created_at      = datetime(2025, 1, 1, 0, 0, 0)
    return obj
 
 
def fake_pengajar(uid: str = None) -> MagicMock:
    """Mock objek Pengajar ORM (profil pengajar)."""
    obj = MagicMock()
    obj.id = uid or fake_id()
    return obj
 
 
def fake_murid(
    nama: str = "Fake Nama Murid",
    usia: int = 15,
    level: str = "SMA",
    credit_total: int = 10,
    credit_used: int = 0,
    uid: str = None,
) -> MagicMock:
    """
    Mock objek Murid ORM.
    Nama selalu diawali 'Fake ' untuk menandai data test.
    """
    obj = MagicMock()
    obj.id               = uid or fake_id()
    obj.nama             = nama
    obj.usia             = usia
    obj.level            = level
    obj.credit_total     = credit_total
    obj.credit_used      = credit_used
    obj.diagnostic_level = None
    return obj
 
 
def fake_kelas(
    nama: str = "Fake Kelas Matematika",
    mata_pelajaran: str = "Matematika",
    kredit: int = 3,
    jadwal: str = "Senin 08:00",
    pengajar_id: str = None,
    uid: str = None,
) -> MagicMock:
    """Mock objek Kelas ORM."""
    obj = MagicMock()
    obj.id             = uid or fake_id()
    obj.nama           = nama
    obj.mata_pelajaran = mata_pelajaran
    obj.kredit         = kredit
    obj.jadwal         = jadwal
    obj.pengajar_id    = pengajar_id or fake_id()
    obj.created_at     = datetime(2025, 1, 1, 0, 0, 0)
    return obj
 
 
def fake_kelas_murid(
    kelas_id: str = None,
    murid_id: str = None,
) -> MagicMock:
    """Mock objek KelasMurid ORM (tabel pivot many-to-many)."""
    obj = MagicMock()
    obj.kelas_id  = kelas_id or fake_id()
    obj.murid_id  = murid_id or fake_id()
    obj.joined_at = datetime(2025, 1, 1, 0, 0, 0)
    return obj
 
 
def fake_log(
    kelas_id: str = None,
    murid_id: str = None,
    topik: str = "Fake Topik Pelajaran",
    nilai: float = 80.0,
    uid: str = None,
) -> MagicMock:
    """Mock objek LogPertemuan ORM."""
    obj = MagicMock()
    obj.id                       = uid or fake_id()
    obj.kelas_id                 = kelas_id or fake_id()
    obj.murid_id                 = murid_id
    obj.tanggal                  = date(2025, 3, 10)
    obj.topik                    = topik
    obj.nilai                    = nilai
    obj.tingkat_pemahaman        = "paham"
    obj.tingkat_keterlibatan     = "aktif"
    obj.kompetensi_dicapai       = "Fake kompetensi yang dicapai"
    obj.target_materi_berikutnya = "Fake materi berikutnya"
    obj.kendala                  = None
    obj.catatan                  = "Fake catatan guru"
    obj.durasi_menit             = 90
    obj.metode_belajar           = "Diskusi"
    obj.created_at               = datetime(2025, 3, 10, 8, 0, 0)
    return obj
 
 
def fake_laporan(
    murid_id: str = None,
    kelas_id: str = None,
    status: str = "draft",
    uid: str = None,
) -> MagicMock:
    """Mock objek Laporan ORM."""
    obj = MagicMock()
    obj.id              = uid or fake_id()
    obj.murid_id        = murid_id or fake_id()
    obj.kelas_id        = kelas_id or fake_id()
    obj.konten          = "Fake konten laporan perkembangan siswa dari AI."
    obj.tipe_laporan    = "perkembangan"
    obj.status          = status
    obj.pdf_path        = None
    obj.tanggal         = datetime(2025, 1, 15, 0, 0, 0)
    obj.tanggal_dikirim = None
    obj.is_ai_generated = True
    obj.periode_mulai   = date(2025, 1, 1)
    obj.periode_selesai = date(2025, 1, 31)
    return obj
 
 
def fake_diagnostic(
    murid_id: str = None,
    kelas_id: str = None,
    topik: str = "Fake Topik Diagnostik",
    skor: float = 75.0,
    uid: str = None,
) -> MagicMock:
    """Mock objek DiagnosticResult ORM."""
    obj = MagicMock()
    obj.id               = uid or fake_id()
    obj.murid_id         = murid_id or fake_id()
    obj.kelas_id         = kelas_id
    obj.topik            = topik
    obj.skor             = skor
    obj.diagnostic_score = skor
    obj.sequence_number  = 1
    obj.model_ai         = None
    obj.created_at       = datetime(2025, 2, 1, 0, 0, 0)
    return obj
 
 
def fake_knowledge_state(
    murid_id: str = None,
    topik: str = "Fake Topik BKT",
    p_knowledge: float = 0.5,
    uid: str = None,
) -> MagicMock:
    """Mock objek KnowledgeState ORM (BKT state)."""
    obj = MagicMock()
    obj.id          = uid or fake_id()
    obj.murid_id    = murid_id or fake_id()
    obj.topik       = topik
    obj.p_knowledge = p_knowledge
    obj.p_learn     = 0.2
    obj.p_guess     = 0.1
    obj.p_slip      = 0.05
    obj.updated_at  = datetime(2025, 3, 1, 0, 0, 0)
    return obj
 
 
def fake_rencana_studi(
    kelas_id: str = None,
    murid_id: str = None,
    uid: str = None,
) -> MagicMock:
    """Mock objek RencanaStudi ORM."""
    obj = MagicMock()
    obj.id                        = uid or fake_id()
    obj.kelas_id                  = kelas_id or fake_id()
    obj.murid_id                  = murid_id
    obj.draft_analisis_id         = None
    obj.waktu                     = datetime(2025, 3, 15, 0, 0, 0)
    obj.daftar_rekomendasi_materi = ["Fake Materi A", "Fake Materi B"]
    obj.estimasi_waktu_selesai    = None
    obj.catatan_analisa           = "Fake catatan analisa rencana studi."
    obj.jadwal_mingguan           = {"Senin": "Fake Materi A", "Rabu": "Fake Materi B"}
    obj.version                   = 1
    return obj
 
 
# ─────────────────────────────────────────────────────────────────────────────
# MOCK DATABASE SESSION
# ─────────────────────────────────────────────────────────────────────────────
 
def mock_db() -> MagicMock:
    """
    Mock SQLAlchemy Session standar.
    Mendukung pola: db.query(...).filter(...).first() / .all()
    Semua chaining method mengembalikan db itu sendiri.
    """
    db = MagicMock()
    db.query.return_value  = db
    db.filter.return_value = db
    db.first.return_value  = None
    db.all.return_value    = []
    db.add    = MagicMock()
    db.commit = MagicMock()
    db.delete = MagicMock()
    db.refresh = MagicMock()
    return db
 
 
def mock_db_chained() -> MagicMock:
    """
    Mock SQLAlchemy Session dengan chaining method lebih lengkap.
    Cocok untuk query dengan order_by, offset, limit, in_, join, distinct, dll.
    """
    db = MagicMock()
    db.query.return_value    = db
    db.filter.return_value   = db
    db.order_by.return_value = db
    db.offset.return_value   = db
    db.limit.return_value    = db
    db.join.return_value     = db
    db.in_.return_value      = db
    db.distinct.return_value = db
    db.group_by.return_value = db
    db.isnot.return_value    = db
    db.ilike.return_value    = db
    db.first.return_value    = None
    db.all.return_value      = []
    db.count.return_value    = 0
    db.add    = MagicMock()
    db.commit = MagicMock()
    db.delete = MagicMock()
    db.refresh = MagicMock()
    return db
 