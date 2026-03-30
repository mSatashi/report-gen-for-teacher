"""
test_kelas.py
Unit testing untuk fitur Kelas & Murid.
Pakai SQLite in-memory — tidak perlu PostgreSQL.

Cara jalankan:
    pytest tests/test_kelas.py -v
"""
import os
import uuid
import pytest

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_kelas.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_kelas.db"

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
        if os.path.exists("./test_kelas.db"):
            os.remove("./test_kelas.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import KelasMusrid, Kelas, Murid, Pengajar, Pengguna
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
        id=uid, username=nama.replace(" ", "_").lower(),
        email_address=email, hashed_password=hash_password("Test1234!"),
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
        id=uid, username=nama.replace(" ", "_").lower(),
        email_address=email, hashed_password=hash_password("Test1234!"),
        tipe_pengguna="murid",
    ))
    db.add(Murid(id=uid, nama=nama))
    db.commit()
    return db.query(Murid).filter(Murid.id == uid).first()


def get_token(client, email="guru@test.com", password="Test1234!"):
    resp = client.post("/api/v1/auth/login", json={
        "email_address": email, "password": password,
    })
    return resp.json().get("access_token", "")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CRUD KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuatKelas:

    def test_buat_kelas_berhasil(self, client):
        """✅ Pengajar bisa membuat kelas baru."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat", email="guru_buat@test.com")
        db.close()

        token = get_token(client, "guru_buat@test.com")
        response = client.post("/api/v1/kelas/", json={
            "nama": "Matematika Kelas 10",
            "mata_pelajaran": "Matematika",
            "kredit": 20,
            "jadwal": "Senin 08:00",
        }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["nama"] == "Matematika Kelas 10"
        assert data["mata_pelajaran"] == "Matematika"
        assert data["kredit"] == 20
        assert "id" in data

    def test_buat_kelas_tanpa_token_ditolak(self, client):
        """❌ Buat kelas tanpa token harus ditolak."""
        response = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Tanpa Auth",
        })
        assert response.status_code in (401, 403)

    def test_buat_kelas_tanpa_nama_ditolak(self, client):
        """❌ Buat kelas tanpa field nama wajib harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_nonama", email="guru_nonama@test.com")
        db.close()

        token = get_token(client, "guru_nonama@test.com")
        response = client.post("/api/v1/kelas/", json={
            "mata_pelajaran": "Fisika",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_buat_kelas_field_opsional_boleh_kosong(self, client):
        """✅ Field opsional seperti jadwal boleh tidak diisi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_opsional", email="guru_opsional@test.com")
        db.close()

        token = get_token(client, "guru_opsional@test.com")
        response = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Minimal",
        }, headers=auth_header(token))

        assert response.status_code == 201

    def test_buat_kelas_otomatis_assign_ke_pengajar(self, client):
        """✅ Kelas yang dibuat harus otomatis ter-assign ke pengajar yang login."""
        db = TestingSessionLocal()
        guru = buat_pengajar(db, nama="guru_assign", email="guru_assign@test.com")
        db.close()

        token = get_token(client, "guru_assign@test.com")
        response = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Auto Assign",
        }, headers=auth_header(token))

        assert response.status_code == 201
        assert response.json()["pengajar_id"] == guru.id

    def test_murid_tidak_bisa_buat_kelas(self, client):
        """❌ Murid tidak boleh membuat kelas."""
        db = TestingSessionLocal()
        buat_murid(db, nama="murid_buat", email="murid_buat@test.com")
        db.close()

        token = get_token(client, "murid_buat@test.com")
        response = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Dari Murid",
        }, headers=auth_header(token))

        assert response.status_code == 403


class TestListKelas:

    def test_list_kelas_kosong(self, client):
        """✅ Pengajar baru belum punya kelas, list harus kosong."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_list1", email="guru_list1@test.com")
        db.close()

        token = get_token(client, "guru_list1@test.com")
        response = client.get("/api/v1/kelas/", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_list_kelas_hanya_milik_sendiri(self, client):
        """✅ List kelas hanya menampilkan kelas milik pengajar yang login."""
        db = TestingSessionLocal()
        guru1 = buat_pengajar(db, nama="guru_list2", email="guru_list2@test.com")
        guru2 = buat_pengajar(db, nama="guru_list3", email="guru_list3@test.com")
        db.close()

        # Guru1 buat 2 kelas
        token1 = get_token(client, "guru_list2@test.com")
        client.post("/api/v1/kelas/", json={"nama": "Kelas A"}, headers=auth_header(token1))
        client.post("/api/v1/kelas/", json={"nama": "Kelas B"}, headers=auth_header(token1))

        # Guru2 buat 1 kelas
        token2 = get_token(client, "guru_list3@test.com")
        client.post("/api/v1/kelas/", json={"nama": "Kelas C"}, headers=auth_header(token2))

        # Guru1 hanya boleh lihat 2 kelasnya sendiri
        response = client.get("/api/v1/kelas/", headers=auth_header(token1))
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_kelas_tanpa_token_ditolak(self, client):
        """❌ List kelas tanpa token harus ditolak."""
        response = client.get("/api/v1/kelas/")
        assert response.status_code in (401, 403)


class TestGetKelas:

    def test_get_kelas_berhasil(self, client):
        """✅ Ambil detail kelas berdasarkan ID."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_get", email="guru_get@test.com")
        db.close()

        token = get_token(client, "guru_get@test.com")
        buat_resp = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Detail",
            "mata_pelajaran": "Fisika",
        }, headers=auth_header(token))
        kelas_id = buat_resp.json()["id"]

        response = client.get(f"/api/v1/kelas/{kelas_id}", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nama"] == "Kelas Detail"
        assert response.json()["id"] == kelas_id

    def test_get_kelas_tidak_ditemukan(self, client):
        """❌ Ambil kelas dengan ID yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_get404", email="guru_get404@test.com")
        db.close()

        token = get_token(client, "guru_get404@test.com")
        response = client.get("/api/v1/kelas/id-tidak-ada-sama-sekali", headers=auth_header(token))

        assert response.status_code == 404


class TestUpdateKelas:

    def test_update_kelas_berhasil(self, client):
        """✅ Pengajar bisa update nama dan detail kelasnya."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd", email="guru_upd@test.com")
        db.close()

        token = get_token(client, "guru_upd@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Nama Lama",
        }, headers=auth_header(token)).json()["id"]

        response = client.put(f"/api/v1/kelas/{kelas_id}", json={
            "nama": "Nama Baru",
            "jadwal": "Selasa 10:00",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nama"] == "Nama Baru"
        assert response.json()["jadwal"] == "Selasa 10:00"

    def test_update_kelas_milik_guru_lain_ditolak(self, client):
        """❌ Pengajar tidak bisa update kelas milik pengajar lain."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd2", email="guru_upd2@test.com")
        buat_pengajar(db, nama="guru_upd3", email="guru_upd3@test.com")
        db.close()

        token1 = get_token(client, "guru_upd2@test.com")
        token2 = get_token(client, "guru_upd3@test.com")

        # Guru1 buat kelas
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Guru1",
        }, headers=auth_header(token1)).json()["id"]

        # Guru2 coba update kelas milik Guru1
        response = client.put(f"/api/v1/kelas/{kelas_id}", json={
            "nama": "Dicuri Guru2",
        }, headers=auth_header(token2))

        assert response.status_code == 404

    def test_update_kelas_tidak_ditemukan(self, client):
        """❌ Update kelas dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd4", email="guru_upd4@test.com")
        db.close()

        token = get_token(client, "guru_upd4@test.com")
        response = client.put("/api/v1/kelas/id-tidak-ada", json={
            "nama": "Apapun",
        }, headers=auth_header(token))

        assert response.status_code == 404


class TestHapusKelas:

    def test_hapus_kelas_berhasil(self, client):
        """✅ Pengajar bisa hapus kelasnya sendiri."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del", email="guru_del@test.com")
        db.close()

        token = get_token(client, "guru_del@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Dihapus",
        }, headers=auth_header(token)).json()["id"]

        response = client.delete(f"/api/v1/kelas/{kelas_id}", headers=auth_header(token))
        assert response.status_code == 204

        # Pastikan kelas benar-benar terhapus
        get_resp = client.get(f"/api/v1/kelas/{kelas_id}", headers=auth_header(token))
        assert get_resp.status_code == 404

    def test_hapus_kelas_milik_guru_lain_ditolak(self, client):
        """❌ Pengajar tidak bisa hapus kelas milik pengajar lain."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del2", email="guru_del2@test.com")
        buat_pengajar(db, nama="guru_del3", email="guru_del3@test.com")
        db.close()

        token1 = get_token(client, "guru_del2@test.com")
        token2 = get_token(client, "guru_del3@test.com")

        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Guru1",
        }, headers=auth_header(token1)).json()["id"]

        response = client.delete(f"/api/v1/kelas/{kelas_id}", headers=auth_header(token2))
        assert response.status_code == 404

    def test_hapus_kelas_tidak_ditemukan(self, client):
        """❌ Hapus kelas dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del4", email="guru_del4@test.com")
        db.close()

        token = get_token(client, "guru_del4@test.com")
        response = client.delete("/api/v1/kelas/id-tidak-ada", headers=auth_header(token))

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# TEST MURID DI DALAM KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTambahMuridKeKelas:

    def test_tambah_murid_ke_kelas_berhasil(self, client):
        """✅ Pengajar bisa tambah murid ke kelasnya."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_addm1", email="guru_addm1@test.com")
        murid = buat_murid(db, nama="murid_addm1", email="murid_addm1@test.com")
        db.close()

        token    = get_token(client, "guru_addm1@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Tambah Murid",
        }, headers=auth_header(token)).json()["id"]

        response = client.post(f"/api/v1/kelas/{kelas_id}/murid", json={
            "murid_id": murid.id,
        }, headers=auth_header(token))

        assert response.status_code == 201
        assert "berhasil" in response.json()["message"].lower()

    def test_tambah_murid_duplikat_ditolak(self, client):
        """❌ Murid yang sudah ada di kelas tidak boleh ditambah lagi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_addm2", email="guru_addm2@test.com")
        murid = buat_murid(db, nama="murid_addm2", email="murid_addm2@test.com")
        db.close()

        token    = get_token(client, "guru_addm2@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Duplikat",
        }, headers=auth_header(token)).json()["id"]

        # Tambah pertama kali
        client.post(f"/api/v1/kelas/{kelas_id}/murid", json={
            "murid_id": murid.id,
        }, headers=auth_header(token))

        # Tambah lagi (duplikat) — harus ditolak
        response = client.post(f"/api/v1/kelas/{kelas_id}/murid", json={
            "murid_id": murid.id,
        }, headers=auth_header(token))

        assert response.status_code == 400
        assert "sudah ada" in response.json()["detail"].lower()

    def test_tambah_murid_tanpa_token_ditolak(self, client):
        """❌ Tambah murid tanpa token harus ditolak."""
        response = client.post("/api/v1/kelas/kelas-id-apapun/murid", json={
            "murid_id": "murid-id-apapun",
        })
        assert response.status_code in (401, 403)


