"""
test_diagnostic.py
Unit testing untuk fitur Tes Diagnostik Awal (F008).
Mencakup: simpan hasil diagnostik, get diagnostik per murid,
          inisialisasi BKT P(L0), validasi skor, akses kontrol.

Pakai SQLite in-memory — tidak perlu PostgreSQL.

Cara jalankan:
    pytest tests/test_diagnostic.py -v
"""
import os
import uuid
import pytest
from datetime import datetime

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_diagnostic.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_diagnostic.db"

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
        if os.path.exists("./test_diagnostic.db"):
            os.remove("./test_diagnostic.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import (
            DiagnosticResult, KnowledgeState,
            KelasMusrid, Kelas, Murid, Pengajar, Pengguna,
        )
        db.query(DiagnosticResult).delete()
        db.query(KnowledgeState).delete()
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
        id=uid,
        username=nama.replace(" ", "_") + uid[:4],
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
        username=nama.replace(" ", "_") + uid[:4],
        email_address=email,
        hashed_password=hash_password("Test1234!"),
        tipe_pengguna="murid",
    ))
    db.add(Murid(id=uid, nama=nama))
    db.commit()
    return db.query(Murid).filter(Murid.id == uid).first()


def buat_kelas(db, pengajar_id, nama="Kelas Test"):
    from app.models.models import Kelas
    k = Kelas(
        id=str(uuid.uuid4()),
        nama=nama,
        mata_pelajaran="Matematika",
        pengajar_id=pengajar_id,
        kredit=20,
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


def buat_diagnostic_db(db, murid_id, topik="Aljabar",
                        skor=75.0, kelas_id=None):
    """Buat diagnostic result langsung ke DB."""
    from app.models.models import DiagnosticResult
    diag = DiagnosticResult(
        id=str(uuid.uuid4()),
        murid_id=murid_id,
        kelas_id=kelas_id,
        topik=topik,
        skor=skor,
        diagnostic_score=skor,
        created_at=datetime.utcnow(),
    )
    db.add(diag)
    db.commit()
    db.refresh(diag)
    return diag


def get_token(client, email, password="Test1234!"):
    resp = client.post("/api/v1/auth/login", json={
        "email_address": email,
        "password": password,
    })
    return resp.json().get("access_token", "")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def payload_diagnostic(murid_id, topik="Aljabar",
                        skor=75.0, kelas_id=None):
    data = {
        "murid_id":         murid_id,
        "topik":            topik,
        "diagnostic_score": skor,
    }
    if kelas_id:
        data["kelas_id"] = kelas_id
    return data


# ═══════════════════════════════════════════════════════════════════════════════
# TEST SIMPAN DIAGNOSTIK (POST)
# ═══════════════════════════════════════════════════════════════════════════════

class TestSimpanDiagnostic:

    def test_simpan_diagnostic_berhasil(self, client):
        """✅ Simpan hasil diagnostik dengan data valid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add1", email="guru_add1@test.com")
        murid = buat_murid(db, nama="murid_add1", email="murid_add1@test.com")
        db.close()

        token    = get_token(client, "guru_add1@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Aljabar", 75.0),
                               headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["murid_id"]        == murid.id
        assert data["topik"]           == "Aljabar"
        assert data["diagnostic_score"]== 75.0
        assert "id"         in data
        assert "created_at" in data

    def test_simpan_diagnostic_dengan_kelas_berhasil(self, client):
        """✅ Simpan diagnostik dengan kelas_id opsional harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add2", email="guru_add2@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_add2", email="murid_add2@test.com")
        db.close()

        token    = get_token(client, "guru_add2@test.com")
        response = client.post(
            "/api/v1/diagnostic/",
            json=payload_diagnostic(murid.id, "Geometri", 80.0, kelas_id=kelas.id),
            headers=auth_header(token),
        )

        assert response.status_code == 201
        assert response.json()["murid_id"] == murid.id

    def test_simpan_diagnostic_skor_nol(self, client):
        """✅ Skor 0 (nilai minimum valid) harus berhasil disimpan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add3", email="guru_add3@test.com")
        murid = buat_murid(db, nama="murid_add3", email="murid_add3@test.com")
        db.close()

        token    = get_token(client, "guru_add3@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Statistika", 0.0),
                               headers=auth_header(token))

        assert response.status_code == 201
        assert response.json()["diagnostic_score"] == 0.0

    def test_simpan_diagnostic_skor_100(self, client):
        """✅ Skor 100 (nilai maksimum valid) harus berhasil disimpan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add4", email="guru_add4@test.com")
        murid = buat_murid(db, nama="murid_add4", email="murid_add4@test.com")
        db.close()

        token    = get_token(client, "guru_add4@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Kalkulus", 100.0),
                               headers=auth_header(token))

        assert response.status_code == 201
        assert response.json()["diagnostic_score"] == 100.0

    def test_simpan_diagnostic_skor_desimal(self, client):
        """✅ Skor desimal (misal 85.5) harus berhasil disimpan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add5", email="guru_add5@test.com")
        murid = buat_murid(db, nama="murid_add5", email="murid_add5@test.com")
        db.close()

        token    = get_token(client, "guru_add5@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Fisika", 85.5),
                               headers=auth_header(token))

        assert response.status_code == 201
        assert response.json()["diagnostic_score"] == 85.5

    def test_simpan_beberapa_topik_berbeda(self, client):
        """✅ Satu murid boleh punya diagnostik untuk banyak topik berbeda."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_add6", email="guru_add6@test.com")
        murid = buat_murid(db, nama="murid_add6", email="murid_add6@test.com")
        db.close()

        token = get_token(client, "guru_add6@test.com")
        for topik, skor in [("Aljabar", 80.0), ("Geometri", 65.0), ("Statistika", 55.0)]:
            resp = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, topik, skor),
                               headers=auth_header(token))
            assert resp.status_code == 201

        # Verifikasi semua tersimpan
        all_diag = client.get(f"/api/v1/diagnostic/murid/{murid.id}",
                              headers=auth_header(token))
        assert len(all_diag.json()) == 3


