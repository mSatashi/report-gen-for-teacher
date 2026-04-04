"""
test_learning_plan.py
Unit testing untuk fitur Learning Plan / Rencana Studi (F004).
Mencakup: get rencana, generate rencana (mock AI+BKT),
          knowledge state, filter per murid, akses kontrol.

Pakai SQLite in-memory — tidak perlu PostgreSQL atau Ollama.

Cara jalankan:
    pytest tests/test_learning_plan.py -v
"""
import os
import uuid
import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch

# ── Set env sebelum import apapun dari app ────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_plan.db"
os.environ["SECRET_KEY"]   = "test-secret-key-cukup-panjang-32-karakter-ok"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db

# ── Setup SQLite ──────────────────────────────────────────────────────────────
SQLITE_URL = "sqlite:///./test_plan.db"

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
        if os.path.exists("./test_plan.db"):
            os.remove("./test_plan.db")
    except PermissionError:
        pass


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    try:
        from app.models.models import (
            RencanaStudi, DraftAnalisis, KnowledgeState,
            LogPertemuan, KelasMusrid, Kelas,
            Murid, Pengajar, Pengguna,
        )
        db.query(RencanaStudi).delete()
        db.query(DraftAnalisis).delete()
        db.query(KnowledgeState).delete()
        db.query(LogPertemuan).delete()
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


# ── Mock response AI ──────────────────────────────────────────────────────────
# Dipakai di semua test yang perlu generate rencana

MOCK_DRAFT_TEXT = "Analisis kelas: siswa sudah menguasai aljabar dasar, perlu perkuat geometri."

MOCK_RENCANA_DATA = {
    "rekomendasi_materi":    ["Geometri", "Trigonometri", "Statistika"],
    "jadwal_mingguan":       {"Minggu 1": ["Geometri"], "Minggu 2": ["Trigonometri"]},
    "catatan_analisa":       "Prioritaskan geometri karena penguasaan masih rendah.",
    "estimasi_selesai_minggu": 3,
    "prioritas_perhatian":   ["Geometri"],
}


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