class TestListMuridKelas:

    def test_list_murid_kelas_kosong(self, client):
        """✅ Kelas baru belum ada murid, list harus kosong."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_lm1", email="guru_lm1@test.com")
        db.close()

        token    = get_token(client, "guru_lm1@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Kosong",
        }, headers=auth_header(token)).json()["id"]

        response = client.get(f"/api/v1/kelas/{kelas_id}/murid", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_list_murid_sesuai_yang_terdaftar(self, client):
        """✅ List murid harus menampilkan semua murid yang terdaftar di kelas."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_lm2", email="guru_lm2@test.com")
        murid1 = buat_murid(db, nama="murid_lm1", email="murid_lm1@test.com")
        murid2 = buat_murid(db, nama="murid_lm2", email="murid_lm2@test.com")
        murid3 = buat_murid(db, nama="murid_lm3", email="murid_lm3@test.com")
        db.close()

        token    = get_token(client, "guru_lm2@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas 3 Murid",
        }, headers=auth_header(token)).json()["id"]

        for murid in [murid1, murid2, murid3]:
            client.post(f"/api/v1/kelas/{kelas_id}/murid", json={
                "murid_id": murid.id,
            }, headers=auth_header(token))

        response = client.get(f"/api/v1/kelas/{kelas_id}/murid", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_murid_memiliki_field_lengkap(self, client):
        """✅ Setiap murid di list harus punya field yang diperlukan."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_lm3", email="guru_lm3@test.com")
        murid = buat_murid(db, nama="Andi Saputra", email="andi@test.com")
        db.close()

        token    = get_token(client, "guru_lm3@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Field Check",
        }, headers=auth_header(token)).json()["id"]

        client.post(f"/api/v1/kelas/{kelas_id}/murid", json={
            "murid_id": murid.id,
        }, headers=auth_header(token))

        response = client.get(f"/api/v1/kelas/{kelas_id}/murid", headers=auth_header(token))
        murid_data = response.json()[0]

        assert "id"            in murid_data
        assert "username"      in murid_data
        assert "email_address" in murid_data
        assert "nama"          in murid_data
        assert "credit_total"  in murid_data


class TestHapusMuridDariKelas:

    def test_hapus_murid_dari_kelas_berhasil(self, client):
        """✅ Pengajar bisa keluarkan murid dari kelas."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_hm1", email="guru_hm1@test.com")
        murid = buat_murid(db, nama="murid_hm1", email="murid_hm1@test.com")
        db.close()

        token    = get_token(client, "guru_hm1@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Hapus Murid",
        }, headers=auth_header(token)).json()["id"]

        client.post(f"/api/v1/kelas/{kelas_id}/murid", json={
            "murid_id": murid.id,
        }, headers=auth_header(token))

        # Hapus murid dari kelas
        response = client.delete(
            f"/api/v1/kelas/{kelas_id}/murid/{murid.id}",
            headers=auth_header(token),
        )
        assert response.status_code == 204

        # Pastikan list murid sudah kosong
        list_resp = client.get(f"/api/v1/kelas/{kelas_id}/murid", headers=auth_header(token))
        assert list_resp.json() == []

    def test_hapus_murid_tidak_ada_di_kelas_return_404(self, client):
        """❌ Hapus murid yang tidak ada di kelas harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_hm2", email="guru_hm2@test.com")
        db.close()

        token    = get_token(client, "guru_hm2@test.com")
        kelas_id = client.post("/api/v1/kelas/", json={
            "nama": "Kelas Kosong",
        }, headers=auth_header(token)).json()["id"]

        response = client.delete(
            f"/api/v1/kelas/{kelas_id}/murid/murid-tidak-ada",
            headers=auth_header(token),
        )
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CRUD MURID STANDALONE
# ═══════════════════════════════════════════════════════════════════════════════

class TestTambahMuridBaru:

    def test_tambah_murid_baru_berhasil(self, client):
        """✅ Pengajar bisa buat akun murid baru."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_nm1", email="guru_nm1@test.com")
        db.close()

        token = get_token(client, "guru_nm1@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_baru_1",
            "email_address": "murid_baru_1@test.com",
            "password":      "Test1234!",
            "nama":          "Budi Setiawan",
            "usia":          15,
            "level":         "SMA",
            "credit_total":  20,
        }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["nama"]    == "Budi Setiawan"
        assert data["usia"]    == 15
        assert data["level"]   == "SMA"
        assert data["credit_total"] == 20
        assert "id" in data

    def test_tambah_murid_email_duplikat_ditolak(self, client):
        """❌ Buat murid dengan email yang sudah dipakai harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_nm2", email="guru_nm2@test.com")
        buat_murid(db, nama="murid_existing", email="sudah_ada@test.com")
        db.close()

        token = get_token(client, "guru_nm2@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "username_baru",
            "email_address": "sudah_ada@test.com",  # email sudah ada
            "password":      "Test1234!",
            "nama":          "Nama Baru",
        }, headers=auth_header(token))

        assert response.status_code == 400
        assert "sudah terdaftar" in response.json()["detail"].lower()

    def test_tambah_murid_tanpa_field_wajib_ditolak(self, client):
        """❌ Buat murid tanpa field wajib harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_nm3", email="guru_nm3@test.com")
        db.close()

        token = get_token(client, "guru_nm3@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "nama": "Tanpa Email dan Password",
        }, headers=auth_header(token))

        assert response.status_code == 422


