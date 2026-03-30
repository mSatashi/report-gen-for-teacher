"""
test_auth.py
Unit testing untuk fitur Auth (register & login).
Pakai SQLite in-memory — tidak perlu PostgreSQL sama sekali.
"""
import os
import pytest

# ── PENTING: set env sebelum import apapun dari app ──────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_temp.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_temp.db"

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
    """Buat semua tabel di SQLite sebelum test jalan."""
    import app.core.database as db_module
    db_module.engine       = engine_test
    db_module.SessionLocal = TestingSessionLocal

    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)
    # Tutup semua koneksi dulu sebelum hapus file (fix PermissionError Windows)
    engine_test.dispose()
    try:
        if os.path.exists("./test_temp.db"):
            os.remove("./test_temp.db")
    except PermissionError:
        pass  # Windows kadang masih lock, tidak apa-apa diabaikan


@pytest.fixture(autouse=True)
def clean_tables():
    """Bersihkan data sebelum tiap test."""
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import Pengguna, Pengajar, Murid
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


# ── Helpers ───────────────────────────────────────────────────────────────────

def register_pengajar(client, email="guru@test.com", username="guru_test", password="Test1234!"):
    return client.post("/api/v1/auth/register", json={
        "username": username,
        "email_address": email,
        "password": password,
        "tipe_pengguna": "pengajar",
    })


def register_murid(client, email="murid@test.com", username="murid_test", password="Test1234!"):
    return client.post("/api/v1/auth/register", json={
        "username": username,
        "email_address": email,
        "password": password,
        "tipe_pengguna": "murid",
    })


