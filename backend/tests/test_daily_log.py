"""
test_daily_log.py
Unit testing untuk fitur Daily Log (F001, F002).
Mencakup: tambah log (form), bulk upload (CSV),
          get log, update log, hapus log, filter, akses kontrol.

Pakai SQLite in-memory — tidak perlu PostgreSQL.

Cara jalankan:
    pytest tests/test_daily_log.py -v
"""
import os
import io
import uuid
import pytest
from datetime import date, timedelta, datetime

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_daily_log.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_daily_log.db"

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
    import app.core.database as db_module
    db_module.engine       = engine_test
    db_module.SessionLocal = TestingSessionLocal
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    engine_test.dispose()
    try:
        if os.path.exists("./test_daily_log.db"):
            os.remove("./test_daily_log.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import (
            LogPertemuan, KelasMurid, Kelas,
            Murid, Pengajar, Pengguna,
        )
        db.query(LogPertemuan).delete()
        db.query(KelasMurid).delete()
        db.query(Kelas).delete()
        db.query(Murid).delete()
        db.query(Pengajar).delete()
        db.query(Pengguna).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    from app.main import app
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────

def buat_pengajar(db, nama="Guru Test", email="guru@test.com"):
    from app.models.models import Pengguna, Pengajar
    from app.core.security import hash_password
    uid = str(uuid.uuid4())
    db.add(Pengguna(
        id=uid,
        username=nama.replace(" ", "_").lower() + uid[:4],
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="pengajar",
    ))
    db.add(Pengajar(id=uid))
    db.commit()
    return db.query(Pengguna).filter(Pengguna.id == uid).first()


def buat_murid(db, nama="Murid Test", email="murid@test.com"):
    from app.models.models import Pengguna, Murid
    from app.core.security import hash_password
    uid = str(uuid.uuid4())
    db.add(Pengguna(
        id=uid,
        username=nama.replace(" ", "_").lower() + uid[:4],
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="murid",
    ))
    db.add(Murid(id=uid, nama=nama))
    db.commit()
    return db.query(Murid).filter(Murid.id == uid).first()


def buat_kelas(db, pengajar_id, nama="Kelas Test"):
    from app.models.models import Kelas
    kelas = Kelas(
        id=str(uuid.uuid4()),
        nama=nama,
        mata_pelajaran="Matematika",
        pengajar_id=pengajar_id,
        kredit=20,
    )
    db.add(kelas)
    db.commit()
    db.refresh(kelas)
    return kelas