# ═══════════════════════════════════════════════════════════════════════════════
# TEST VALIDASI INPUT
# ═══════════════════════════════════════════════════════════════════════════════

class TestValidasiInput:

    def test_skor_di_atas_100_ditolak(self, client):
        """❌ Skor lebih dari 100 harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_val1", email="guru_val1@test.com")
        murid = buat_murid(db, nama="murid_val1", email="murid_val1@test.com")
        db.close()

        token    = get_token(client, "guru_val1@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Aljabar", 101.0),
                               headers=auth_header(token))

        assert response.status_code == 422

    def test_skor_negatif_ditolak(self, client):
        """❌ Skor negatif harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_val2", email="guru_val2@test.com")
        murid = buat_murid(db, nama="murid_val2", email="murid_val2@test.com")
        db.close()

        token    = get_token(client, "guru_val2@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Aljabar", -5.0),
                               headers=auth_header(token))

        assert response.status_code == 422

    def test_tanpa_murid_id_ditolak(self, client):
        """❌ Request tanpa murid_id harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val3", email="guru_val3@test.com")
        db.close()

        token    = get_token(client, "guru_val3@test.com")
        response = client.post("/api/v1/diagnostic/", json={
            "topik":            "Aljabar",
            "diagnostic_score": 75.0,
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tanpa_topik_ditolak(self, client):
        """❌ Request tanpa topik harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_val4", email="guru_val4@test.com")
        murid = buat_murid(db, nama="murid_val4", email="murid_val4@test.com")
        db.close()

        token    = get_token(client, "guru_val4@test.com")
        response = client.post("/api/v1/diagnostic/", json={
            "murid_id":         murid.id,
            "diagnostic_score": 75.0,
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_tanpa_skor_ditolak(self, client):
        """❌ Request tanpa diagnostic_score harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_val5", email="guru_val5@test.com")
        murid = buat_murid(db, nama="murid_val5", email="murid_val5@test.com")
        db.close()

        token    = get_token(client, "guru_val5@test.com")
        response = client.post("/api/v1/diagnostic/", json={
            "murid_id": murid.id,
            "topik":    "Aljabar",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_body_kosong_ditolak(self, client):
        """❌ Request body kosong harus ditolak."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_val6", email="guru_val6@test.com")
        db.close()

        token    = get_token(client, "guru_val6@test.com")
        response = client.post("/api/v1/diagnostic/", json={},
                               headers=auth_header(token))

        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# TEST AKSES KONTROL
# ═══════════════════════════════════════════════════════════════════════════════

class TestAksesKontrol:

    def test_simpan_tanpa_token_ditolak(self, client):
        """❌ Simpan diagnostik tanpa token harus ditolak."""
        response = client.post("/api/v1/diagnostic/", json={
            "murid_id":         "murid-id",
            "topik":            "Aljabar",
            "diagnostic_score": 75.0,
        })
        assert response.status_code in (401, 403)

    def test_simpan_token_palsu_ditolak(self, client):
        """❌ Token palsu harus ditolak."""
        response = client.post("/api/v1/diagnostic/", json={
            "murid_id":         "murid-id",
            "topik":            "Aljabar",
            "diagnostic_score": 75.0,
        }, headers={"Authorization": "Bearer token.palsu.banget"})

        assert response.status_code == 401

    def test_murid_tidak_bisa_simpan_diagnostic(self, client):
        """❌ Murid tidak boleh menyimpan hasil diagnostik."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_akses1", email="murid_akses1@test.com")
        db.close()

        token    = get_token(client, "murid_akses1@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Aljabar", 70.0),
                               headers=auth_header(token))

        assert response.status_code == 403

    def test_get_diagnostic_tanpa_token_ditolak(self, client):
        """❌ Get diagnostik tanpa token harus ditolak."""
        response = client.get("/api/v1/diagnostic/murid/murid-id-apapun")
        assert response.status_code in (401, 403)

    def test_murid_tidak_bisa_get_diagnostic(self, client):
        """❌ Murid tidak boleh mengakses endpoint get diagnostik."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_akses2", email="murid_akses2@test.com")
        db.close()

        token    = get_token(client, "murid_akses2@test.com")
        response = client.get(f"/api/v1/diagnostic/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET DIAGNOSTIK PER MURID
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDiagnostic:

    def test_get_diagnostic_berhasil(self, client):
        """✅ Ambil semua diagnostik untuk satu murid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get1", email="guru_get1@test.com")
        murid = buat_murid(db, nama="murid_get1", email="murid_get1@test.com")
        buat_diagnostic_db(db, murid.id, "Aljabar",    80.0)
        buat_diagnostic_db(db, murid.id, "Geometri",   65.0)
        buat_diagnostic_db(db, murid.id, "Statistika", 55.0)
        db.close()

        token    = get_token(client, "guru_get1@test.com")
        response = client.get(f"/api/v1/diagnostic/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_diagnostic_murid_tanpa_data(self, client):
        """✅ Murid yang belum punya diagnostik harus return list kosong."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get2", email="guru_get2@test.com")
        murid = buat_murid(db, nama="murid_get2", email="murid_get2@test.com")
        db.close()

        token    = get_token(client, "guru_get2@test.com")
        response = client.get(f"/api/v1/diagnostic/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_get_diagnostic_response_field_lengkap(self, client):
        """✅ Setiap item diagnostik harus punya field yang diperlukan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get3", email="guru_get3@test.com")
        murid = buat_murid(db, nama="murid_get3", email="murid_get3@test.com")
        buat_diagnostic_db(db, murid.id, "Aljabar", 78.0)
        db.close()

        token    = get_token(client, "guru_get3@test.com")
        response = client.get(f"/api/v1/diagnostic/murid/{murid.id}",
                              headers=auth_header(token))

        data = response.json()[0]
        assert "id"               in data
        assert "murid_id"         in data
        assert "topik"            in data
        assert "diagnostic_score" in data
        assert "created_at"       in data

    def test_get_diagnostic_tidak_tercampur_murid_lain(self, client):
        """✅ Diagnostik milik murid lain tidak boleh ikut muncul."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_get4", email="guru_get4@test.com")
        murid1 = buat_murid(db, nama="murid_get4a", email="murid_get4a@test.com")
        murid2 = buat_murid(db, nama="murid_get4b", email="murid_get4b@test.com")
        buat_diagnostic_db(db, murid1.id, "Aljabar",  80.0)
        buat_diagnostic_db(db, murid2.id, "Geometri", 60.0)
        buat_diagnostic_db(db, murid2.id, "Fisika",   70.0)
        db.close()

        token    = get_token(client, "guru_get4@test.com")
        response = client.get(f"/api/v1/diagnostic/murid/{murid1.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["murid_id"] == murid1.id

    def test_get_diagnostic_urut_terbaru_dulu(self, client):
        """✅ Diagnostik harus diurutkan dari yang paling baru."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get5", email="guru_get5@test.com")
        murid = buat_murid(db, nama="murid_get5", email="murid_get5@test.com")
        buat_diagnostic_db(db, murid.id, "Topik 1", 70.0)
        buat_diagnostic_db(db, murid.id, "Topik 2", 75.0)
        buat_diagnostic_db(db, murid.id, "Topik 3", 80.0)
        db.close()

        token    = get_token(client, "guru_get5@test.com")
        response = client.get(f"/api/v1/diagnostic/murid/{murid.id}",
                              headers=auth_header(token))

        created_ats = [item["created_at"] for item in response.json()]
        assert created_ats == sorted(created_ats, reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST DATA TERSIMPAN DI DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class TestDataTersimpan:

    def test_diagnostic_tersimpan_di_tabel(self, client):
        """✅ Hasil diagnostik harus tersimpan di tabel diagnostic_result."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_db1", email="guru_db1@test.com")
        murid = buat_murid(db, nama="murid_db1", email="murid_db1@test.com")
        db.close()

        token    = get_token(client, "guru_db1@test.com")
        response = client.post("/api/v1/diagnostic/",
                               json=payload_diagnostic(murid.id, "Aljabar", 78.0),
                               headers=auth_header(token))

        assert response.status_code == 201
        diag_id = response.json()["id"]

        db = TestingSessionLocal()
        from app.models.models import DiagnosticResult
        diag = db.query(DiagnosticResult).filter(
            DiagnosticResult.id == diag_id
        ).first()
        db.close()

        assert diag is not None
        assert diag.murid_id         == murid.id
        assert diag.topik            == "Aljabar"
        assert float(diag.diagnostic_score) == 78.0

    def test_diagnostic_inisialisasi_knowledge_state_baru(self, client):
        """✅ Diagnostik baru harus menginisialisasi knowledge state di BKT."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_db2", email="guru_db2@test.com")
        murid = buat_murid(db, nama="murid_db2", email="murid_db2@test.com")
        db.close()

        token = get_token(client, "guru_db2@test.com")
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid.id, "Geometri", 60.0),
                    headers=auth_header(token))

        # Cek knowledge state terbentuk
        db = TestingSessionLocal()
        from app.models.models import KnowledgeState
        ks = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid.id,
            KnowledgeState.topik    == "Geometri",
        ).first()
        db.close()

        assert ks is not None
        # P(L0) = skor / 100 = 60 / 100 = 0.6
        assert abs(float(ks.p_knowledge) - 0.6) < 0.001

    def test_diagnostic_p_l0_sesuai_skor(self, client):
        """✅ P(L0) di knowledge state harus sama dengan skor / 100."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_db3", email="guru_db3@test.com")
        murid = buat_murid(db, nama="murid_db3", email="murid_db3@test.com")
        db.close()

        token = get_token(client, "guru_db3@test.com")

        test_cases = [
            ("Aljabar",    80.0, 0.80),
            ("Geometri",   45.0, 0.45),
            ("Statistika", 100.0, 1.00),
            ("Kalkulus",   0.0,   0.00),
        ]

        for topik, skor, expected_p_l0 in test_cases:
            client.post("/api/v1/diagnostic/",
                        json=payload_diagnostic(murid.id, topik, skor),
                        headers=auth_header(token))

            db = TestingSessionLocal()
            from app.models.models import KnowledgeState
            ks = db.query(KnowledgeState).filter(
                KnowledgeState.murid_id == murid.id,
                KnowledgeState.topik    == topik,
            ).first()
            db.close()

            assert ks is not None, f"KnowledgeState untuk {topik} tidak ditemukan"
            assert abs(float(ks.p_knowledge) - expected_p_l0) < 0.001, \
                f"P(L0) untuk {topik}: expected {expected_p_l0}, got {ks.p_knowledge}"

    def test_diagnostic_update_knowledge_state_yang_ada(self, client):
        """✅ Diagnostik baru untuk topik yang sudah ada harus update KS, bukan duplikat."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_db4", email="guru_db4@test.com")
        murid = buat_murid(db, nama="murid_db4", email="murid_db4@test.com")
        db.close()

        token = get_token(client, "guru_db4@test.com")

        # Simpan diagnostik pertama untuk topik "Aljabar" dengan skor 50
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid.id, "Aljabar", 50.0),
                    headers=auth_header(token))

        # Simpan lagi untuk topik yang sama dengan skor baru 90
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid.id, "Aljabar", 90.0),
                    headers=auth_header(token))

        # Knowledge state harus hanya ada 1 record (tidak duplikat)
        db = TestingSessionLocal()
        from app.models.models import KnowledgeState
        count = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid.id,
            KnowledgeState.topik    == "Aljabar",
        ).count()
        ks = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid.id,
            KnowledgeState.topik    == "Aljabar",
        ).first()
        db.close()

        assert count == 1
        # P(L0) harus sudah diupdate ke skor terbaru (90 / 100 = 0.9)
        assert abs(float(ks.p_knowledge) - 0.9) < 0.001

    def test_diagnostic_skor_dan_diagnostic_score_sama(self, client):
        """✅ Field skor dan diagnostic_score harus bernilai sama."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_db5", email="guru_db5@test.com")
        murid = buat_murid(db, nama="murid_db5", email="murid_db5@test.com")
        db.close()

        token = get_token(client, "guru_db5@test.com")
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid.id, "Fisika", 72.5),
                    headers=auth_header(token))

        db = TestingSessionLocal()
        from app.models.models import DiagnosticResult
        diag = db.query(DiagnosticResult).filter(
            DiagnosticResult.murid_id == murid.id,
            DiagnosticResult.topik    == "Fisika",
        ).first()
        db.close()

        assert diag is not None
        assert float(diag.skor)             == 72.5
        assert float(diag.diagnostic_score) == 72.5


