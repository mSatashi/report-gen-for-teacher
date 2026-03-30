"""
test_dashboard.py
Unit testing untuk fitur Dashboard.
Pakai SQLite in-memory — tidak perlu PostgreSQL.

Cara jalankan:
    pytest tests/test_dashboard.py -v

Jalankan semua test sekaligus:
    pytest tests/ -v
"""
import os
import uuid
import pytest
from datetime import date, datetime

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_dashboard.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_dashboard.db"

engine_test = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Buat semua tabel di SQLite sebelum test."""
    import app.core.database as db_module
    db_module.engine       = engine_test
    db_module.SessionLocal = TestingSessionLocal
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    engine_test.dispose()
    try:
        if os.path.exists("./test_dashboard.db"):
            os.remove("./test_dashboard.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    """Bersihkan semua data sebelum tiap test."""
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import (
            LogPertemuan, Laporan, RencanaStudi, KelasMusrid,
            Kelas, Murid, Pengajar, Pengguna,
        )
        db.query(LogPertemuan).delete()
        db.query(Laporan).delete()
        db.query(RencanaStudi).delete()
        db.query(KelasMusrid).delete()
        db.query(Kelas).delete()
        db.query(Murid).delete()
        db.query(Pengajar).delete()
        db.query(Pengguna).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    """FastAPI test client pakai SQLite."""
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helper functions ──────────────────────────────────────────────────────────

def buat_pengajar(db, nama="Guru Test", email="guru@test.com"):
    """Buat data pengajar langsung di DB, kembalikan objek Pengguna."""
    from app.models.models import Pengguna, Pengajar
    from app.core.security import hash_password

    uid = str(uuid.uuid4())
    pengguna = Pengguna(
        id=uid,
        username=nama.replace(" ", "_").lower(),
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="pengajar",
    )
    db.add(pengguna)
    db.add(Pengajar(id=uid))
    db.commit()
    db.refresh(pengguna)
    return pengguna


def buat_murid(db, nama="Murid Test", email="murid@test.com"):
    """Buat data murid langsung di DB, kembalikan objek Murid."""
    from app.models.models import Pengguna, Murid
    from app.core.security import hash_password

    uid = str(uuid.uuid4())
    pengguna = Pengguna(
        id=uid,
        username=nama.replace(" ", "_").lower(),
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="murid",
    )
    murid = Murid(id=uid, nama=nama)
    db.add(pengguna)
    db.add(murid)
    db.commit()
    db.refresh(murid)
    return murid


def buat_kelas(db, pengajar_id, nama="Kelas Test", mata_pelajaran="Matematika"):
    """Buat data kelas langsung di DB."""
    from app.models.models import Kelas

    kelas = Kelas(
        id=str(uuid.uuid4()),
        nama=nama,
        mata_pelajaran=mata_pelajaran,
        pengajar_id=pengajar_id,
        kredit=20,
    )
    db.add(kelas)
    db.commit()
    db.refresh(kelas)
    return kelas


def daftarkan_murid(db, kelas_id, murid_id):
    """Daftarkan murid ke kelas."""
    from app.models.models import KelasMusrid

    km = KelasMusrid(kelas_id=kelas_id, murid_id=murid_id)
    db.add(km)
    db.commit()


def buat_log(db, kelas_id, murid_id=None, topik="Aljabar", nilai=80.0, tanggal=None):
    """Buat data log pertemuan langsung di DB."""
    from app.models.models import LogPertemuan

    log = LogPertemuan(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        tanggal=tanggal or date.today(),
        topik=topik,
        nilai=nilai,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def buat_laporan(db, murid_id, kelas_id, status="draft"):
    """Buat data laporan langsung di DB."""
    from app.models.models import Laporan

    lap = Laporan(
        id=str(uuid.uuid4()),
        murid_id=murid_id,
        kelas_id=kelas_id,
        konten="Isi laporan test",
        status=status,
        tanggal=datetime.utcnow(),
    )
    db.add(lap)
    db.commit()
    db.refresh(lap)
    return lap


def buat_rencana(db, kelas_id, murid_id=None):
    """Buat data rencana studi langsung di DB."""
    from app.models.models import RencanaStudi

    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        daftar_rekomendasi_materi=["Topik A", "Topik B"],
        catatan_analisa="Catatan test",
        waktu=datetime.utcnow(),
        version=1,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana


def get_token(client, email="guru@test.com", password="Test1234!"):
    """Login dan kembalikan JWT token."""
    resp = client.post("/api/v1/auth/login", json={
        "email_address": email,
        "password": password,
    })
    return resp.json().get("access_token", "")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════════
# TEST AKSES DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardAkses:

    def test_dashboard_tanpa_token_ditolak(self, client):
        """❌ Akses dashboard tanpa token harus ditolak."""
        response = client.get("/api/v1/dashboard/")
        assert response.status_code in (401, 403)

    def test_dashboard_token_palsu_ditolak(self, client):
        """❌ Akses dashboard dengan token palsu harus ditolak."""
        response = client.get(
            "/api/v1/dashboard/",
            headers={"Authorization": "Bearer token.palsu.banget"},
        )
        assert response.status_code == 401

    def test_dashboard_murid_tidak_bisa_akses(self, client):
        """❌ Murid tidak boleh mengakses dashboard pengajar."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_akses", email="murid_akses@test.com")
        db.close()

        token = get_token(client, "murid_akses@test.com")
        response = client.get("/api/v1/dashboard/", headers=auth_header(token))

        assert response.status_code == 403

    def test_dashboard_pengajar_bisa_akses(self, client):
        """✅ Pengajar bisa mengakses dashboard."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_akses", email="guru_akses@test.com")
        db.close()

        token = get_token(client, "guru_akses@test.com")
        response = client.get("/api/v1/dashboard/", headers=auth_header(token))

        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# TEST STRUKTUR RESPONSE DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardStruktur:

    def test_response_memiliki_semua_field(self, client):
        """✅ Response dashboard harus memiliki semua field yang dibutuhkan."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_field", email="guru_field@test.com")
        db.close()

        token = get_token(client, "guru_field@test.com")
        response = client.get("/api/v1/dashboard/", headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()

        # Cek semua field wajib ada
        assert "total_siswa" in data
        assert "log_hari_ini" in data
        assert "plan_aktif" in data
        assert "report_pending" in data
        assert "aktivitas_terbaru" in data
        assert "progress_siswa" in data

    def test_response_tipe_data_benar(self, client):
        """✅ Tipe data setiap field harus sesuai."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_tipe", email="guru_tipe@test.com")
        db.close()

        token = get_token(client, "guru_tipe@test.com")
        data = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert isinstance(data["total_siswa"], int)
        assert isinstance(data["log_hari_ini"], int)
        assert isinstance(data["plan_aktif"], int)
        assert isinstance(data["report_pending"], int)
        assert isinstance(data["aktivitas_terbaru"], list)
        assert isinstance(data["progress_siswa"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Kondisi Kosong
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardKosong:

    def test_dashboard_pengajar_baru_semua_nol(self, client):
        """✅ Pengajar baru tanpa data apapun, semua angka harus 0."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_baru", email="guru_baru@test.com")
        db.close()

        token = get_token(client, "guru_baru@test.com")
        data = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["total_siswa"]    == 0
        assert data["log_hari_ini"]   == 0
        assert data["plan_aktif"]     == 0
        assert data["report_pending"] == 0
        assert data["aktivitas_terbaru"] == []
        assert data["progress_siswa"]    == []

    def test_dashboard_pengajar_ada_kelas_tapi_belum_ada_murid(self, client):
        """✅ Pengajar punya kelas tapi belum ada murid, total_siswa harus 0."""
        db = TestingSessionLocal()
        guru = buat_pengajar(db, nama="guru_kelas", email="guru_kelas@test.com")
        buat_kelas(db, guru.id)
        db.close()

        token = get_token(client, "guru_kelas@test.com")
        data = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["total_siswa"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Hitung Total Siswa
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardTotalSiswa:

    def test_total_siswa_satu_kelas(self, client):
        """✅ Total siswa harus sesuai jumlah murid yang terdaftar di kelas."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_siswa1", email="guru_siswa1@test.com")
        kelas  = buat_kelas(db, guru.id)
        murid1 = buat_murid(db, nama="murid_a1", email="murid_a1@test.com")
        murid2 = buat_murid(db, nama="murid_b1", email="murid_b1@test.com")
        daftarkan_murid(db, kelas.id, murid1.id)
        daftarkan_murid(db, kelas.id, murid2.id)
        db.close()

        token = get_token(client, "guru_siswa1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["total_siswa"] == 2

    def test_total_siswa_dua_kelas_murid_berbeda(self, client):
        """✅ Murid di dua kelas berbeda dihitung semua."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_siswa2", email="guru_siswa2@test.com")
        kelas1 = buat_kelas(db, guru.id, nama="Kelas A")
        kelas2 = buat_kelas(db, guru.id, nama="Kelas B")
        murid1 = buat_murid(db, nama="murid_c1", email="murid_c1@test.com")
        murid2 = buat_murid(db, nama="murid_d1", email="murid_d1@test.com")
        murid3 = buat_murid(db, nama="murid_e1", email="murid_e1@test.com")
        daftarkan_murid(db, kelas1.id, murid1.id)
        daftarkan_murid(db, kelas1.id, murid2.id)
        daftarkan_murid(db, kelas2.id, murid3.id)
        db.close()

        token = get_token(client, "guru_siswa2@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["total_siswa"] == 3

    def test_total_siswa_tidak_terpengaruh_kelas_guru_lain(self, client):
        """✅ Murid di kelas guru lain tidak boleh ikut terhitung."""
        db = TestingSessionLocal()
        guru1  = buat_pengajar(db, nama="guru_x1", email="guru_x1@test.com")
        guru2  = buat_pengajar(db, nama="guru_y1", email="guru_y1@test.com")
        kelas1 = buat_kelas(db, guru1.id, nama="Kelas Guru1")
        kelas2 = buat_kelas(db, guru2.id, nama="Kelas Guru2")
        murid1 = buat_murid(db, nama="murid_f1", email="murid_f1@test.com")
        murid2 = buat_murid(db, nama="murid_g1", email="murid_g1@test.com")
        murid3 = buat_murid(db, nama="murid_h1", email="murid_h1@test.com")
        daftarkan_murid(db, kelas1.id, murid1.id)
        daftarkan_murid(db, kelas2.id, murid2.id)
        daftarkan_murid(db, kelas2.id, murid3.id)
        db.close()

        token = get_token(client, "guru_x1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        # Guru1 hanya punya 1 murid, tidak boleh lihat murid guru2
        assert data["total_siswa"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Log Hari Ini
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardLogHariIni:

    def test_log_hari_ini_terhitung(self, client):
        """✅ Log yang dibuat hari ini harus muncul di log_hari_ini."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_log1", email="guru_log1@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_log(db, kelas.id, topik="Topik Hari Ini", tanggal=date.today())
        buat_log(db, kelas.id, topik="Topik Hari Ini 2", tanggal=date.today())
        db.close()

        token = get_token(client, "guru_log1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["log_hari_ini"] == 2

    def test_log_kemarin_tidak_terhitung(self, client):
        """✅ Log kemarin tidak boleh masuk ke log_hari_ini."""
        from datetime import timedelta
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_log2", email="guru_log2@test.com")
        kelas = buat_kelas(db, guru.id)
        kemarin = date.today() - timedelta(days=1)
        buat_log(db, kelas.id, topik="Topik Kemarin", tanggal=kemarin)
        db.close()

        token = get_token(client, "guru_log2@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["log_hari_ini"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Report Pending
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardReportPending:

    def test_laporan_draft_masuk_pending(self, client):
        """✅ Laporan berstatus draft harus masuk ke report_pending."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_rpt1", email="guru_rpt1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_rpt1", email="murid_rpt1@test.com")
        buat_laporan(db, murid.id, kelas.id, status="draft")
        buat_laporan(db, murid.id, kelas.id, status="final")
        db.close()

        token = get_token(client, "guru_rpt1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["report_pending"] == 2

    def test_laporan_terkirim_tidak_masuk_pending(self, client):
        """✅ Laporan yang sudah terkirim tidak boleh masuk ke report_pending."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_rpt2", email="guru_rpt2@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_rpt2", email="murid_rpt2@test.com")
        buat_laporan(db, murid.id, kelas.id, status="terkirim")
        db.close()

        token = get_token(client, "guru_rpt2@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["report_pending"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Plan Aktif
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardPlanAktif:

    def test_rencana_studi_terhitung(self, client):
        """✅ Rencana studi yang ada harus terhitung di plan_aktif."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_plan1", email="guru_plan1@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_rencana(db, kelas.id)
        buat_rencana(db, kelas.id)
        db.close()

        token = get_token(client, "guru_plan1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["plan_aktif"] == 2

    def test_rencana_guru_lain_tidak_terhitung(self, client):
        """✅ Rencana studi milik guru lain tidak boleh ikut terhitung."""
        db = TestingSessionLocal()
        guru1  = buat_pengajar(db, nama="guru_plan2", email="guru_plan2@test.com")
        guru2  = buat_pengajar(db, nama="guru_plan3", email="guru_plan3@test.com")
        kelas1 = buat_kelas(db, guru1.id, nama="Kelas Plan1")
        kelas2 = buat_kelas(db, guru2.id, nama="Kelas Plan2")
        buat_rencana(db, kelas2.id)  # milik guru2
        db.close()

        token = get_token(client, "guru_plan2@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        # Guru1 tidak punya rencana, harus 0
        assert data["plan_aktif"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Aktivitas Terbaru
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardAktivitas:

    def test_aktivitas_terbaru_muncul(self, client):
        """✅ Log pertemuan harus muncul di aktivitas_terbaru."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_akt1", email="guru_akt1@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_log(db, kelas.id, topik="Persamaan Linear")
        db.close()

        token = get_token(client, "guru_akt1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert len(data["aktivitas_terbaru"]) == 1
        assert data["aktivitas_terbaru"][0]["topik"] == "Persamaan Linear"

    def test_aktivitas_terbaru_max_10(self, client):
        """✅ Aktivitas terbaru hanya menampilkan maksimal 10 item."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_akt2", email="guru_akt2@test.com")
        kelas = buat_kelas(db, guru.id)
        # Buat 15 log
        for i in range(15):
            buat_log(db, kelas.id, topik=f"Topik {i}")
        db.close()

        token = get_token(client, "guru_akt2@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert len(data["aktivitas_terbaru"]) <= 10

    def test_aktivitas_memiliki_field_lengkap(self, client):
        """✅ Setiap item aktivitas harus punya field yang diperlukan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_akt3", email="guru_akt3@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_log(db, kelas.id, topik="Matriks", nilai=85.0)
        db.close()

        token = get_token(client, "guru_akt3@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        aktivitas = data["aktivitas_terbaru"][0]
        assert "tanggal"  in aktivitas
        assert "topik"    in aktivitas
        assert "kelas_id" in aktivitas
        assert "nilai"    in aktivitas


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA DASHBOARD — Progress Siswa
# ═══════════════════════════════════════════════════════════════════════════════

class TestDashboardProgressSiswa:

    def test_progress_siswa_on_track(self, client):
        """✅ Siswa dengan rata-rata nilai >= 70 harus berstatus 'On Track'."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_prog1", email="guru_prog1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_prog1", email="murid_prog1@test.com")
        daftarkan_murid(db, kelas.id, murid.id)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=80.0)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=90.0)
        db.close()

        token = get_token(client, "guru_prog1@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert len(data["progress_siswa"]) == 1
        assert data["progress_siswa"][0]["status"] == "On Track"
        assert data["progress_siswa"][0]["avg_nilai"] >= 70

    def test_progress_siswa_perlu_perhatian(self, client):
        """✅ Siswa dengan rata-rata nilai < 70 harus berstatus 'Perlu Perhatian'."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_prog2", email="guru_prog2@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_prog2", email="murid_prog2@test.com")
        daftarkan_murid(db, kelas.id, murid.id)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=50.0)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=55.0)
        db.close()

        token = get_token(client, "guru_prog2@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["progress_siswa"][0]["status"] == "Perlu Perhatian"

    def test_progress_siswa_memiliki_field_lengkap(self, client):
        """✅ Setiap item progress siswa harus memiliki semua field."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_prog3", email="guru_prog3@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="Budi Santoso", email="budi@test.com")
        daftarkan_murid(db, kelas.id, murid.id)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=75.0)
        db.close()

        token = get_token(client, "guru_prog3@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        progress = data["progress_siswa"][0]
        assert "murid_id"   in progress
        assert "nama"       in progress
        assert "avg_nilai"  in progress
        assert "total_sesi" in progress
        assert "status"     in progress

    def test_progress_siswa_hitung_total_sesi(self, client):
        """✅ total_sesi harus sesuai jumlah log yang ada untuk murid tersebut."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_prog4", email="guru_prog4@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_sesi", email="murid_sesi@test.com")
        daftarkan_murid(db, kelas.id, murid.id)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=70.0)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=80.0)
        buat_log(db, kelas.id, murid_id=murid.id, nilai=90.0)
        db.close()

        token = get_token(client, "guru_prog4@test.com")
        data  = client.get("/api/v1/dashboard/", headers=auth_header(token)).json()

        assert data["progress_siswa"][0]["total_sesi"] == 3