def buat_kelas(db, pengajar_id, nama="Kelas Test", mapel="Matematika", kredit=20):
    from app.models.models import Kelas
    k = Kelas(
        id=str(uuid.uuid4()),
        nama=nama,
        mata_pelajaran=mapel,
        pengajar_id=pengajar_id,
        kredit=kredit,
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


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


def buat_rencana_db(db, kelas_id, murid_id=None, version=1):
    from app.models.models import RencanaStudi
    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        daftar_rekomendasi_materi=["Topik A", "Topik B"],
        jadwal_mingguan={"Minggu 1": ["Topik A"]},
        catatan_analisa="Catatan test",
        waktu=datetime.utcnow(),
        estimasi_waktu_selesai=datetime.utcnow() + timedelta(weeks=4),
        version=version,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana


def buat_knowledge_state(db, murid_id, topik, p_knowledge=0.5):
    from app.models.models import KnowledgeState
    ks = KnowledgeState(
        id=str(uuid.uuid4()),
        murid_id=murid_id,
        topik=topik,
        p_knowledge=p_knowledge,
        p_learn=0.2,
        p_guess=0.1,
        p_slip=0.05,
    )
    db.add(ks)
    db.commit()
    db.refresh(ks)
    return ks


def get_token(client, email, password="Test1234!"):
    resp = client.post("/api/v1/auth/login", json={
        "email_address": email,
        "password": password,
    })
    return resp.json().get("access_token", "")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GET RENCANA STUDI
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetRencana:

    def test_get_rencana_by_id_berhasil(self, client):
        """✅ Ambil rencana studi berdasarkan ID harus berhasil."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_get1", email="guru_get1@test.com")
        kelas  = buat_kelas(db, guru.id)
        rencana = buat_rencana_db(db, kelas.id)
        db.close()

        token    = get_token(client, "guru_get1@test.com")
        response = client.get(f"/api/v1/plan/{rencana.id}", headers=auth_header(token))

        assert response.status_code == 200
        data = response.json()
        assert data["id"]       == rencana.id
        assert data["kelas_id"] == kelas.id

    def test_get_rencana_tidak_ditemukan(self, client):
        """❌ Get rencana dengan ID tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_get2", email="guru_get2@test.com")
        db.close()

        token    = get_token(client, "guru_get2@test.com")
        response = client.get("/api/v1/plan/id-tidak-ada", headers=auth_header(token))

        assert response.status_code == 404

    def test_get_rencana_response_field_lengkap(self, client):
        """✅ Response rencana harus memiliki semua field yang diperlukan."""
        db = TestingSessionLocal()
        guru    = buat_pengajar(db, nama="guru_get3", email="guru_get3@test.com")
        kelas   = buat_kelas(db, guru.id)
        rencana = buat_rencana_db(db, kelas.id)
        db.close()

        token    = get_token(client, "guru_get3@test.com")
        response = client.get(f"/api/v1/plan/{rencana.id}", headers=auth_header(token))
        data     = response.json()

        assert "id"                        in data
        assert "kelas_id"                  in data
        assert "waktu"                     in data
        assert "daftar_rekomendasi_materi" in data
        assert "jadwal_mingguan"           in data
        assert "catatan_analisa"           in data
        assert "version"                   in data

    def test_get_rencana_tanpa_token_ditolak(self, client):
        """❌ Akses rencana tanpa token harus ditolak."""
        response = client.get("/api/v1/plan/rencana-id-apapun")
        assert response.status_code in (401, 403)

    def test_murid_tidak_bisa_akses_rencana(self, client):
        """❌ Murid tidak boleh mengakses learning plan."""
        db = TestingSessionLocal()
        buat_murid(db, nama="murid_get1", email="murid_get1@test.com")
        db.close()

        token    = get_token(client, "murid_get1@test.com")
        response = client.get("/api/v1/plan/rencana-id-apapun", headers=auth_header(token))

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# TEST LIST RENCANA BY KELAS
# ═══════════════════════════════════════════════════════════════════════════════

class TestListRencanaByKelas:

    def test_list_rencana_berhasil(self, client):
        """✅ List rencana untuk satu kelas harus berhasil."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_list1", email="guru_list1@test.com")
        kelas  = buat_kelas(db, guru.id)
        buat_rencana_db(db, kelas.id, version=1)
        buat_rencana_db(db, kelas.id, version=2)
        db.close()

        token    = get_token(client, "guru_list1@test.com")
        response = client.get(f"/api/v1/plan/kelas/{kelas.id}", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_rencana_kelas_kosong(self, client):
        """✅ Kelas tanpa rencana harus return list kosong."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_list2", email="guru_list2@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token    = get_token(client, "guru_list2@test.com")
        response = client.get(f"/api/v1/plan/kelas/{kelas.id}", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_list_rencana_filter_per_murid(self, client):
        """✅ Filter rencana per murid dalam satu kelas harus bekerja."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_list3", email="guru_list3@test.com")
        kelas  = buat_kelas(db, guru.id)
        murid1 = buat_murid(db, nama="murid_list1", email="murid_list1@test.com")
        murid2 = buat_murid(db, nama="murid_list2", email="murid_list2@test.com")
        buat_rencana_db(db, kelas.id, murid_id=murid1.id)
        buat_rencana_db(db, kelas.id, murid_id=murid1.id)
        buat_rencana_db(db, kelas.id, murid_id=murid2.id)
        db.close()

        token    = get_token(client, "guru_list3@test.com")
        response = client.get(
            f"/api/v1/plan/kelas/{kelas.id}?murid_id={murid1.id}",
            headers=auth_header(token),
        )

        assert response.status_code == 200
        rencana_list = response.json()
        assert len(rencana_list) == 2
        for r in rencana_list:
            assert r["murid_id"] == murid1.id

    def test_list_rencana_tidak_tercampur_kelas_lain(self, client):
        """✅ Rencana dari kelas lain tidak boleh ikut muncul."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_list4", email="guru_list4@test.com")
        kelas1 = buat_kelas(db, guru.id, nama="Kelas A")
        kelas2 = buat_kelas(db, guru.id, nama="Kelas B")
        buat_rencana_db(db, kelas1.id)
        buat_rencana_db(db, kelas2.id)
        buat_rencana_db(db, kelas2.id)
        db.close()

        token    = get_token(client, "guru_list4@test.com")
        response = client.get(f"/api/v1/plan/kelas/{kelas1.id}", headers=auth_header(token))

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_rencana_urut_terbaru_dulu(self, client):
        """✅ Rencana harus diurutkan dari yang paling baru."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_list5", email="guru_list5@test.com")
        kelas = buat_kelas(db, guru.id)
        buat_rencana_db(db, kelas.id, version=1)
        buat_rencana_db(db, kelas.id, version=2)
        buat_rencana_db(db, kelas.id, version=3)
        db.close()

        token    = get_token(client, "guru_list5@test.com")
        response = client.get(f"/api/v1/plan/kelas/{kelas.id}", headers=auth_header(token))

        versions = [r["version"] for r in response.json()]
        assert versions == sorted(versions, reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GENERATE RENCANA STUDI — AI dimock (F004)
# ═══════════════════════════════════════════════════════════════════════════════

class TestGenerateRencana:

    def test_generate_rencana_kelas_berhasil(self, client):
        """✅ Generate rencana untuk seluruh kelas harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen1", email="guru_gen1@test.com")
        kelas = buat_kelas(db, guru.id, kredit=20)
        buat_log_db(db, kelas.id, topik="Aljabar",  nilai=80.0)
        buat_log_db(db, kelas.id, topik="Geometri", nilai=65.0)
        db.close()

        token = get_token(client, "guru_gen1@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value=MOCK_DRAFT_TEXT,
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            response = client.post(
                f"/api/v1/plan/generate/{kelas.id}",
                headers=auth_header(token),
            )

        assert response.status_code == 201
        data = response.json()
        assert data["kelas_id"]                   == kelas.id
        assert data["daftar_rekomendasi_materi"]  == ["Geometri", "Trigonometri", "Statistika"]
        assert data["version"]                    == 1

    def test_generate_rencana_per_murid_berhasil(self, client):
        """✅ Generate rencana untuk satu murid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen2", email="guru_gen2@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="Andi Budi", email="murid_gen2@test.com")
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Aljabar", nilai=75.0)
        db.close()

        token = get_token(client, "guru_gen2@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value=MOCK_DRAFT_TEXT,
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            response = client.post(
                f"/api/v1/plan/generate/{kelas.id}?murid_id={murid.id}",
                headers=auth_header(token),
            )

        assert response.status_code == 201
        data = response.json()
        assert data["murid_id"] == murid.id
        assert data["kelas_id"] == kelas.id

    def test_generate_rencana_tersimpan_di_database(self, client):
        """✅ Rencana yang di-generate harus tersimpan di database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen3", email="guru_gen3@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token = get_token(client, "guru_gen3@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value=MOCK_DRAFT_TEXT,
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            response = client.post(
                f"/api/v1/plan/generate/{kelas.id}",
                headers=auth_header(token),
            )

        assert response.status_code == 201
        rencana_id = response.json()["id"]

        db = TestingSessionLocal()
        from app.models.models import RencanaStudi
        rencana = db.query(RencanaStudi).filter(RencanaStudi.id == rencana_id).first()
        db.close()

        assert rencana is not None
        assert rencana.kelas_id                  == kelas.id
        assert rencana.daftar_rekomendasi_materi == ["Geometri", "Trigonometri", "Statistika"]

    def test_generate_rencana_kelas_tidak_ada(self, client):
        """❌ Generate rencana untuk kelas yang tidak ada harus return 404."""
        db = TestingSessionLocal()
        buat_pengajar(db, nama="guru_gen4", email="guru_gen4@test.com")
        db.close()

        token = get_token(client, "guru_gen4@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value=MOCK_DRAFT_TEXT,
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            response = client.post(
                "/api/v1/plan/generate/kelas-tidak-ada",
                headers=auth_header(token),
            )

        assert response.status_code == 404

    def test_generate_rencana_versi_bertambah(self, client):
        """✅ Setiap generate rencana untuk kelas yang sama versinya harus bertambah."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen5", email="guru_gen5@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token = get_token(client, "guru_gen5@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value=MOCK_DRAFT_TEXT,
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            resp1 = client.post(
                f"/api/v1/plan/generate/{kelas.id}",
                headers=auth_header(token),
            )
            resp2 = client.post(
                f"/api/v1/plan/generate/{kelas.id}",
                headers=auth_header(token),
            )

        assert resp1.json()["version"] == 1
        assert resp2.json()["version"] == 2

    def test_generate_rencana_draft_analisis_tersimpan(self, client):
        """✅ DraftAnalisis harus ikut tersimpan saat generate rencana."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen6", email="guru_gen6@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token = get_token(client, "guru_gen6@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value="Draft analisis spesifik untuk test ini.",
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            client.post(
                f"/api/v1/plan/generate/{kelas.id}",
                headers=auth_header(token),
            )

        db = TestingSessionLocal()
        from app.models.models import DraftAnalisis
        draft = db.query(DraftAnalisis).filter(
            DraftAnalisis.kelas_id == kelas.id
        ).first()
        db.close()

        assert draft is not None
        assert draft.konten == "Draft analisis spesifik untuk test ini."

    def test_generate_rencana_estimasi_waktu_ada(self, client):
        """✅ Rencana yang di-generate harus memiliki estimasi waktu selesai."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_gen7", email="guru_gen7@test.com")
        kelas = buat_kelas(db, guru.id)
        db.close()

        token = get_token(client, "guru_gen7@test.com")

        with patch(
            "app.services.plan_service.narrative_engine.analyze_class_data",
            new_callable=AsyncMock,
            return_value=MOCK_DRAFT_TEXT,
        ), patch(
            "app.services.plan_service.planner_engine.generate_rencana_studi",
            new_callable=AsyncMock,
            return_value=MOCK_RENCANA_DATA,
        ):
            response = client.post(
                f"/api/v1/plan/generate/{kelas.id}",
                headers=auth_header(token),
            )

        assert response.status_code == 201
        assert response.json()["estimasi_waktu_selesai"] is not None

    def test_generate_rencana_tanpa_token_ditolak(self, client):
        """❌ Generate rencana tanpa token harus ditolak."""
        response = client.post("/api/v1/plan/generate/kelas-id-apapun")
        assert response.status_code in (401, 403)

    def test_murid_tidak_bisa_generate_rencana(self, client):
        """❌ Murid tidak boleh generate rencana studi."""
        db = TestingSessionLocal()
        murid = buat_murid(db, nama="murid_gen1", email="murid_gen1@test.com")
        db.close()

        token    = get_token(client, "murid_gen1@test.com")
        response = client.post(
            "/api/v1/plan/generate/kelas-id-apapun",
            headers=auth_header(token),
        )

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# TEST KNOWLEDGE STATE (BKT)
# ═══════════════════════════════════════════════════════════════════════════════

class TestKnowledgeState:

    def test_get_knowledge_state_berhasil(self, client):
        """✅ Ambil knowledge state murid harus berhasil."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_ks1", email="guru_ks1@test.com")
        murid = buat_murid(db, nama="murid_ks1", email="murid_ks1@test.com")
        buat_knowledge_state(db, murid.id, "Aljabar",   p_knowledge=0.75)
        buat_knowledge_state(db, murid.id, "Geometri",  p_knowledge=0.45)
        buat_knowledge_state(db, murid.id, "Statistika",p_knowledge=0.30)
        db.close()

        token    = get_token(client, "guru_ks1@test.com")
        response = client.get(
            f"/api/v1/plan/knowledge-state/{murid.id}",
            headers=auth_header(token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["murid_id"] == murid.id
        assert "knowledge_state" in data
        ks = data["knowledge_state"]
        assert "Aljabar"    in ks
        assert "Geometri"   in ks
        assert "Statistika" in ks

    def test_knowledge_state_nilai_antara_0_dan_1(self, client):
        """✅ Semua nilai knowledge state harus berada di antara 0.0 dan 1.0."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_ks2", email="guru_ks2@test.com")
        murid = buat_murid(db, nama="murid_ks2", email="murid_ks2@test.com")
        buat_knowledge_state(db, murid.id, "Topik A", p_knowledge=0.9)
        buat_knowledge_state(db, murid.id, "Topik B", p_knowledge=0.1)
        db.close()

        token    = get_token(client, "guru_ks2@test.com")
        response = client.get(
            f"/api/v1/plan/knowledge-state/{murid.id}",
            headers=auth_header(token),
        )

        ks = response.json()["knowledge_state"]
        for topik, nilai in ks.items():
            assert 0.0 <= nilai <= 1.0, f"Nilai {topik} = {nilai} di luar range 0-1"

    def test_knowledge_state_murid_tanpa_data(self, client):
        """✅ Murid tanpa knowledge state harus return dict kosong."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_ks3", email="guru_ks3@test.com")
        murid = buat_murid(db, nama="murid_ks3", email="murid_ks3@test.com")
        db.close()

        token    = get_token(client, "guru_ks3@test.com")
        response = client.get(
            f"/api/v1/plan/knowledge-state/{murid.id}",
            headers=auth_header(token),
        )

        assert response.status_code == 200
        assert response.json()["knowledge_state"] == {}

    def test_knowledge_state_tidak_tercampur_murid_lain(self, client):
        """✅ Knowledge state murid lain tidak boleh ikut muncul."""
        db = TestingSessionLocal()
        guru   = buat_pengajar(db, nama="guru_ks4", email="guru_ks4@test.com")
        murid1 = buat_murid(db, nama="murid_ks4a", email="murid_ks4a@test.com")
        murid2 = buat_murid(db, nama="murid_ks4b", email="murid_ks4b@test.com")
        buat_knowledge_state(db, murid1.id, "Topik Murid1", p_knowledge=0.8)
        buat_knowledge_state(db, murid2.id, "Topik Murid2", p_knowledge=0.3)
        db.close()

        token    = get_token(client, "guru_ks4@test.com")
        response = client.get(
            f"/api/v1/plan/knowledge-state/{murid1.id}",
            headers=auth_header(token),
        )

        ks = response.json()["knowledge_state"]
        assert "Topik Murid1" in ks
        assert "Topik Murid2" not in ks

    def test_knowledge_state_tanpa_token_ditolak(self, client):
        """❌ Akses knowledge state tanpa token harus ditolak."""
        response = client.get("/api/v1/plan/knowledge-state/murid-id-apapun")
        assert response.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST BKT MODULE — Unit test langsung
# ═══════════════════════════════════════════════════════════════════════════════

class TestBKTModule:

    def test_bkt_update_correct_naik(self):
        """✅ Jawab benar harus menaikkan probabilitas penguasaan."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule(p_learn=0.2, p_guess=0.1, p_slip=0.05)

        p_awal  = 0.3
        p_baru  = bkt.update(p_awal, correct=True)

        assert p_baru > p_awal

    def test_bkt_update_incorrect_turun_atau_flat(self):
        """✅ Jawab salah seharusnya tidak menaikkan probabilitas secara signifikan."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule(p_learn=0.2, p_guess=0.1, p_slip=0.05)

        p_awal = 0.8
        p_baru = bkt.update(p_awal, correct=False)

        # Meski salah, p_learn masih ada jadi tidak harus turun drastis,
        # tapi tidak boleh lebih tinggi dari kondisi selalu benar
        p_selalu_benar = bkt.update(p_awal, correct=True)
        assert p_baru < p_selalu_benar

    def test_bkt_nilai_selalu_antara_0_dan_1(self):
        """✅ Hasil BKT harus selalu berada di antara 0.0 dan 1.0."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        for p_awal in [0.0, 0.1, 0.5, 0.9, 1.0]:
            for correct in [True, False]:
                p_baru = bkt.update(p_awal, correct=correct)
                assert 0.0 <= p_baru <= 1.0, \
                    f"p_baru={p_baru} di luar range untuk p_awal={p_awal}, correct={correct}"

    def test_bkt_compute_from_score_benar_jika_nilai_tinggi(self):
        """✅ Skor >= 60 dianggap 'correct' dalam BKT."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        p_awal = 0.3
        p_skor_tinggi = bkt.compute_from_score(p_awal, score=80.0)
        p_skor_rendah = bkt.compute_from_score(p_awal, score=40.0)

        assert p_skor_tinggi > p_skor_rendah

    def test_bkt_compute_from_score_batas_60(self):
        """✅ Skor tepat 60 dianggap correct, skor 59 dianggap incorrect."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        p_awal = 0.5
        p_60   = bkt.compute_from_score(p_awal, score=60.0)
        p_59   = bkt.compute_from_score(p_awal, score=59.0)

        assert p_60 > p_59

    def test_bkt_batch_update_makin_banyak_benar_makin_tinggi(self):
        """✅ Makin banyak jawaban benar, probabilitas penguasaan makin tinggi."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        p_3_benar  = bkt.batch_update(0.1, [80.0, 85.0, 90.0])
        p_1_benar  = bkt.batch_update(0.1, [80.0])

        assert p_3_benar > p_1_benar

    def test_bkt_batch_update_skor_campuran(self):
        """✅ Batch update dengan skor campuran harus tetap dalam range 0-1."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        scores = [80.0, 45.0, 90.0, 30.0, 75.0]
        p_final = bkt.batch_update(0.1, scores)

        assert 0.0 <= p_final <= 1.0

    def test_bkt_update_knowledge_state_tersimpan_ke_db(self, client):
        """✅ update_knowledge_states harus menyimpan hasil BKT ke database."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bkt1", email="guru_bkt1@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_bkt1", email="murid_bkt1@test.com")

        # Buat beberapa log dengan nilai
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Aljabar", nilai=80.0)
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Aljabar", nilai=85.0)
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Geometri", nilai=55.0)

        # Jalankan BKT update
        from app.services.plan_service import update_knowledge_states
        update_knowledge_states(db, murid.id, kelas.id)

        # Cek hasilnya di database
        from app.models.models import KnowledgeState
        ks_list = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid.id
        ).all()
        db.close()

        ks_map = {ks.topik: float(ks.p_knowledge) for ks in ks_list}

        assert "Aljabar"  in ks_map
        assert "Geometri" in ks_map
        # Aljabar harusnya lebih tinggi karena nilai lebih baik
        assert ks_map["Aljabar"] > ks_map["Geometri"]

    def test_bkt_update_upsert_tidak_duplikat(self, client):
        """✅ Panggil update_knowledge_states dua kali tidak boleh buat duplikat di DB."""
        db = TestingSessionLocal()
        guru  = buat_pengajar(db, nama="guru_bkt2", email="guru_bkt2@test.com")
        kelas = buat_kelas(db, guru.id)
        murid = buat_murid(db, nama="murid_bkt2", email="murid_bkt2@test.com")
        buat_log_db(db, kelas.id, murid_id=murid.id, topik="Aljabar", nilai=80.0)

        from app.services.plan_service import update_knowledge_states
        from app.models.models import KnowledgeState

        # Panggil dua kali
        update_knowledge_states(db, murid.id, kelas.id)
        update_knowledge_states(db, murid.id, kelas.id)

        count = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid.id,
            KnowledgeState.topik == "Aljabar",
        ).count()
        db.close()

        # Harus hanya ada 1 record, bukan 2
        assert count == 1