# ═══════════════════════════════════════════════════════════════════════════════
# TEST INTEGRASI — Diagnostik → BKT → Knowledge State
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegrasiDiagnosticBKT:

    def test_murid_dengan_skor_tinggi_punya_p_l0_tinggi(self, client):
        """✅ Murid dengan skor diagnostik tinggi harus punya P(L0) tinggi di BKT."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_int1", email="guru_int1@test.com")
        murid1 = buat_murid(db, nama="murid_int1a", email="murid_int1a@test.com")
        murid2 = buat_murid(db, nama="murid_int1b", email="murid_int1b@test.com")
        db.close()

        token = get_token(client, "guru_int1@test.com")

        # Murid1 skor tinggi, murid2 skor rendah untuk topik yang sama
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid1.id, "Aljabar", 90.0),
                    headers=auth_header(token))
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid2.id, "Aljabar", 30.0),
                    headers=auth_header(token))

        db = TestingSessionLocal()
        from app.models.models import KnowledgeState
        ks1 = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid1.id,
            KnowledgeState.topik    == "Aljabar",
        ).first()
        ks2 = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid2.id,
            KnowledgeState.topik    == "Aljabar",
        ).first()
        db.close()

        assert float(ks1.p_knowledge) > float(ks2.p_knowledge)

    def test_knowledge_state_terbaca_di_endpoint_plan(self, client):
        """✅ Knowledge state dari diagnostik harus terbaca di endpoint knowledge-state."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_int2", email="guru_int2@test.com")
        murid = buat_murid(db, nama="murid_int2", email="murid_int2@test.com")
        db.close()

        token = get_token(client, "guru_int2@test.com")

        # Simpan diagnostik
        client.post("/api/v1/diagnostic/",
                    json=payload_diagnostic(murid.id, "Trigonometri", 70.0),
                    headers=auth_header(token))

        # Cek di endpoint knowledge-state
        ks_resp = client.get(
            f"/api/v1/plan/knowledge-state/{murid.id}",
            headers=auth_header(token),
        )

        assert ks_resp.status_code == 200
        ks = ks_resp.json()["knowledge_state"]
        assert "Trigonometri" in ks
        assert abs(ks["Trigonometri"] - 0.7) < 0.001

    def test_multiple_topik_masing_masing_punya_knowledge_state(self, client):
        """✅ Setiap topik diagnostik harus punya knowledge state terpisah di BKT."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_int3", email="guru_int3@test.com")
        murid = buat_murid(db, nama="murid_int3", email="murid_int3@test.com")
        db.close()

        token  = get_token(client, "guru_int3@test.com")
        topiks = {
            "Aljabar":    85.0,
            "Geometri":   60.0,
            "Kalkulus":   40.0,
            "Statistika": 75.0,
        }

        for topik, skor in topiks.items():
            client.post("/api/v1/diagnostic/",
                        json=payload_diagnostic(murid.id, topik, skor),
                        headers=auth_header(token))

        ks_resp = client.get(
            f"/api/v1/plan/knowledge-state/{murid.id}",
            headers=auth_header(token),
        )

        ks = ks_resp.json()["knowledge_state"]
        for topik, skor in topiks.items():
            assert topik in ks
            expected_p = skor / 100.0
            assert abs(ks[topik] - expected_p) < 0.001, \
                f"P(L0) untuk {topik}: expected {expected_p}, got {ks[topik]}"
