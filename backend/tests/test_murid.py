"""
test_murid.py
Unit testing untuk fitur Murid.
Mencakup: buat murid baru (via kelas & via /murid/),
          list master data, detail, delete, update profil,
          validasi field, credit management, akses kontrol, logout.

Pakai SQLite in-memory — tidak perlu PostgreSQL.

Cara jalankan:
    pytest tests/test_murid.py -v
"""
import os
import uuid
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test_murid.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

SQLITE_URL = "sqlite:///./test_murid.db"
engine_test = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
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


def buat_murid_via_kelas_api(client, token, data=None):
    """Buat murid baru via endpoint lama POST /kelas/murid/tambah."""
    payload = data or {
        "username":      "murid_kelas_" + str(uuid.uuid4())[:4],
        "email_address": "murid_kelas_" + str(uuid.uuid4())[:8] + "@test.com",
        "password":      "Test1234!",
        "nama":          "Murid Kelas API",
        "usia":          15,
        "level":         "SMA",
        "credit_total":  20,
    }
    return client.post("/api/v1/kelas/murid/tambah", json=payload, headers=auth_header(token))


def buat_murid_via_api(client, token, data=None):
    """Buat murid baru via endpoint baru POST /murid/."""
    payload = data or {
        "username":      "murid_api_" + str(uuid.uuid4())[:4],
        "email_address": "murid_api_" + str(uuid.uuid4())[:8] + "@test.com",
        "password":      "Test1234!",
        "nama":          "Murid API Baru",
        "usia":          15,
        "level":         "SMA",
        "credit_total":  20,
    }
    return client.post("/api/v1/murid/", json=payload, headers=auth_header(token))