class TestUpdateMurid:

    def test_update_murid_berhasil(self, client):
        """✅ Pengajar bisa update profil murid."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_um1", email="guru_um1@test.com")
        db.close()

        token = get_token(client, "guru_um1@test.com")

        # Buat murid dulu
        murid_resp = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_update_1",
            "email_address": "murid_update_1@test.com",
            "password":      "Test1234!",
            "nama":          "Nama Awal",
            "usia":          14,
        }, headers=auth_header(token))
        murid_id = murid_resp.json()["id"]

        # Update murid
        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "nama":  "Nama Sudah Diupdate",
            "usia":  16,
            "level": "SMA Kelas 2",
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["nama"]  == "Nama Sudah Diupdate"
        assert data["usia"]  == 16
        assert data["level"] == "SMA Kelas 2"

    def test_update_murid_tidak_ditemukan(self, client):
        """❌ Update murid dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_um2", email="guru_um2@test.com")
        db.close()

        token = get_token(client, "guru_um2@test.com")
        response = client.put("/api/v1/kelas/murid/id-tidak-ada", json={
            "nama": "Apapun",
        }, headers=auth_header(token))

        assert response.status_code == 404

    def test_update_murid_partial_boleh(self, client):
        """✅ Update sebagian field saja (partial update) harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_um3", email="guru_um3@test.com")
        db.close()

        token = get_token(client, "guru_um3@test.com")
        murid_resp = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_partial",
            "email_address": "murid_partial@test.com",
            "password":      "Test1234!",
            "nama":          "Nama Partial",
            "usia":          13,
        }, headers=auth_header(token))
        murid_id = murid_resp.json()["id"]

        # Update hanya usia saja
        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "usia": 14,
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["usia"]  == 14
        assert response.json()["nama"]  == "Nama Partial"  # nama tidak berubah