def buat_log_db(db, kelas_id, murid_id=None, topik="Aljabar",
                nilai=80.0, tanggal=None, catatan=None):
    """Buat log pertemuan langsung ke DB."""
    from app.models.models import LogPertemuan
    log = LogPertemuan(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        tanggal=tanggal or date.today(),
        topik=topik,
        nilai=nilai,
        catatan=catatan,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_token(client, email, password="Test1234!"):
    resp = client.post("/api/v1/auth/login", json={
        "email_address": email,
        "password": password,
    })
    return resp.json().get("access_token", "")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def payload_log_lengkap(kelas_id, murid_id=None):
    """Payload log pertemuan lengkap untuk POST request."""
    return {
        "kelas_id":                  kelas_id,
        "murid_id":                  murid_id,
        "tanggal":                   str(date.today()),
        "topik":                     "Persamaan Linear",
        "nilai":                     85.0,
        "tingkat_pemahaman":         "paham",
        "tingkat_keterlibatan":      "aktif",
        "kompetensi_dicapai":        "Siswa dapat menyelesaikan persamaan linear",
        "target_materi_berikutnya":  "Persamaan Kuadrat",
        "kendala":                   "Beberapa siswa masih bingung tanda negatif",
        "catatan":                   "Sesi berjalan lancar",
        "durasi_menit":              90,
        "metode_belajar":            "Diskusi Kelompok",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TEST TAMBAH LOG (F001 — Single Form)
# ═══════════════════════════════════════════════════════════════════════════════

class TestTambahLog:

    def test_tambah_log_lengkap_berhasil(self, client):
        """✅ Tambah log dengan semua field terisi harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add1", email="guru_add1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_add1", email="murid_add1@test.com")
        db.close()

        token    = get_token(client, "guru_add1@test.com")
        response = client.post("/api/v1/logs/", json=payload_log_lengkap(kelas.id, murid.id),
                               headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["topik"]               == "Persamaan Linear"
        assert data["nilai"]               == 85.0
        assert data["tingkat_pemahaman"]   == "paham"
        assert data["tingkat_keterlibatan"]== "aktif"
        assert data["durasi_menit"]        == 90
        assert data["kelas_id"]            == kelas.id
        assert data["murid_id"]            == murid.id
        assert "id" in data

    def test_tambah_log_minimal_berhasil(self, client):
        """✅ Tambah log dengan field minimal (kelas_id, tanggal, topik) harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add2", email="guru_add2@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_add2@test.com")
        response = client.post("/api/v1/logs/", json={
            "kelas_id": kelas.id,
            "tanggal":  str(date.today()),
            "topik":    "Materi Minimal",
        }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["topik"]    == "Materi Minimal"
        assert data["nilai"]    is None
        assert data["murid_id"] is None

    def test_tambah_log_tanpa_kelas_id_ditolak(self, client):
        """❌ Log tanpa kelas_id harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_add3", email="guru_add3@test.com")
        db.close()

        token    = get_token(client, "guru_add3@test.com")
        response = client.post("/api/v1/logs/", json={
            "tanggal": str(date.today()),
            "topik":   "Tanpa Kelas",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tambah_log_tanpa_topik_ditolak(self, client):
        """❌ Log tanpa topik harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add4", email="guru_add4@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_add4@test.com")
        response = client.post("/api/v1/logs/", json={
            "kelas_id": kelas.id,
            "tanggal":  str(date.today()),
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tambah_log_tanpa_tanggal_ditolak(self, client):
        """❌ Log tanpa tanggal harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add5", email="guru_add5@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_add5@test.com")
        response = client.post("/api/v1/logs/", json={
            "kelas_id": kelas.id,
            "topik":    "Tanpa Tanggal",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tambah_log_tanpa_token_ditolak(self, client):
        """❌ Tambah log tanpa token harus ditolak."""
        response = client.post("/api/v1/logs/", json={
            "kelas_id": "kelas-id",
            "tanggal":  str(date.today()),
            "topik":    "Tanpa Token",
        })
        assert response.status_code in (401, 403)

    def test_murid_tidak_bisa_tambah_log(self, client):
        """❌ Murid tidak boleh tambah log pertemuan."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_add2", email="murid_add2@test.com")
        db.close()

        token    = get_token(client, "murid_add2@test.com")
        response = client.post("/api/v1/logs/", json={
            "kelas_id": "kelas-id",
            "tanggal":  str(date.today()),
            "topik":    "Dari Murid",
        }, headers=auth_header(token))

        assert response.status_code == 403

    def test_tambah_log_tersimpan_di_database(self, client):
        """✅ Log yang ditambah via API harus tersimpan di database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add6", email="guru_add6@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_add6@test.com")
        response = client.post("/api/v1/logs/", json={
            "kelas_id": kelas.id,
            "tanggal":  str(date.today()),
            "topik":    "Topik Tersimpan",
            "nilai":    90.0,
        }, headers=auth_header(token))

        assert response.status_code == 201
        log_id = response.json()["id"]

        # Cek langsung di database
        db = TestingSessionLocal()
        from app.models.models import LogPertemuan
        log = db.query(LogPertemuan).filter(LogPertemuan.id == log_id).first()
        db.close()

        assert log is not None
        assert log.topik == "Topik Tersimpan"
        assert float(log.nilai) == 90.0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LOG
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLog:

    def test_get_log_by_id_berhasil(self, client):
        """✅ Ambil satu log berdasarkan ID harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get1", email="guru_get1@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, topik="Topik Get")
        db.close()

        token    = get_token(client, "guru_get1@test.com")
        response = client.get(f"/api/v1/logs/{log.id}", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["id"]    == log.id
        assert response.json()["topik"] == "Topik Get"

    def test_get_log_tidak_ditemukan(self, client):
        """❌ Get log dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_get2", email="guru_get2@test.com")
        db.close()

        token    = get_token(client, "guru_get2@test.com")
        response = client.get("/api/v1/logs/id-tidak-ada-sama-sekali",
                              headers=auth_header(token))

        assert response.status_code == 404

    def test_get_log_response_field_lengkap(self, client):
        """✅ Response log harus memiliki semua field yang diperlukan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get3", email="guru_get3@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_get1", email="murid_get1@test.com")
        log   = buat_log_db(db, kelas.id, murid_id=murid.id,
                            topik="Topik Field", nilai=75.0)
        db.close()

        token    = get_token(client, "guru_get3@test.com")
        response = client.get(f"/api/v1/logs/{log.id}", headers=auth_header(token))
        data     = response.json()

        assert "id"         in data
        assert "kelas_id"   in data
        assert "murid_id"   in data
        assert "tanggal"    in data
        assert "topik"      in data
        assert "nilai"      in data
        assert "created_at" in data


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LOGS BY KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLogsByKelas:

    def test_get_logs_by_kelas_berhasil(self, client):
        """✅ Ambil semua log untuk satu kelas harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lk1", email="guru_lk1@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_log_db(db, kelas.id, topik="Topik 1")
        buat_log_db(db, kelas.id, topik="Topik 2")
        buat_log_db(db, kelas.id, topik="Topik 3")
        db.close()

        token    = get_token(client, "guru_lk1@test.com")
        response = client.get(f"/api/v1/logs/kelas/{kelas.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_logs_kelas_kosong(self, client):
        """✅ Kelas tanpa log harus return list kosong."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lk2", email="guru_lk2@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_lk2@test.com")
        response = client.get(f"/api/v1/logs/kelas/{kelas.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_get_logs_by_kelas_filter_murid(self, client):
        """✅ Filter log per murid di dalam satu kelas harus bekerja."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_lk3", email="guru_lk3@test.com")
        kelas  = buat_kelas(db, guru.id)
        murid1 = buat_murid(db, nama="murid_lk1", email="murid_lk1@test.com")
        murid2 = buat_murid(db, nama="murid_lk2", email="murid_lk2@test.com")
        buat_log_db(db, kelas.id, murid_id=murid1.id, topik="Log Murid 1")
        buat_log_db(db, kelas.id, murid_id=murid1.id, topik="Log Murid 1 Lagi")
        buat_log_db(db, kelas.id, murid_id=murid2.id, topik="Log Murid 2")
        db.close()

        token    = get_token(client, "guru_lk3@test.com")
        response = client.get(
            f"/api/v1/logs/kelas/{kelas.id}?murid_id={murid1.id}",
            headers=auth_header(token),
        )

        assert response.status_code == 200
        logs = response.json()
        assert len(logs) == 2
        for log in logs:
            assert log["murid_id"] == murid1.id

    def test_get_logs_kelas_tidak_tercampur_kelas_lain(self, client):
        """✅ Log dari kelas lain tidak boleh ikut muncul."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_lk4", email="guru_lk4@test.com")
        kelas1 = buat_kelas(db, guru.id, nama="Kelas A")
        kelas2 = buat_kelas(db, guru.id, nama="Kelas B")
        buat_log_db(db, kelas1.id, topik="Log Kelas A")
        buat_log_db(db, kelas2.id, topik="Log Kelas B")
        buat_log_db(db, kelas2.id, topik="Log Kelas B Lagi")
        db.close()

        token    = get_token(client, "guru_lk4@test.com")
        response = client.get(f"/api/v1/logs/kelas/{kelas1.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["topik"] == "Log Kelas A"

    def test_get_logs_kelas_pagination(self, client):
        """✅ Parameter skip dan limit harus bekerja dengan benar."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lk5", email="guru_lk5@test.com")
        kelas = buat_kelas(db, guru.id)
        for i in range(10):
            buat_log_db(db, kelas.id, topik=f"Topik {i}")
        db.close()

        token = get_token(client, "guru_lk5@test.com")

        # Ambil 5 pertama
        resp1 = client.get(f"/api/v1/logs/kelas/{kelas.id}?skip=0&limit=5",
                           headers=auth_header(token))
        assert len(resp1.json()) == 5

        # Skip 5, ambil 5 berikutnya
        resp2 = client.get(f"/api/v1/logs/kelas/{kelas.id}?skip=5&limit=5",
                           headers=auth_header(token))
        assert len(resp2.json()) == 5

        # Pastikan dua halaman tidak overlap
        ids1 = {l["id"] for l in resp1.json()}
        ids2 = {l["id"] for l in resp2.json()}
        assert ids1.isdisjoint(ids2)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LOGS BY MURID
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLogsByMurid:

    def test_get_logs_by_murid_berhasil(self, client):
        """✅ Ambil semua log untuk satu murid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lm1", email="guru_lm1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_lm1", email="murid_lm1@test.com")
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Log A")
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Log B")
        db.close()

        token    = get_token(client, "guru_lm1@test.com")
        response = client.get(f"/api/v1/logs/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_logs_murid_tanpa_log(self, client):
        """✅ Murid tanpa log harus return list kosong."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_lm2", email="guru_lm2@test.com")
        murid = buat_murid(db, nama="murid_lm2", email="murid_lm2@test.com")
        db.close()

        token    = get_token(client, "guru_lm2@test.com")
        response = client.get(f"/api/v1/logs/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_get_logs_murid_tidak_tercampur_murid_lain(self, client):
        """✅ Log murid lain tidak boleh muncul."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_lm3", email="guru_lm3@test.com")
        kelas  = buat_kelas(db, guru.id)
        murid1 = buat_murid(db, nama="murid_lm3", email="murid_lm3@test.com")
        murid2 = buat_murid(db, nama="murid_lm4", email="murid_lm4@test.com")
        buat_log_db(db, kelas.id, murid_id=murid1.id, topik="Log Murid1")
        buat_log_db(db, kelas.id, murid_id=murid2.id, topik="Log Murid2")
        db.close()

        token    = get_token(client, "guru_lm3@test.com")
        response = client.get(f"/api/v1/logs/murid/{murid1.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["murid_id"] == murid1.id


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LOG HARI INI
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLogHariIni:

    def test_log_hari_ini_muncul(self, client):
        """✅ Log yang dibuat hari ini harus muncul."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_hi1", email="guru_hi1@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_log_db(db, kelas.id, topik="Pagi Ini", tanggal=date.today())
        buat_log_db(db, kelas.id, topik="Siang Ini", tanggal=date.today())
        db.close()

        token    = get_token(client, "guru_hi1@test.com")
        response = client.get("/api/v1/logs/hari-ini", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_log_kemarin_tidak_muncul(self, client):
        """✅ Log kemarin tidak boleh muncul di hari-ini."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_hi2", email="guru_hi2@test.com")
        kelas = buat_kelas(db, guru.id)
        kemarin = date.today() - timedelta(days=1)
        buat_log_db(db, kelas.id, topik="Log Kemarin", tanggal=kemarin)
        db.close()

        token    = get_token(client, "guru_hi2@test.com")
        response = client.get("/api/v1/logs/hari-ini", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_log_hari_ini_hanya_milik_kelas_sendiri(self, client):
        """✅ Hanya log dari kelas milik pengajar yang login yang muncul."""
        db = TestingSessionLocal()
        guru1  = buat_pengajar(db, nama="guru_hi3", email="guru_hi3@test.com")
        guru2  = buat_pengajar(db, nama="guru_hi4", email="guru_hi4@test.com")
        kelas1 = buat_kelas(db, guru1.id, nama="Kelas Guru1")
        kelas2 = buat_kelas(db, guru2.id, nama="Kelas Guru2")
        buat_log_db(db, kelas1.id, topik="Log Guru1", tanggal=date.today())
        buat_log_db(db, kelas2.id, topik="Log Guru2", tanggal=date.today())
        db.close()

        token    = get_token(client, "guru_hi3@test.com")
        response = client.get("/api/v1/logs/hari-ini", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["topik"] == "Log Guru1"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST UPDATE LOG
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateLog:

    def test_update_topik_berhasil(self, client):
        """✅ Update topik log harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_upd1", email="guru_upd1@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, topik="Topik Lama")
        db.close()

        token    = get_token(client, "guru_upd1@test.com")
        response = client.put(f"/api/v1/logs/{log.id}", json={
            "topik": "Topik Baru",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["topik"] == "Topik Baru"

    def test_update_nilai_berhasil(self, client):
        """✅ Update nilai log harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_upd2", email="guru_upd2@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, nilai=70.0)
        db.close()

        token    = get_token(client, "guru_upd2@test.com")
        response = client.put(f"/api/v1/logs/{log.id}", json={
            "nilai": 85.0,
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nilai"] == 85.0

    def test_update_semua_field_berhasil(self, client):
        """✅ Update semua field sekaligus harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_upd3", email="guru_upd3@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, topik="Sebelum", nilai=60.0)
        db.close()

        token    = get_token(client, "guru_upd3@test.com")
        response = client.put(f"/api/v1/logs/{log.id}", json={
            "topik":                    "Sesudah Update",
            "nilai":                    95.0,
            "tingkat_pemahaman":        "sangat_paham",
            "tingkat_keterlibatan":     "sangat_aktif",
            "catatan":                  "Update catatan",
            "durasi_menit":             120,
            "metode_belajar":           "Ceramah",
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["topik"]               == "Sesudah Update"
        assert data["nilai"]               == 95.0
        assert data["tingkat_pemahaman"]   == "sangat_paham"
        assert data["durasi_menit"]        == 120

    def test_update_partial_field_lain_tidak_berubah(self, client):
        """✅ Update sebagian field tidak boleh mengubah field lain."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_upd4", email="guru_upd4@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, topik="Topik Tetap", nilai=80.0)
        db.close()

        token    = get_token(client, "guru_upd4@test.com")
        response = client.put(f"/api/v1/logs/{log.id}", json={
            "catatan": "Hanya catatan yang berubah",
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["topik"] == "Topik Tetap"   # tidak berubah
        assert data["nilai"] == 80.0             # tidak berubah
        assert data["catatan"] == "Hanya catatan yang berubah"

    def test_update_log_tidak_ditemukan(self, client):
        """❌ Update log dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd5", email="guru_upd5@test.com")
        db.close()

        token    = get_token(client, "guru_upd5@test.com")
        response = client.put("/api/v1/logs/id-tidak-ada", json={
            "topik": "Apapun",
        }, headers=auth_header(token))

        assert response.status_code == 404

    def test_update_log_tanpa_token_ditolak(self, client):
        """❌ Update log tanpa token harus ditolak."""
        response = client.put("/api/v1/logs/log-id-apapun", json={
            "topik": "Tanpa Token",
        })
        assert response.status_code in (401, 403)

    def test_update_tersimpan_di_database(self, client):
        """✅ Perubahan setelah update harus tersimpan di database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_upd6", email="guru_upd6@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, topik="Sebelum DB", nilai=60.0)
        db.close()

        token = get_token(client, "guru_upd6@test.com")
        client.put(f"/api/v1/logs/{log.id}", json={
            "topik": "Sesudah DB",
            "nilai": 99.0,
        }, headers=auth_header(token))

        # Verifikasi langsung di database
        db = TestingSessionLocal()
        from app.models.models import LogPertemuan
        updated = db.query(LogPertemuan).filter(LogPertemuan.id == log.id).first()
        db.close()

        assert updated.topik       == "Sesudah DB"
        assert float(updated.nilai) == 99.0


# ═══════════════════════════════════════════════════════════════════════════════
# TEST HAPUS LOG
# ═══════════════════════════════════════════════════════════════════════════════

class TestHapusLog:

    def test_hapus_log_berhasil(self, client):
        """✅ Hapus log harus berhasil dan log benar-benar terhapus."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_del1", email="guru_del1@test.com")
        kelas = buat_kelas(db, guru.id)
        log   = buat_log_db(db, kelas.id, topik="Log Dihapus")
        db.close()

        token    = get_token(client, "guru_del1@test.com")
        response = client.delete(f"/api/v1/logs/{log.id}", headers=auth_header(token))
        assert response.status_code == 204

        # Pastikan benar-benar terhapus
        get_resp = client.get(f"/api/v1/logs/{log.id}", headers=auth_header(token))
        assert get_resp.status_code == 404

    def test_hapus_log_tidak_ditemukan(self, client):
        """❌ Hapus log dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del2", email="guru_del2@test.com")
        db.close()

        token    = get_token(client, "guru_del2@test.com")
        response = client.delete("/api/v1/logs/id-tidak-ada-sama-sekali",
                                 headers=auth_header(token))

        assert response.status_code == 404

    def test_hapus_log_tanpa_token_ditolak(self, client):
        """❌ Hapus log tanpa token harus ditolak."""
        response = client.delete("/api/v1/logs/log-id-apapun")
        assert response.status_code in (401, 403)

    def test_hapus_log_tidak_pengaruhi_log_lain(self, client):
        """✅ Hapus satu log tidak boleh menghapus log lain di kelas yang sama."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_del3", email="guru_del3@test.com")
        kelas = buat_kelas(db, guru.id)
        log1  = buat_log_db(db, kelas.id, topik="Log Tetap")
        log2  = buat_log_db(db, kelas.id, topik="Log Dihapus")
        db.close()

        token = get_token(client, "guru_del3@test.com")
        client.delete(f"/api/v1/logs/{log2.id}", headers=auth_header(token))

        # Log pertama masih harus ada
        response = client.get(f"/api/v1/logs/{log1.id}", headers=auth_header(token))
        assert response.status_code == 200
        assert response.json()["topik"] == "Log Tetap"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST BULK UPLOAD CSV (F002)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBulkUpload:

    def _buat_csv(self, rows: list) -> bytes:
        """Helper buat file CSV dari list of dicts."""
        import csv
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return output.getvalue().encode("utf-8")

    def test_bulk_upload_csv_berhasil(self, client):
        """✅ Upload CSV dengan data valid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bulk1", email="guru_bulk1@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        csv_bytes = self._buat_csv([
            {"tanggal": str(date.today()), "topik": "Aljabar",    "nilai": 80},
            {"tanggal": str(date.today()), "topik": "Geometri",   "nilai": 75},
            {"tanggal": str(date.today()), "topik": "Trigonometri","nilai": 90},
        ])

        token    = get_token(client, "guru_bulk1@test.com")
        response = client.post(
            f"/api/v1/logs/bulk/{kelas.id}",
            files={"file": ("log_test.csv", csv_bytes, "text/csv")},
            headers=auth_header(token),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total_baris"] == 3
        assert data["berhasil"]    == 3
        assert data["gagal"]       == 0

    def test_bulk_upload_tersimpan_di_database(self, client):
        """✅ Data dari bulk upload harus benar-benar tersimpan di database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bulk2", email="guru_bulk2@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        csv_bytes = self._buat_csv([
            {"tanggal": str(date.today()), "topik": "Topik Bulk DB", "nilai": 88},
        ])

        token = get_token(client, "guru_bulk2@test.com")
        client.post(
            f"/api/v1/logs/bulk/{kelas.id}",
            files={"file": ("log.csv", csv_bytes, "text/csv")},
            headers=auth_header(token),
        )

        # Cek di database
        db = TestingSessionLocal()
        from app.models.models import LogPertemuan
        logs = db.query(LogPertemuan).filter(
            LogPertemuan.kelas_id == kelas.id,
            LogPertemuan.topik == "Topik Bulk DB",
        ).all()
        db.close()

        assert len(logs) == 1
        assert float(logs[0].nilai) == 88.0

    def test_bulk_upload_baris_tanpa_topik_gagal(self, client):
        """✅ Baris tanpa topik harus masuk ke detail_error."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bulk3", email="guru_bulk3@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        csv_bytes = self._buat_csv([
            {"tanggal": str(date.today()), "topik": "Valid",  "nilai": 80},
            {"tanggal": str(date.today()), "topik": "",       "nilai": 70},  # topik kosong
            {"tanggal": str(date.today()), "topik": "Valid 2","nilai": 90},
        ])

        token    = get_token(client, "guru_bulk3@test.com")
        response = client.post(
            f"/api/v1/logs/bulk/{kelas.id}",
            files={"file": ("log.csv", csv_bytes, "text/csv")},
            headers=auth_header(token),
        )

        assert response.status_code == 201
        data = response.json()
        assert data["berhasil"]        == 2
        assert data["gagal"]           == 1
        assert len(data["detail_error"]) == 1

    def test_bulk_upload_file_kosong_ditolak(self, client):
        """❌ Upload file kosong harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bulk4", email="guru_bulk4@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_bulk4@test.com")
        response = client.post(
            f"/api/v1/logs/bulk/{kelas.id}",
            files={"file": ("kosong.csv", b"", "text/csv")},
            headers=auth_header(token),
        )

        assert response.status_code == 400

    def test_bulk_upload_ekstensi_tidak_valid_ditolak(self, client):
        """❌ Upload file dengan ekstensi tidak didukung harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bulk5", email="guru_bulk5@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_bulk5@test.com")
        response = client.post(
            f"/api/v1/logs/bulk/{kelas.id}",
            files={"file": ("data.txt", b"topik,nilai\nAljabar,80", "text/plain")},
            headers=auth_header(token),
        )

        assert response.status_code == 400

    def test_bulk_upload_tanpa_token_ditolak(self, client):
        """❌ Bulk upload tanpa token harus ditolak."""
        csv_bytes = self._buat_csv([
            {"tanggal": str(date.today()), "topik": "Topik", "nilai": 80},
        ])
        response = client.post(
            "/api/v1/logs/bulk/kelas-id-apapun",
            files={"file": ("log.csv", csv_bytes, "text/csv")},
        )
        assert response.status_code in (401, 403)