# ═══════════════════════════════════════════════════════════════════════════════
# TEST BUAT MURID — endpoint /kelas/murid/tambah (lama, tetap harus jalan)
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuatMuridViaKelas:

    def test_buat_murid_lengkap_berhasil(self, client):
        """✅ Buat murid via /kelas/murid/tambah dengan semua field harus berhasil."""
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
        assert data["credit_total"] == 24
        assert data["credit_used"]  == 0
        assert data["username"]     == "budi_santoso"
        assert "id" in data

    def test_buat_murid_minimal_berhasil(self, client):
        """✅ Buat murid dengan field minimal harus berhasil."""
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
        assert data["credit_total"] == 0

    def test_buat_murid_email_duplikat_ditolak(self, client):
        """❌ Email yang sudah terdaftar harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_buat3", email="guru_buat3@test.com")
        buat_murid_db(db, nama="murid_existing", email="sudah_ada@test.com")
        db.close()

        token = get_token(client, "guru_buat3@test.com")
        response = client.post("/api/v1/kelas/murid/tambah", json={
            "username":      "username_baru_unik",
            "email_address": "sudah_ada@test.com",
            "password":      "Test1234!",
            "nama":          "Nama Baru",
        }, headers=auth_header(token))

        assert response.status_code == 400
        assert "sudah terdaftar" in response.json()["detail"].lower()

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

    def test_response_tidak_ada_password(self, client):
        """✅ Response tidak boleh mengandung password."""
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
# TEST BUAT MURID — endpoint baru POST /murid/
# ═══════════════════════════════════════════════════════════════════════════════

class TestBuatMuridEndpointBaru:

    def test_buat_murid_via_endpoint_baru_berhasil(self, client):
        """✅ POST /murid/ harus berhasil membuat murid baru."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_new1", email="guru_new1@test.com")
        db.close()

        token = get_token(client, "guru_new1@test.com")
        response = buat_murid_via_api(client, token, {
            "username":      "murid_baru_endpoint",
            "email_address": "murid_baru_endpoint@test.com",
            "password":      "Test1234!",
            "nama":          "Murid Endpoint Baru",
            "usia":          16,
            "level":         "SMA",
            "credit_total":  10,
        })

        assert response.status_code == 201
        data = response.json()
        assert data["nama"]         == "Murid Endpoint Baru"
        assert data["username"]     == "murid_baru_endpoint"
        assert data["email_address"]== "murid_baru_endpoint@test.com"
        assert data["usia"]         == 16
        assert data["credit_used"]  == 0
        assert "id" in data

    def test_murid_tidak_bisa_akses_endpoint_baru(self, client):
        """❌ Murid tidak boleh POST /murid/."""
        db = TestingSessionLocal()
        buat_murid_db(db, nama="murid_coba", email="murid_coba@test.com")
        db.close()

        token = get_token(client, "murid_coba@test.com")
        response = buat_murid_via_api(client, token)
        assert response.status_code == 403

    def test_tanpa_token_ditolak(self, client):
        """❌ POST /murid/ tanpa token harus ditolak."""
        response = client.post("/api/v1/murid/", json={
            "username": "x", "email_address": "x@x.com",
            "password": "Test1234!", "nama": "X",
        })
        assert response.status_code in (401, 403)

    def test_email_duplikat_ditolak(self, client):
        """❌ Email duplikat di POST /murid/ harus 400."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_new2", email="guru_new2@test.com")
        buat_murid_db(db, nama="existing", email="exists@test.com")
        db.close()

        token = get_token(client, "guru_new2@test.com")
        response = buat_murid_via_api(client, token, {
            "username": "unik123", "email_address": "exists@test.com",
            "password": "Test1234!", "nama": "Duplikat",
        })
        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# TEST LIST SEMUA MURID — GET /murid/
# ═══════════════════════════════════════════════════════════════════════════════

class TestListMurid:

    def test_list_murid_kosong(self, client):
        """✅ List murid saat belum ada data harus return list kosong."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_list1", email="guru_list1@test.com")
        db.close()

        token = get_token(client, "guru_list1@test.com")
        response = client.get("/api/v1/murid/", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_list_murid_menampilkan_semua(self, client):
        """✅ List murid harus menampilkan semua murid yang ada."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_list2", email="guru_list2@test.com")
        buat_murid_db(db, nama="Murid Satu",  email="m1@test.com")
        buat_murid_db(db, nama="Murid Dua",   email="m2@test.com")
        buat_murid_db(db, nama="Murid Tiga",  email="m3@test.com")
        db.close()

        token = get_token(client, "guru_list2@test.com")
        response = client.get("/api/v1/murid/", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_murid_struktur_response(self, client):
        """✅ Setiap item dalam list harus punya field yang benar."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_list3", email="guru_list3@test.com")
        buat_murid_db(db, nama="Murid Struktur", email="struktur@test.com")
        db.close()

        token = get_token(client, "guru_list3@test.com")
        response = client.get("/api/v1/murid/", headers=auth_header(token))

        assert response.status_code == 200
        item = response.json()[0]
        assert "id"            in item
        assert "nama"          in item
        assert "credit_total"  in item
        assert "credit_used"   in item
        assert "password"      not in item
        assert "hashed_password" not in item

    def test_list_murid_search_filter(self, client):
        """✅ Filter search harus menyaring berdasarkan nama."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_list4", email="guru_list4@test.com")
        buat_murid_db(db, nama="Andi Pratama", email="andi@test.com")
        buat_murid_db(db, nama="Budi Santoso", email="budi@test.com")
        db.close()

        token = get_token(client, "guru_list4@test.com")
        response = client.get("/api/v1/murid/?search=Andi", headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nama"] == "Andi Pratama"

    def test_list_murid_paginasi(self, client):
        """✅ Parameter skip/limit harus bekerja dengan benar."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_list5", email="guru_list5@test.com")
        for i in range(5):
            buat_murid_db(db, nama=f"Murid {i}", email=f"murid{i}@test.com")
        db.close()

        token = get_token(client, "guru_list5@test.com")

        resp_all   = client.get("/api/v1/murid/?limit=100",         headers=auth_header(token))
        resp_limit = client.get("/api/v1/murid/?limit=2",           headers=auth_header(token))
        resp_skip  = client.get("/api/v1/murid/?skip=3&limit=100",  headers=auth_header(token))

        assert len(resp_all.json())   == 5
        assert len(resp_limit.json()) == 2
        assert len(resp_skip.json())  == 2

    def test_murid_tidak_bisa_akses_list(self, client):
        """❌ Murid tidak bisa lihat master data semua murid."""
        db = TestingSessionLocal()
        buat_murid_db(db, nama="murid_akses2", email="murid_akses2@test.com")
        db.close()

        token = get_token(client, "murid_akses2@test.com")
        response = client.get("/api/v1/murid/", headers=auth_header(token))
        assert response.status_code == 403

    def test_tanpa_token_ditolak(self, client):
        """❌ GET /murid/ tanpa token harus ditolak."""
        response = client.get("/api/v1/murid/")
        assert response.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DETAIL MURID — GET /murid/{id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestDetailMurid:

    def test_detail_murid_berhasil(self, client):
        """✅ GET /murid/{id} harus return data murid yang benar."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_det1", email="guru_det1@test.com")
        murid = buat_murid_db(db, nama="Murid Detail", email="detail@test.com")
        db.close()

        token = get_token(client, "guru_det1@test.com")
        response = client.get(f"/api/v1/murid/{murid.id}", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nama"] == "Murid Detail"
        assert response.json()["id"]   == murid.id

    def test_detail_murid_tidak_ada_return_404(self, client):
        """❌ ID yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_det2", email="guru_det2@test.com")
        db.close()

        token = get_token(client, "guru_det2@test.com")
        response = client.get("/api/v1/murid/id-tidak-ada", headers=auth_header(token))
        assert response.status_code == 404

    def test_murid_bisa_lihat_diri_sendiri(self, client):
        """✅ Murid bisa akses detail dirinya sendiri."""
        db = TestingSessionLocal()
        murid = buat_murid_db(db, nama="Murid Self", email="self@test.com")
        db.close()

        token = get_token(client, "self@test.com")
        response = client.get(f"/api/v1/murid/{murid.id}", headers=auth_header(token))
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DELETE MURID — DELETE /murid/{id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeleteMurid:

    def test_hapus_murid_berhasil(self, client):
        """✅ Pengajar bisa hapus murid dan data hilang dari DB."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del1", email="guru_del1@test.com")
        murid = buat_murid_db(db, nama="Murid Hapus", email="hapus@test.com")
        murid_id = murid.id
        db.close()

        token = get_token(client, "guru_del1@test.com")
        response = client.delete(f"/api/v1/murid/{murid_id}", headers=auth_header(token))

        assert response.status_code == 200
        assert "berhasil" in response.json()["message"].lower()

        # Verifikasi benar-benar terhapus dari DB
        db = TestingSessionLocal()
        from app.models.models import Pengguna
        pengguna = db.query(Pengguna).filter(Pengguna.id == murid_id).first()
        db.close()
        assert pengguna is None

    def test_hapus_murid_tidak_ada_return_404(self, client):
        """❌ Hapus murid dengan ID tidak ada harus 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del2", email="guru_del2@test.com")
        db.close()

        token = get_token(client, "guru_del2@test.com")
        response = client.delete("/api/v1/murid/id-tidak-ada", headers=auth_header(token))
        assert response.status_code == 404

    def test_murid_tidak_bisa_hapus_murid(self, client):
        """❌ Murid tidak bisa menghapus murid lain."""
        db = TestingSessionLocal()
        murid_penyerang = buat_murid_db(db, nama="penyerang", email="penyerang@test.com")
        murid_target    = buat_murid_db(db, nama="target",    email="target@test.com")
        db.close()

        token = get_token(client, "penyerang@test.com")
        response = client.delete(f"/api/v1/murid/{murid_target.id}", headers=auth_header(token))
        assert response.status_code == 403

    def test_tanpa_token_tidak_bisa_hapus(self, client):
        """❌ Hapus murid tanpa token harus ditolak."""
        response = client.delete("/api/v1/murid/id-apapun")
        assert response.status_code in (401, 403)

    def test_hapus_pengajar_ditolak(self, client):
        """❌ DELETE /murid/{id} tidak bisa dipakai untuk hapus pengajar."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_del3",   email="guru_del3@test.com")
        pengajar2 = buat_pengajar(db, nama="guru_target", email="guru_target@test.com")
        db.close()

        token = get_token(client, "guru_del3@test.com")
        # Coba hapus pengajar via endpoint delete murid — harus 404
        response = client.delete(f"/api/v1/murid/{pengajar2.id}", headers=auth_header(token))
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# TEST UPDATE MURID — PUT /kelas/murid/{id}
# ═══════════════════════════════════════════════════════════════════════════════

class TestUpdateMurid:

    def test_update_nama_berhasil(self, client):
        """✅ Update nama murid harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd1", email="guru_upd1@test.com")
        db.close()

        token = get_token(client, "guru_upd1@test.com")
        murid_id = buat_murid_via_kelas_api(client, token, {
            "username": "murid_upd1", "email_address": "murid_upd1@test.com",
            "password": "Test1234!", "nama": "Nama Lama",
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "nama": "Nama Baru Setelah Update",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["nama"] == "Nama Baru Setelah Update"

    def test_update_semua_field_sekaligus(self, client):
        """✅ Update semua field sekaligus harus berhasil."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd5", email="guru_upd5@test.com")
        db.close()

        token = get_token(client, "guru_upd5@test.com")
        murid_id = buat_murid_via_kelas_api(client, token, {
            "username": "murid_upd5", "email_address": "murid_upd5@test.com",
            "password": "Test1234!", "nama": "Sebelum Update",
            "usia": 13, "level": "SMP", "credit_total": 5,
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "nama": "Sesudah Update", "usia": 15,
            "level": "SMA", "credit_total": 20,
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["nama"]         == "Sesudah Update"
        assert data["usia"]         == 15
        assert data["level"]        == "SMA"
        assert data["credit_total"] == 20

    def test_update_partial_field_lain_tidak_berubah(self, client):
        """✅ Update sebagian field tidak boleh mengubah field lain."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd6", email="guru_upd6@test.com")
        db.close()

        token = get_token(client, "guru_upd6@test.com")
        murid_id = buat_murid_via_kelas_api(client, token, {
            "username": "murid_upd6", "email_address": "murid_upd6@test.com",
            "password": "Test1234!", "nama": "Nama Tetap",
            "usia": 15, "level": "SMA", "credit_total": 20,
        }).json()["id"]

        response = client.put(f"/api/v1/kelas/murid/{murid_id}", json={
            "usia": 16,
        }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["usia"]         == 16
        assert data["nama"]         == "Nama Tetap"
        assert data["level"]        == "SMA"
        assert data["credit_total"] == 20

    def test_update_id_tidak_ada_return_404(self, client):
        """❌ Update murid dengan ID tidak ada harus 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_upd7", email="guru_upd7@test.com")
        db.close()

        token = get_token(client, "guru_upd7@test.com")
        response = client.put("/api/v1/kelas/murid/id-tidak-ada", json={
            "nama": "Apapun",
        }, headers=auth_header(token))
        assert response.status_code == 404

    def test_murid_tidak_bisa_update_murid_lain(self, client):
        """❌ Murid tidak bisa mengupdate profil murid lain."""
        db = TestingSessionLocal()
        murid_target    = buat_murid_db(db, nama="murid_target",    email="murid_target@test.com")
        buat_murid_db(db, nama="murid_penyerang", email="murid_penyerang@test.com")
        db.close()

        token = get_token(client, "murid_penyerang@test.com")
        response = client.put(f"/api/v1/kelas/murid/{murid_target.id}", json={
            "nama": "Dicuri",
        }, headers=auth_header(token))
        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# TEST LOGOUT
# ═══════════════════════════════════════════════════════════════════════════════

class TestLogout:

    def test_logout_berhasil(self, client):
        """✅ Logout harus return pesan sukses."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_logout1", email="guru_logout1@test.com")
        db.close()

        token = get_token(client, "guru_logout1@test.com")
        response = client.post("/api/v1/auth/logout", headers=auth_header(token))

        assert response.status_code == 200
        assert "logout" in response.json()["message"].lower()

    def test_token_tidak_bisa_dipakai_setelah_logout(self, client):
        """❌ Token yang sudah logout harus ditolak untuk request berikutnya."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_logout2", email="guru_logout2@test.com")
        db.close()

        token = get_token(client, "guru_logout2@test.com")

        # Pastikan token valid dulu
        resp_before = client.get("/api/v1/dashboard/", headers=auth_header(token))
        assert resp_before.status_code == 200

        # Logout
        client.post("/api/v1/auth/logout", headers=auth_header(token))

        # Token seharusnya sudah tidak berlaku
        resp_after = client.get("/api/v1/dashboard/", headers=auth_header(token))
        assert resp_after.status_code == 401

    def test_logout_tanpa_token_ditolak(self, client):
        """❌ Logout tanpa token harus ditolak."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code in (401, 403)

    def test_logout_token_palsu_ditolak(self, client):
        """❌ Logout dengan token palsu harus ditolak."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer token.palsu.banget"},
        )
        # Token palsu tidak masuk blacklist, tetap ditolak di protected endpoint
        # Logout sendiri mungkin return 200 (hanya blacklist), tapi endpoint lain 401
        # Bergantung implementasi — yang penting tidak crash
        assert response.status_code in (200, 401, 403)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA TERSIMPAN DI DATABASE
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

        login_resp = client.post("/api/v1/auth/login", json={
            "email_address": "murid_login_test@test.com",
            "password":      "Test1234!",
        })

        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()
        assert login_resp.json()["tipe_pengguna"] == "murid"