def login(client, email, password):
    return client.post("/api/v1/auth/login", json={
        "email_address": email,
        "password": password,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# TEST REGISTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegister:

    def test_register_pengajar_berhasil(self, client):
        """✅ Registrasi pengajar dengan data valid harus berhasil."""
        response = register_pengajar(client)

        assert response.status_code == 201
        data = response.json()
        assert data["tipe"] == "pengajar"
        assert "user_id" in data
        assert data["message"] == "Registrasi berhasil"

    def test_register_murid_berhasil(self, client):
        """✅ Registrasi murid dengan data valid harus berhasil."""
        response = register_murid(client)

        assert response.status_code == 201
        data = response.json()
        assert data["tipe"] == "murid"
        assert "user_id" in data

    def test_register_email_duplikat(self, client):
        """❌ Registrasi dengan email yang sudah dipakai harus gagal."""
        register_pengajar(client, email="duplikat@test.com", username="user_pertama")
        response = register_pengajar(client, email="duplikat@test.com", username="user_kedua")

        assert response.status_code == 400
        assert "Email sudah terdaftar" in response.json()["detail"]

    def test_register_username_duplikat(self, client):
        """❌ Registrasi dengan username yang sama harus gagal."""
        register_pengajar(client, email="email1@test.com", username="username_sama")
        response = register_pengajar(client, email="email2@test.com", username="username_sama")

        assert response.status_code == 400
        assert "Username sudah digunakan" in response.json()["detail"]

    def test_register_tipe_tidak_valid(self, client):
        """❌ Tipe pengguna selain pengajar/murid harus ditolak."""
        response = client.post("/api/v1/auth/register", json={
            "username": "user_invalid",
            "email_address": "invalid@test.com",
            "password": "Test1234!",
            "tipe_pengguna": "admin",
        })
        assert response.status_code == 422

    def test_register_tanpa_email(self, client):
        """❌ Registrasi tanpa email harus gagal."""
        response = client.post("/api/v1/auth/register", json={
            "username": "user_tanpa_email",
            "password": "Test1234!",
            "tipe_pengguna": "pengajar",
        })
        assert response.status_code == 422

    def test_register_tanpa_password(self, client):
        """❌ Registrasi tanpa password harus gagal."""
        response = client.post("/api/v1/auth/register", json={
            "username": "user_tanpa_pass",
            "email_address": "tanpapass@test.com",
            "tipe_pengguna": "pengajar",
        })
        assert response.status_code == 422

    def test_register_format_email_salah(self, client):
        """❌ Format email yang salah harus ditolak."""
        response = client.post("/api/v1/auth/register", json={
            "username": "user_email_salah",
            "email_address": "ini-bukan-email",
            "password": "Test1234!",
            "tipe_pengguna": "pengajar",
        })
        assert response.status_code == 422

    def test_register_body_kosong(self, client):
        """❌ Body kosong harus ditolak."""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# TEST LOGIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestLogin:

    def test_login_pengajar_berhasil(self, client):
        """✅ Login dengan kredensial benar harus dapat token."""
        register_pengajar(client, email="login_guru@test.com", username="login_guru")
        response = login(client, "login_guru@test.com", "Test1234!")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["tipe_pengguna"] == "pengajar"
        assert "user_id" in data

    def test_login_murid_berhasil(self, client):
        """✅ Login murid dengan kredensial benar harus berhasil."""
        register_murid(client, email="login_murid@test.com", username="login_murid")
        response = login(client, "login_murid@test.com", "Test1234!")

        assert response.status_code == 200
        assert response.json()["tipe_pengguna"] == "murid"

    def test_login_password_salah(self, client):
        """❌ Password salah harus ditolak."""
        register_pengajar(client, email="pass_salah@test.com", username="pass_salah")
        response = login(client, "pass_salah@test.com", "PasswordSalah!")

        assert response.status_code == 401
        assert "Email atau password salah" in response.json()["detail"]

    def test_login_email_tidak_terdaftar(self, client):
        """❌ Email yang tidak terdaftar harus ditolak."""
        response = login(client, "tidakterdaftar@test.com", "Test1234!")
        assert response.status_code == 401

    def test_login_token_bisa_dipakai(self, client):
        """✅ Token dari login harus bisa akses endpoint yang butuh auth."""
        register_pengajar(client, email="token_test@test.com", username="token_test")
        login_resp = login(client, "token_test@test.com", "Test1234!")

        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        response = client.get(
            "/api/v1/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code != 401

    def test_akses_tanpa_token_ditolak(self, client):
        """❌ Akses endpoint tanpa token harus ditolak (401 atau 403)."""
        response = client.get("/api/v1/dashboard")
        # FastAPI HTTPBearer return 403 jika header tidak ada sama sekali
        assert response.status_code in (401, 403)

    def test_token_palsu_ditolak(self, client):
        """❌ Token palsu harus ditolak."""
        response = client.get(
            "/api/v1/dashboard",
            headers={"Authorization": "Bearer ini.token.palsu"},
        )
        assert response.status_code == 401

    def test_login_body_kosong(self, client):
        """❌ Login dengan body kosong harus ditolak."""
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_tanpa_password(self, client):
        """❌ Login tanpa password harus ditolak."""
        response = client.post("/api/v1/auth/login", json={
            "email_address": "guru@test.com",
        })
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# TEST SECURITY — Password & JWT
# ═══════════════════════════════════════════════════════════════════════════════

class TestSecurity:

    def test_password_tidak_disimpan_plaintext(self, client):
        """✅ Password di database harus hash bcrypt, bukan teks asli."""
        register_pengajar(client, email="hash_test@test.com", username="hash_test")

        db = TestingSessionLocal()
        try:
            from app.models.models import Pengguna
            user = db.query(Pengguna).filter(
                Pengguna.email_address == "hash_test@test.com"
            ).first()
        finally:
            db.close()

        assert user is not None, "User tidak tersimpan di database"
        assert user.hashed_password != "Test1234!"
        assert user.hashed_password.startswith("$2b$")  # format hash bcrypt

    def test_verify_password_benar(self):
        """✅ Verifikasi password yang benar harus return True."""
        from app.core.security import hash_password, verify_password

        hashed = hash_password("passwordku123")
        assert verify_password("passwordku123", hashed) is True

    def test_verify_password_salah(self):
        """❌ Verifikasi password yang salah harus return False."""
        from app.core.security import hash_password, verify_password

        hashed = hash_password("passwordku123")
        assert verify_password("passwordsalah", hashed) is False

    def test_jwt_token_berisi_data_benar(self):
        """✅ Token yang dibuat harus bisa di-decode dan isinya benar."""
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token({"sub": "user-123", "tipe": "pengajar"})
        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["tipe"] == "pengajar"

    def test_jwt_token_palsu_gagal_decode(self):
        """❌ Token palsu tidak boleh bisa di-decode."""
        from app.core.security import decode_access_token

        assert decode_access_token("ini.token.palsu") is None

    def test_jwt_token_expired_ditolak(self):
        """❌ Token yang sudah expired harus ditolak."""
        from datetime import timedelta
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token(
            data={"sub": "user-expired"},
            expires_delta=timedelta(minutes=-1),  # langsung expired
        )
        assert decode_access_token(token) is None
