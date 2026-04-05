"""
test_laporan.py
Unit testing untuk fitur Laporan Perkembangan (F003, F005, F006, F007).
Mencakup: get laporan, generate laporan (mock AI), edit, finalisasi,
          kirim email (mock SMTP), download PDF, akses kontrol.

Pakai SQLite in-memory — tidak perlu PostgreSQL, Ollama, atau SMTP.

Cara jalankan:
    pytest tests/test_laporan.py -v
"""
import os
import uuid
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, patch, MagicMock

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_laporan.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_laporan.db"

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
        if os.path.exists("./test_laporan.db"):
            os.remove("./test_laporan.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import (
            Laporan, LogPertemuan, KnowledgeState,
            KelasMurid, Kelas, Murid, Pengajar, Pengguna,
        )
        db.query(Laporan).delete()
        db.query(LogPertemuan).delete()
        db.query(KnowledgeState).delete()
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


def buat_kelas(db, pengajar_id, nama="Kelas Test", mapel="Matematika"):
    from app.models.models import Kelas
    k = Kelas(
        id=str(uuid.uuid4()),
        nama=nama,
        mata_pelajaran=mapel,
        pengajar_id=pengajar_id,
        kredit=20,
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


def buat_laporan_db(db, murid_id, kelas_id=None, status="draft",
                    konten="Isi laporan test.", tipe="perkembangan"):
    """Buat laporan langsung ke DB tanpa lewat API."""
    from app.models.models import Laporan
    lap = Laporan(
        id=str(uuid.uuid4()),
        murid_id=murid_id,
        kelas_id=kelas_id,
        konten=konten,
        tipe_laporan=tipe,
        status=status,
        is_ai_generated=False,
        tanggal=datetime.utcnow(),
    )
    db.add(lap)
    db.commit()
    db.refresh(lap)
    return lap


def buat_log_db(db, kelas_id, murid_id=None, topik="Aljabar", nilai=80.0):
    from app.models.models import LogPertemuan
    log = LogPertemuan(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        tanggal=date.today(),
        topik=topik,
        nilai=nilai,
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


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LAPORAN
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLaporan:

    def test_get_laporan_by_id_berhasil(self, client):
        """✅ Ambil laporan berdasarkan ID harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get1", email="guru_get1@test.com")
        murid = buat_murid(db, nama="murid_get1", email="murid_get1@test.com")
        lap   = buat_laporan_db(db, murid.id, konten="Konten laporan test")
        db.close()

        token    = get_token(client, "guru_get1@test.com")
        response = client.get(f"/api/v1/laporan/{lap.id}", headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["id"]     == lap.id
        assert data["konten"] == "Konten laporan test"

    def test_get_laporan_tidak_ditemukan(self, client):
        """❌ Get laporan dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_get2", email="guru_get2@test.com")
        db.close()

        token    = get_token(client, "guru_get2@test.com")
        response = client.get("/api/v1/laporan/id-tidak-ada", headers=auth_header(token))

        assert response.status_code == 404

    def test_get_laporan_response_field_lengkap(self, client):
        """✅ Response laporan harus memiliki semua field yang diperlukan."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_get3", email="guru_get3@test.com")
        murid = buat_murid(db, nama="murid_get3", email="murid_get3@test.com")
        kelas = buat_kelas(db, guru.id)
        lap   = buat_laporan_db(db, murid.id, kelas_id=kelas.id)
        db.close()

        token    = get_token(client, "guru_get3@test.com")
        response = client.get(f"/api/v1/laporan/{lap.id}", headers=auth_header(token))
        data     = response.json()

        assert "id"              in data
        assert "murid_id"        in data
        assert "konten"          in data
        assert "status"          in data
        assert "tipe_laporan"    in data
        assert "tanggal"         in data
        assert "is_ai_generated" in data

    def test_get_laporan_tanpa_token_ditolak(self, client):
        """❌ Akses laporan tanpa token harus ditolak."""
        response = client.get("/api/v1/laporan/laporan-id-apapun")
        assert response.status_code in (401, 403)

    def test_murid_bisa_lihat_laporan_sendiri(self, client):
        """✅ Murid bisa melihat laporannya sendiri (F007)."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_lihat1", email="murid_lihat1@test.com")
        lap   = buat_laporan_db(db, murid.id)
        db.close()

        token    = get_token(client, "murid_lihat1@test.com")
        response = client.get(f"/api/v1/laporan/{lap.id}", headers=auth_header(token))

        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LAPORAN BY MURID (F007)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLaporanByMurid:

    def test_get_laporan_by_murid_berhasil(self, client):
        """✅ Ambil semua laporan untuk satu murid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lm1", email="guru_lm1@test.com")
        murid = buat_murid(db, nama="murid_lm1", email="murid_lm1@test.com")
        buat_laporan_db(db, murid.id, konten="Laporan 1")
        buat_laporan_db(db, murid.id, konten="Laporan 2")
        buat_laporan_db(db, murid.id, konten="Laporan 3")
        db.close()

        token    = get_token(client, "guru_lm1@test.com")
        response = client.get(f"/api/v1/laporan/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_laporan_murid_tanpa_laporan(self, client):
        """✅ Murid tanpa laporan harus return list kosong."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lm2", email="guru_lm2@test.com")
        murid = buat_murid(db, nama="murid_lm2", email="murid_lm2@test.com")
        db.close()

        token    = get_token(client, "guru_lm2@test.com")
        response = client.get(f"/api/v1/laporan/murid/{murid.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_laporan_murid_tidak_tercampur_murid_lain(self, client):
        """✅ Laporan murid lain tidak boleh ikut muncul."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_lm3", email="guru_lm3@test.com")
        murid1 = buat_murid(db, nama="murid_lm3a", email="murid_lm3a@test.com")
        murid2 = buat_murid(db, nama="murid_lm3b", email="murid_lm3b@test.com")
        buat_laporan_db(db, murid1.id, konten="Laporan Murid 1")
        buat_laporan_db(db, murid2.id, konten="Laporan Murid 2")
        buat_laporan_db(db, murid2.id, konten="Laporan Murid 2 Lagi")
        db.close()

        token    = get_token(client, "guru_lm3@test.com")
        response = client.get(f"/api/v1/laporan/murid/{murid1.id}",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["murid_id"] == murid1.id

    def test_pagination_laporan_murid(self, client):
        """✅ Parameter skip dan limit harus bekerja."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_lm4", email="guru_lm4@test.com")
        murid = buat_murid(db, nama="murid_lm4", email="murid_lm4@test.com")
        for i in range(10):
            buat_laporan_db(db, murid.id, konten=f"Laporan {i}")
        db.close()

        token = get_token(client, "guru_lm4@test.com")
        resp1 = client.get(f"/api/v1/laporan/murid/{murid.id}?skip=0&limit=5",
                           headers=auth_header(token))
        resp2 = client.get(f"/api/v1/laporan/murid/{murid.id}?skip=5&limit=5",
                           headers=auth_header(token))

        assert len(resp1.json()) == 5
        assert len(resp2.json()) == 5
        ids1 = {l["id"] for l in resp1.json()}
        ids2 = {l["id"] for l in resp2.json()}
        assert ids1.isdisjoint(ids2)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET LAPORAN PENDING
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetLaporanPending:

    def test_laporan_draft_masuk_pending(self, client):
        """✅ Laporan berstatus draft harus muncul di pending."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_pnd1", email="guru_pnd1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_pnd1", email="murid_pnd1@test.com")
        buat_laporan_db(db, murid.id, kelas_id=kelas.id, status="draft")
        buat_laporan_db(db, murid.id, kelas_id=kelas.id, status="final")
        db.close()

        token    = get_token(client, "guru_pnd1@test.com")
        response = client.get("/api/v1/laporan/pending", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_laporan_terkirim_tidak_masuk_pending(self, client):
        """✅ Laporan terkirim tidak boleh masuk pending."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_pnd2", email="guru_pnd2@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_pnd2", email="murid_pnd2@test.com")
        buat_laporan_db(db, murid.id, kelas_id=kelas.id, status="terkirim")
        db.close()

        token    = get_token(client, "guru_pnd2@test.com")
        response = client.get("/api/v1/laporan/pending", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_pending_hanya_milik_kelas_sendiri(self, client):
        """✅ Pending hanya menampilkan laporan dari kelas milik pengajar yang login."""
        db = TestingSessionLocal()
        guru1  = buat_pengajar(db, nama="guru_pnd3", email="guru_pnd3@test.com")
        guru2  = buat_pengajar(db, nama="guru_pnd4", email="guru_pnd4@test.com")
        kelas1 = buat_kelas(db, guru1.id, nama="Kelas Guru1")
        kelas2 = buat_kelas(db, guru2.id, nama="Kelas Guru2")
        murid1 = buat_murid(db, nama="murid_pnd3", email="murid_pnd3@test.com")
        murid2 = buat_murid(db, nama="murid_pnd4", email="murid_pnd4@test.com")
        buat_laporan_db(db, murid1.id, kelas_id=kelas1.id, status="draft")
        buat_laporan_db(db, murid2.id, kelas_id=kelas2.id, status="draft")
        buat_laporan_db(db, murid2.id, kelas_id=kelas2.id, status="draft")
        db.close()

        token    = get_token(client, "guru_pnd3@test.com")
        response = client.get("/api/v1/laporan/pending", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_pending_tanpa_token_ditolak(self, client):
        """❌ Akses pending tanpa token harus ditolak."""
        response = client.get("/api/v1/laporan/pending")
        assert response.status_code in (401, 403)

    def test_murid_tidak_bisa_akses_pending(self, client):
        """❌ Murid tidak boleh mengakses endpoint pending."""
        db = TestingSessionLocal()
        buat_murid(db, nama="murid_pnd5", email="murid_pnd5@test.com")
        db.close()

        token    = get_token(client, "murid_pnd5@test.com")
        response = client.get("/api/v1/laporan/pending", headers=auth_header(token))

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GENERATE LAPORAN — AI dimock (F003)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGenerateLaporan:

    def test_generate_laporan_berhasil(self, client):
        """✅ Generate laporan dengan mock AI harus berhasil dan tersimpan sebagai draft."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen1", email="guru_gen1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="Andi Budi", email="murid_gen1@test.com")
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Aljabar", nilai=80.0)
        db.close()

        token = get_token(client, "guru_gen1@test.com")

        # Mock NarrativeEngine supaya tidak perlu Ollama
        with patch(
            "app.services.report_service.narrative_engine.generate_report",
            new_callable=AsyncMock,
            return_value="Laporan perkembangan Andi Budi: siswa menunjukkan kemajuan baik.",
        ):
            response = client.post("/api/v1/laporan/generate", json={
                "murid_id":   murid.id,
                "kelas_id":   kelas.id,
                "tipe_laporan": "perkembangan",
            }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["murid_id"]        == murid.id
        assert data["status"]          == "draft"
        assert data["is_ai_generated"] == True
        assert "Andi Budi" in data["konten"]

    def test_generate_laporan_murid_tidak_ada(self, client):
        """❌ Generate laporan untuk murid yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_gen2", email="guru_gen2@test.com")
        db.close()

        token = get_token(client, "guru_gen2@test.com")

        with patch(
            "app.services.report_service.narrative_engine.generate_report",
            new_callable=AsyncMock,
            return_value="Laporan test.",
        ):
            response = client.post("/api/v1/laporan/generate", json={
                "murid_id":     "murid-tidak-ada-sama-sekali",
                "tipe_laporan": "perkembangan",
            }, headers=auth_header(token))

        assert response.status_code == 404

    def test_generate_laporan_tersimpan_di_database(self, client):
        """✅ Laporan yang di-generate harus tersimpan di database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen3", email="guru_gen3@test.com")
        murid = buat_murid(db, nama="Budi Santoso", email="murid_gen3@test.com")
        db.close()

        token = get_token(client, "guru_gen3@test.com")

        with patch(
            "app.services.report_service.narrative_engine.generate_report",
            new_callable=AsyncMock,
            return_value="Laporan Budi tersimpan.",
        ):
            response = client.post("/api/v1/laporan/generate", json={
                "murid_id":     murid.id,
                "tipe_laporan": "perkembangan",
            }, headers=auth_header(token))

        assert response.status_code == 201
        laporan_id = response.json()["id"]

        # Verifikasi di database
        db = TestingSessionLocal()
        from app.models.models import Laporan
        lap = db.query(Laporan).filter(Laporan.id == laporan_id).first()
        db.close()

        assert lap is not None
        assert lap.konten         == "Laporan Budi tersimpan."
        assert lap.status         == "draft"
        assert lap.is_ai_generated == True

    def test_generate_laporan_dengan_periode(self, client):
        """✅ Generate laporan dengan filter periode harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen4", email="guru_gen4@test.com")
        murid = buat_murid(db, nama="murid_gen4", email="murid_gen4@test.com")
        db.close()

        token = get_token(client, "guru_gen4@test.com")

        with patch(
            "app.services.report_service.narrative_engine.generate_report",
            new_callable=AsyncMock,
            return_value="Laporan periode Januari.",
        ):
            response = client.post("/api/v1/laporan/generate", json={
                "murid_id":       murid.id,
                "tipe_laporan":   "perkembangan",
                "periode_mulai":  "2025-01-01",
                "periode_selesai":"2025-01-31",
            }, headers=auth_header(token))

        assert response.status_code == 201
        data = response.json()
        assert data["periode_mulai"]   == "2025-01-01"
        assert data["periode_selesai"] == "2025-01-31"

    def test_generate_laporan_tanpa_token_ditolak(self, client):
        """❌ Generate laporan tanpa token harus ditolak."""
        response = client.post("/api/v1/laporan/generate", json={
            "murid_id":     "murid-id-apapun",
            "tipe_laporan": "perkembangan",
        })
        assert response.status_code in (401, 403)

    def test_murid_tidak_bisa_generate_laporan(self, client):
        """❌ Murid tidak boleh generate laporan."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_gen5", email="murid_gen5@test.com")
        db.close()

        token = get_token(client, "murid_gen5@test.com")
        response = client.post("/api/v1/laporan/generate", json={
            "murid_id":     murid.id,
            "tipe_laporan": "perkembangan",
        }, headers=auth_header(token))

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# TEST EDIT LAPORAN (F005)
# ═══════════════════════════════════════════════════════════════════════════════

class TestEditLaporan:

    def test_edit_konten_berhasil(self, client):
        """✅ Edit konten laporan harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_edit1", email="guru_edit1@test.com")
        murid = buat_murid(db, nama="murid_edit1", email="murid_edit1@test.com")
        lap   = buat_laporan_db(db, murid.id, konten="Konten Asli")
        db.close()

        token    = get_token(client, "guru_edit1@test.com")
        response = client.put(f"/api/v1/laporan/{lap.id}", json={
            "konten": "Konten Sudah Diedit Oleh Guru",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["konten"] == "Konten Sudah Diedit Oleh Guru"

    def test_edit_status_berhasil(self, client):
        """✅ Edit status laporan harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_edit2", email="guru_edit2@test.com")
        murid = buat_murid(db, nama="murid_edit2", email="murid_edit2@test.com")
        lap   = buat_laporan_db(db, murid.id, status="draft")
        db.close()

        token    = get_token(client, "guru_edit2@test.com")
        response = client.put(f"/api/v1/laporan/{lap.id}", json={
            "status": "final",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["status"] == "final"

    def test_edit_partial_field_lain_tidak_berubah(self, client):
        """✅ Edit sebagian field tidak mengubah field lain."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_edit3", email="guru_edit3@test.com")
        murid = buat_murid(db, nama="murid_edit3", email="murid_edit3@test.com")
        lap   = buat_laporan_db(db, murid.id,
                                konten="Konten Tetap", status="draft")
        db.close()

        token    = get_token(client, "guru_edit3@test.com")
        response = client.put(f"/api/v1/laporan/{lap.id}", json={
            "status": "final",
        }, headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["konten"] == "Konten Tetap"   # tidak berubah
        assert response.json()["status"] == "final"           # berubah

    def test_edit_laporan_tidak_ditemukan(self, client):
        """❌ Edit laporan yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_edit4", email="guru_edit4@test.com")
        db.close()

        token    = get_token(client, "guru_edit4@test.com")
        response = client.put("/api/v1/laporan/id-tidak-ada", json={
            "konten": "Apapun",
        }, headers=auth_header(token))

        assert response.status_code == 404

    def test_edit_tersimpan_di_database(self, client):
        """✅ Perubahan setelah edit harus tersimpan di database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_edit5", email="guru_edit5@test.com")
        murid = buat_murid(db, nama="murid_edit5", email="murid_edit5@test.com")
        lap   = buat_laporan_db(db, murid.id, konten="Sebelum Edit")
        db.close()

        token = get_token(client, "guru_edit5@test.com")
        client.put(f"/api/v1/laporan/{lap.id}", json={
            "konten": "Sesudah Edit",
        }, headers=auth_header(token))

        db = TestingSessionLocal()
        from app.models.models import Laporan
        updated = db.query(Laporan).filter(Laporan.id == lap.id).first()
        db.close()

        assert updated.konten == "Sesudah Edit"

    def test_edit_tanpa_token_ditolak(self, client):
        """❌ Edit laporan tanpa token harus ditolak."""
        response = client.put("/api/v1/laporan/laporan-id-apapun", json={
            "konten": "Tanpa Token",
        })
        assert response.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FINALISASI LAPORAN
# ═══════════════════════════════════════════════════════════════════════════════

class TestFinalisasiLaporan:

    def test_finalisasi_berhasil(self, client):
        """✅ Finalisasi laporan harus mengubah status menjadi 'final'."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_fin1", email="guru_fin1@test.com")
        murid = buat_murid(db, nama="murid_fin1", email="murid_fin1@test.com")
        lap   = buat_laporan_db(db, murid.id, status="draft")
        db.close()

        token    = get_token(client, "guru_fin1@test.com")
        response = client.put(f"/api/v1/laporan/{lap.id}/finalisasi",
                              headers=auth_header(token))

        assert response.status_code == 200
        assert response.json()["status"] == "final"

    def test_finalisasi_tersimpan_di_database(self, client):
        """✅ Status 'final' harus tersimpan di database setelah finalisasi."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_fin2", email="guru_fin2@test.com")
        murid = buat_murid(db, nama="murid_fin2", email="murid_fin2@test.com")
        lap   = buat_laporan_db(db, murid.id, status="draft")
        db.close()

        token = get_token(client, "guru_fin2@test.com")
        client.put(f"/api/v1/laporan/{lap.id}/finalisasi", headers=auth_header(token))

        db = TestingSessionLocal()
        from app.models.models import Laporan
        updated = db.query(Laporan).filter(Laporan.id == lap.id).first()
        db.close()

        assert updated.status == "final"

    def test_finalisasi_laporan_tidak_ditemukan(self, client):
        """❌ Finalisasi laporan yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_fin3", email="guru_fin3@test.com")
        db.close()

        token    = get_token(client, "guru_fin3@test.com")
        response = client.put("/api/v1/laporan/id-tidak-ada/finalisasi",
                              headers=auth_header(token))

        assert response.status_code == 404

    def test_finalisasi_tanpa_token_ditolak(self, client):
        """❌ Finalisasi tanpa token harus ditolak."""
        response = client.put("/api/v1/laporan/laporan-id/finalisasi")
        assert response.status_code in (401, 403)

    def test_laporan_final_muncul_di_pending(self, client):
        """✅ Laporan yang sudah final tapi belum dikirim tetap muncul di pending."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_fin4", email="guru_fin4@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_fin4", email="murid_fin4@test.com")
        lap   = buat_laporan_db(db, murid.id, kelas_id=kelas.id, status="draft")
        db.close()

        token = get_token(client, "guru_fin4@test.com")

        # Finalisasi dulu
        client.put(f"/api/v1/laporan/{lap.id}/finalisasi", headers=auth_header(token))

        # Cek masih muncul di pending
        pending = client.get("/api/v1/laporan/pending", headers=auth_header(token))
        assert any(l["id"] == lap.id for l in pending.json())


# ═══════════════════════════════════════════════════════════════════════════════
# TEST KIRIM LAPORAN — Email dimock (F006)
# ═══════════════════════════════════════════════════════════════════════════════

class TestKirimLaporan:

    def test_kirim_laporan_final_berhasil(self, client):
        """✅ Kirim laporan yang sudah final harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_kirim1", email="guru_kirim1@test.com")
        murid = buat_murid(db, nama="murid_kirim1", email="murid_kirim1@test.com")
        lap   = buat_laporan_db(db, murid.id, status="final",
                                konten="Isi laporan yang akan dikirim.")
        db.close()

        token = get_token(client, "guru_kirim1@test.com")

        # Mock fungsi kirim email dan generate PDF
        with patch("app.routers.laporan.generate_pdf", return_value=""), \
             patch("app.routers.laporan.kirim_laporan_email", new_callable=AsyncMock):
            response = client.post(f"/api/v1/laporan/{lap.id}/kirim", json={
                "email_tujuan": "orangtua@test.com",
            }, headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert "dikirim" in data["message"].lower()
        assert data["laporan_id"] == lap.id

    def test_kirim_laporan_draft_ditolak(self, client):
        """❌ Laporan berstatus draft tidak boleh dikirim sebelum difinalisasi."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_kirim2", email="guru_kirim2@test.com")
        murid = buat_murid(db, nama="murid_kirim2", email="murid_kirim2@test.com")
        lap   = buat_laporan_db(db, murid.id, status="draft")
        db.close()

        token    = get_token(client, "guru_kirim2@test.com")
        response = client.post(f"/api/v1/laporan/{lap.id}/kirim", json={
            "email_tujuan": "orangtua@test.com",
        }, headers=auth_header(token))

        assert response.status_code == 400
        assert "finalisasi" in response.json()["detail"].lower()

    def test_kirim_laporan_tidak_ditemukan(self, client):
        """❌ Kirim laporan yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_kirim3", email="guru_kirim3@test.com")
        db.close()

        token    = get_token(client, "guru_kirim3@test.com")
        response = client.post("/api/v1/laporan/id-tidak-ada/kirim", json={
            "email_tujuan": "test@test.com",
        }, headers=auth_header(token))

        assert response.status_code == 404

    def test_kirim_tanpa_email_tujuan_ditolak(self, client):
        """❌ Kirim laporan tanpa email_tujuan harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_kirim4", email="guru_kirim4@test.com")
        murid = buat_murid(db, nama="murid_kirim4", email="murid_kirim4@test.com")
        lap   = buat_laporan_db(db, murid.id, status="final")
        db.close()

        token    = get_token(client, "guru_kirim4@test.com")
        response = client.post(f"/api/v1/laporan/{lap.id}/kirim",
                               json={}, headers=auth_header(token))

        assert response.status_code == 422

    def test_kirim_email_format_salah_ditolak(self, client):
        """❌ Format email tujuan yang salah harus ditolak."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_kirim5", email="guru_kirim5@test.com")
        murid = buat_murid(db, nama="murid_kirim5", email="murid_kirim5@test.com")
        lap   = buat_laporan_db(db, murid.id, status="final")
        db.close()

        token    = get_token(client, "guru_kirim5@test.com")
        response = client.post(f"/api/v1/laporan/{lap.id}/kirim", json={
            "email_tujuan": "ini-bukan-email",
        }, headers=auth_header(token))

        assert response.status_code == 422

    def test_kirim_dengan_catatan_tambahan(self, client):
        """✅ Kirim laporan dengan catatan tambahan harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_kirim6", email="guru_kirim6@test.com")
        murid = buat_murid(db, nama="murid_kirim6", email="murid_kirim6@test.com")
        lap   = buat_laporan_db(db, murid.id, status="final")
        db.close()

        token = get_token(client, "guru_kirim6@test.com")

        with patch("app.routers.laporan.generate_pdf", return_value=""), \
             patch("app.routers.laporan.kirim_laporan_email", new_callable=AsyncMock):
            response = client.post(f"/api/v1/laporan/{lap.id}/kirim", json={
                "email_tujuan":      "orangtua@test.com",
                "catatan_tambahan":  "Mohon perhatikan perkembangan anak.",
            }, headers=auth_header(token))

        assert response.status_code == 200

    def test_kirim_tanpa_token_ditolak(self, client):
        """❌ Kirim laporan tanpa token harus ditolak."""
        response = client.post("/api/v1/laporan/laporan-id/kirim", json={
            "email_tujuan": "test@test.com",
        })
        assert response.status_code in (401, 403)
