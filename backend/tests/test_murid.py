"""
test_murid.py
Unit testing untuk fitur Murid.
Mencakup: buat murid baru, update profil, validasi field,
          credit management, dan akses kontrol.

Pakai SQLite in-memory — tidak perlu PostgreSQL.

Cara jalankan:
    pytest tests/test_murid.py -v
"""
import os
import uuid
import pytest

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_murid.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_murid.db"

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
        if os.path.exists("./test_murid.db"):
            os.remove("./test_murid.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import KelasMurid, Kelas, Murid, Pengajar, Pengguna
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
        username=nama.replace(" ", "_").lower() + "_" + uid[:4],
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="pengajar",
    ))
    db.add(Pengajar(id=uid))
    db.commit()
    return db.query(Pengguna).filter(Pengguna.id == uid).first()


def buat_murid_db(db, nama="Murid Test", email="murid@test.com"):
    """Buat murid langsung ke DB tanpa lewat API."""
    from app.models.models import Pengguna, Murid
    from app.core.security import hash_password
    uid = str(uuid.uuid4())
    db.add(Pengguna(
        id=uid,
        username=nama.replace(" ", "_").lower() + "_" + uid[:4],
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="murid",
    ))
    db.add(Murid(id=uid, nama=nama, credit_total=0, credit_used=0))
    db.commit()
    return db.query(Murid).filter(Murid.id == uid).first()


def get_token(client, email, password="Test1234!"):
    resp = client.post("/api/v1/auth/login", json={
        "email_address": email,
        "password": password,
    })
    return resp.json().get("access_token", "")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def buat_murid_via_api(client, token, data=None):
    """Buat murid baru via API endpoint POST /kelas/murid/tambah."""
    payload = data or {
        "username":      "murid_api_" + str(uuid.uuid4())[:4],
        "email_address": "murid_api_" + str(uuid.uuid4())[:8] + "@test.com",
        "password":      "Test1234!",
        "nama":          "Murid API",
        "usia":          15,
        "level":         "SMA",
        "credit_total":  20,
    }
    return client.post("/api/v1/kelas/murid/tambah", json=payload, headers=auth_header(token))


# ═══════════════════════════════════════════════════════════════════════════════
# TEST BUAT MURID BARU
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuatMurid:

    def test_buat_murid_lengkap_berhasil(self, client):
        """✅ Buat murid dengan semua field terisi harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat1", email="guru_buat1@test.com")
        db.close()

        token = get_token(client, "guru_buat1@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "budi_santoso",
            "email_address": "budi@test.com",
            "password":      "Test1234!",
            "nama":          "Budi Santoso",
            "usia":          15,
            "level":         "SMA Kelas 1",
            "credit_total":  24,
        }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["nama"]         == "Budi Santoso"
        assert data["usia"]         == 15
        assert data["level"]        == "SMA Kelas 1"
        assert data["credit_total"] == 24
        assert data["credit_used"]  == 0
        assert data["username"]     == "budi_santoso"
        assert "id" in data

    def test_buat_murid_minimal_berhasil(self, client):
        """✅ Buat murid dengan field minimal (wajib saja) harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat2", email="guru_buat2@test.com")
        db.close()

        token = get_token(client, "guru_buat2@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_minimal",
            "email_address": "minimal@test.com",
            "password":      "Test1234!",
            "nama":          "Murid Minimal",
        }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["nama"]         == "Murid Minimal"
        assert data["usia"]         is None
        assert data["level"]        is None
        assert data["credit_total"] == 0   # default

    def test_buat_murid_credit_default_nol(self, client):
        """✅ credit_total default harus 0 jika tidak diisi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat3", email="guru_buat3@test.com")
        db.close()

        token = get_token(client, "guru_buat3@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_nocredit",
            "email_address": "nocredit@test.com",
            "password":      "Test1234!",
            "nama":          "Murid No Credit",
        }, headers=auth_header(token))

        assert response.status_code == 201
        assert response.json()["credit_total"] == 0
        assert response.json()["credit_used"]  == 0

    def test_buat_murid_credit_used_selalu_nol(self, client):
        """✅ credit_used harus selalu 0 saat murid pertama kali dibuat."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat4", email="guru_buat4@test.com")
        db.close()

        token = get_token(client, "guru_buat4@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_creditused",
            "email_address": "creditused@test.com",
            "password":      "Test1234!",
            "nama":          "Murid Credit Used",
            "credit_total":  30,
        }, headers=auth_header(token))

        assert response.status_code == 201
        assert response.json()["credit_used"] == 0

    def test_buat_murid_response_tidak_ada_password(self, client):
        """✅ Response tidak boleh mengandung password dalam bentuk apapun."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat5", email="guru_buat5@test.com")
        db.close()

        token = get_token(client, "guru_buat5@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_nopass",
            "email_address": "nopass@test.com",
            "password":      "Test1234!",
            "nama":          "Murid No Pass",
        }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert "password"        not in data
        assert "hashed_password" not in data


# ═══════════════════════════════════════════════════════════════════════════════
# TEST VALIDASI INPUT BUAT MURID
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidasiBuatMurid:

    def test_email_duplikat_ditolak(self, client):
        """❌ Email yang sudah terdaftar tidak boleh dipakai lagi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val1", email="guru_val1@test.com")
        buat_murid_db(db, nama="murid_existing", email="sudah_ada@test.com")
        db.close()

        token = get_token(client, "guru_val1@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "username_baru_unik",
            "email_address": "sudah_ada@test.com",
            "password":      "Test1234!",
            "nama":          "Nama Baru",
        }, headers=auth_header(token))

        assert response.status_code == 400
        assert "sudah terdaftar" in response.json()["detail"].lower()

    def test_tanpa_username_ditolak(self, client):
        """❌ Field username wajib diisi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val2", email="guru_val2@test.com")
        db.close()

        token = get_token(client, "guru_val2@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "email_address": "tanpa_username@test.com",
            "password":      "Test1234!",
            "nama":          "Tanpa Username",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tanpa_email_ditolak(self, client):
        """❌ Field email wajib diisi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val3", email="guru_val3@test.com")
        db.close()

        token = get_token(client, "guru_val3@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username": "tanpa_email",
            "password": "Test1234!",
            "nama":     "Tanpa Email",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tanpa_password_ditolak(self, client):
        """❌ Field password wajib diisi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val4", email="guru_val4@test.com")
        db.close()

        token = get_token(client, "guru_val4@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "tanpa_password",
            "email_address": "tanpa_password@test.com",
            "nama":          "Tanpa Password",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tanpa_nama_ditolak(self, client):
        """❌ Field nama wajib diisi."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val5", email="guru_val5@test.com")
        db.close()

        token = get_token(client, "guru_val5@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "tanpa_nama",
            "email_address": "tanpa_nama@test.com",
            "password":      "Test1234!",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_format_email_salah_ditolak(self, client):
        """❌ Format email yang tidak valid harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val6", email="guru_val6@test.com")
        db.close()

        token = get_token(client, "guru_val6@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "email_salah",
            "email_address": "ini-bukan-format-email",
            "password":      "Test1234!",
            "nama":          "Email Salah",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_body_kosong_ditolak(self, client):
        """❌ Request body kosong harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val7", email="guru_val7@test.com")
        db.close()

        token = get_token(client, "guru_val7@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={}, headers=auth_header(token))

        assert response.status_code == 422

    def test_murid_tidak_bisa_buat_murid(self, client):
        """❌ Murid tidak boleh membuat akun murid baru."""
        db = TestingSessionLocal()
        buat_murid_db(db, nama="murid_akses", email="murid_akses@test.com")
        db.close()

        token = get_token(client, "murid_akses@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_baru",
            "email_address": "murid_baru@test.com",
            "password":      "Test1234!",
            "nama":          "Murid Baru",
        }, headers=auth_header(token))

        assert response.status_code == 403

    def test_tanpa_token_ditolak(self, client):
        """❌ Buat murid tanpa token harus ditolak."""
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "tanpa_token",
            "email_address": "tanpa_token@test.com",
            "password":      "Test1234!",
            "nama":          "Tanpa Token",
        })
        assert response.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST UPDATE MURID
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateMurid:

    def test_update_nama_berhasil(self, client):
        """✅ Update nama murid harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd1", email="guru_upd1@test.com")
        db.close()

        token = get_token(client, "guru_upd1@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd1", "email_address": "murid_upd1@test.com",
            "password": "Test1234!", "nama": "Nama Lama",
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "nama": "Nama Baru Setelah Update",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nama"] == "Nama Baru Setelah Update"

    def test_update_usia_berhasil(self, client):
        """✅ Update usia murid harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd2", email="guru_upd2@test.com")
        db.close()

        token = get_token(client, "guru_upd2@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd2", "email_address": "murid_upd2@test.com",
            "password": "Test1234!", "nama": "Murid Usia", "usia": 14,
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "usia": 16,
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["usia"] == 16

    def test_update_level_berhasil(self, client):
        """✅ Update level murid harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd3", email="guru_upd3@test.com")
        db.close()

        token = get_token(client, "guru_upd3@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd3", "email_address": "murid_upd3@test.com",
            "password": "Test1234!", "nama": "Murid Level", "level": "SMA Kelas 1",
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "level": "SMA Kelas 2",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["level"] == "SMA Kelas 2"

    def test_update_credit_total_berhasil(self, client):
        """✅ Update credit_total murid harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd4", email="guru_upd4@test.com")
        db.close()

        token = get_token(client, "guru_upd4@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd4", "email_address": "murid_upd4@test.com",
            "password": "Test1234!", "nama": "Murid Credit", "credit_total": 10,
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "credit_total": 30,
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["credit_total"] == 30

    def test_update_semua_field_sekaligus(self, client):
        """✅ Update semua field sekaligus harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd5", email="guru_upd5@test.com")
        db.close()

        token = get_token(client, "guru_upd5@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd5", "email_address": "murid_upd5@test.com",
            "password": "Test1234!", "nama": "Sebelum Update",
            "usia": 13, "level": "SMP", "credit_total": 5,
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "nama":         "Sesudah Update",
            "usia":         15,
            "level":        "SMA",
            "credit_total": 20,
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["nama"]         == "Sesudah Update"
        assert data["usia"]         == 15
        assert data["level"]        == "SMA"
        assert data["credit_total"] == 20

    def test_update_partial_field_lain_tidak_berubah(self, client):
        """✅ Update sebagian field tidak boleh mengubah field lain yang tidak di-update."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd6", email="guru_upd6@test.com")
        db.close()

        token = get_token(client, "guru_upd6@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd6", "email_address": "murid_upd6@test.com",
            "password": "Test1234!", "nama": "Nama Tetap",
            "usia": 15, "level": "SMA", "credit_total": 20,
        }).json()["id"]

        # Update hanya usia
        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "usia": 16,
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["usia"]         == 16          # berubah
        assert data["nama"]         == "Nama Tetap"  # tidak berubah
        assert data["level"]        == "SMA"         # tidak berubah
        assert data["credit_total"] == 20            # tidak berubah

    def test_update_id_tidak_ada_return_404(self, client):
        """❌ Update murid dengan ID yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd7", email="guru_upd7@test.com")
        db.close()

        token = get_token(client, "guru_upd7@test.com")
        response = client.put("/api/v1/kelas/murid/id-tidak-ada-sama-sekali", json={
            "nama": "Apapun",
        }, headers=auth_header(token))

        assert response.status_code == 404

    def test_update_tanpa_token_ditolak(self, client):
        """❌ Update murid tanpa token harus ditolak."""
        response = client.put("/api/v1/kelas/murid/murid-id-apapun", json={
            "nama": "Tanpa Token",
        })
        assert response.status_code in (401, 403)

    def test_update_body_kosong_tetap_berhasil(self, client):
        """✅ Update dengan body kosong tidak mengubah data apapun."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd8", email="guru_upd8@test.com")
        db.close()

        token = get_token(client, "guru_upd8@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_upd8", "email_address": "murid_upd8@test.com",
            "password": "Test1234!", "nama": "Nama Tidak Berubah", "usia": 15,
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={},
                              headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nama"] == "Nama Tidak Berubah"
        assert response.json()["usia"] == 15


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA TERSIMPAN DENGAN BENAR DI DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class TestDataTersimpan:

    def test_murid_tersimpan_di_tabel_pengguna(self, client):
        """✅ Murid harus tersimpan di tabel pengguna dengan tipe_pengguna='murid'."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_db1", email="guru_db1@test.com")
        db.close()

        token = get_token(client, "guru_db1@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_db_check",
            "email_address": "murid_db_check@test.com",
            "password":      "Test1234!",
            "nama":          "Murid DB Check",
        }, headers=auth_header(token))

        assert response.status_code == 201
        murid_id = response.json()["id"]

        # Cek langsung di database
        db = TestingSessionLocal()
        from app.models.models import Pengguna, Murid
        pengguna = db.query(Pengguna).filter(Pengguna.id == murid_id).first()
        murid    = db.query(Murid).filter(Murid.id == murid_id).first()
        db.close()

        assert pengguna is not None
        assert pengguna.tipe_pengguna == "murid"
        assert pengguna.email_address == "murid_db_check@test.com"
        assert murid is not None
        assert murid.nama == "Murid DB Check"

    def test_password_murid_tersimpan_sebagai_hash(self, client):
        """✅ Password murid di database harus berbentuk hash bcrypt."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_db2", email="guru_db2@test.com")
        db.close()

        token = get_token(client, "guru_db2@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_hashcheck",
            "email_address": "murid_hashcheck@test.com",
            "password":      "PasswordRahasia123!",
            "nama":          "Murid Hash Check",
        }, headers=auth_header(token))

        murid_id = response.json()["id"]

        db = TestingSessionLocal()
        from app.models.models import Pengguna
        pengguna = db.query(Pengguna).filter(Pengguna.id == murid_id).first()
        db.close()

        # Password tidak boleh tersimpan sebagai plaintext
        assert pengguna.hashed_password != "PasswordRahasia123!"
        assert pengguna.hashed_password.startswith("$2b$")

    def test_murid_bisa_login_setelah_dibuat(self, client):
        """✅ Murid yang baru dibuat harus langsung bisa login."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_db3", email="guru_db3@test.com")
        db.close()

        token = get_token(client, "guru_db3@test.com")
        client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_login_test",
            "email_address": "murid_login_test@test.com",
            "password":      "Test1234!",
            "nama":          "Murid Login Test",
        }, headers=auth_header(token))

        # Murid langsung coba login
        login_resp = client.post("/api/v1/auth/login", json={
            "email_address": "murid_login_test@test.com",
            "password":      "Test1234!",
        })

        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()
        assert login_resp.json()["tipe_pengguna"] == "murid"

    def test_update_tersimpan_di_database(self, client):
        """✅ Perubahan data setelah update harus tersimpan di database."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_db4", email="guru_db4@test.com")
        db.close()

        token = get_token(client, "guru_db4@test.com")
        murid_id = buat_murid_via_api(client, token, {
            "username": "murid_db4", "email_address": "murid_db4@test.com",
            "password": "Test1234!", "nama": "Nama Sebelum", "usia": 13,
        }).json()["id"]

        client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "nama": "Nama Sesudah", "usia": 15,
        }, headers=auth_header(token))

        # Cek langsung di database
        db = TestingSessionLocal()
        from app.models.models import Murid
        murid = db.query(Murid).filter(Murid.id == murid_id).first()
        db.close()

        assert murid.nama == "Nama Sesudah"
        assert murid.usia == 15


# ═══════════════════════════════════════════════════════════════════════════════
# TEST AKSES KONTROL
# ═══════════════════════════════════════════════════════════════════════════════

class TestAksesKontrol:

    def test_murid_tidak_bisa_update_murid_lain(self, client):
        """❌ Murid tidak bisa mengupdate profil murid lain."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_akses1", email="guru_akses1@test.com")
        murid2 = buat_murid_db(db, nama="murid_target", email="murid_target@test.com")
        db.close()

        # Login sebagai murid (bukan pengajar)
        db = TestingSessionLocal()
        buat_murid_db(db, nama="murid_penyerang", email="murid_penyerang@test.com")
        db.close()

        token_murid = get_token(client, "murid_penyerang@test.com")
        response = client.put(f"/api/v1/kelas/murid/{murid2.id}", json={
            "nama": "Dicuri",
        }, headers=auth_header(token_murid))

        # Murid tidak punya akses (bukan pengajar)
        assert response.status_code == 403

    def test_tanpa_token_tidak_bisa_update(self, client):
        """❌ Update murid tanpa token harus ditolak."""
        db = TestingSessionLocal()
        murid = buat_murid_db(db, nama="murid_notok", email="murid_notok@test.com")
        db.close()

        response = client.put(f"/api/v1/kelas/murid/{murid.id}", json={
            "nama": "Tanpa Token",
        })
        assert response.status_code in (401, 403)

    def test_token_palsu_tidak_bisa_buat_murid(self, client):
        """❌ Token palsu tidak bisa dipakai untuk buat murid."""
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "murid_tokenpalsu",
            "email_address": "tokenpalsu@test.com",
            "password":      "Test1234!",
            "nama":          "Token Palsu",
        }, headers={"Authorization": "Bearer token.palsu.banget"})

        assert response.status_code == 401
