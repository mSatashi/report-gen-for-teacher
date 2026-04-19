import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import (
    fake_id, fake_pengguna, fake_murid, fake_kelas,
    fake_rencana_studi, mock_db,
)
from app.schemas.schemas import RencanaStudiResponse
 
 
def _make_rencana_response(**kwargs) -> RencanaStudiResponse:
    defaults = dict(
        id=fake_id(),
        kelas_id=fake_id(),
        murid_id=None,
        waktu=datetime(2025, 3, 15),
        daftar_rekomendasi_materi=["Fake Materi A", "Fake Materi B"],
        estimasi_waktu_selesai=None,
        catatan_analisa="Fake catatan analisa rencana studi.",
        jadwal_mingguan={"Senin": "Fake Materi A"},
        version=1,
    )
    defaults.update(kwargs)
    return RencanaStudiResponse(**defaults)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestListRencana — GET /plan/kelas/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestListRencana:
 
    def test_list_rencana_memanggil_service(self):
        """✅ list_rencana harus memanggil get_rencana_by_kelas dengan kelas_id dan murid_id."""
        from app.routers.plan import list_rencana
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
 
        with patch("app.routers.plan.get_rencana_by_kelas", return_value=[]) as mock_svc:
            list_rencana(kelas_id=kelas_id, murid_id=None, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, kelas_id, None)
 
    def test_list_rencana_dengan_filter_murid(self):
        """✅ murid_id filter harus diteruskan ke get_rencana_by_kelas."""
        from app.routers.plan import list_rencana
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        murid_id = fake_id()
 
        with patch("app.routers.plan.get_rencana_by_kelas", return_value=[]) as mock_svc:
            list_rencana(kelas_id=kelas_id, murid_id=murid_id, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, kelas_id, murid_id)
 
    def test_list_rencana_return_list(self):
        """✅ Harus mengembalikan list rencana dari service."""
        from app.routers.plan import list_rencana
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        rencana1 = _make_rencana_response()
        rencana2 = _make_rencana_response()
 
        with patch("app.routers.plan.get_rencana_by_kelas", return_value=[rencana1, rencana2]):
            result = list_rencana(kelas_id=fake_id(), murid_id=None, current_user=current_user, db=db)
 
        assert len(result) == 2
 
    def test_list_rencana_kosong_return_list_kosong(self):
        """✅ Tidak ada rencana → return list kosong."""
        from app.routers.plan import list_rencana
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.plan.get_rencana_by_kelas", return_value=[]):
            result = list_rencana(kelas_id=fake_id(), murid_id=None, current_user=current_user, db=db)
 
        assert result == []
 
    def test_list_rencana_tidak_commit(self):
        """✅ list_rencana adalah read-only — tidak boleh commit."""
        from app.routers.plan import list_rencana
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.plan.get_rencana_by_kelas", return_value=[]):
            list_rencana(kelas_id=fake_id(), murid_id=None, current_user=current_user, db=db)
 
        db.commit.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestGetPlan — GET /plan/{plan_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestGetPlan:
 
    def test_get_plan_ditemukan_return_rencana(self):
        """✅ get_plan harus mengembalikan rencana yang ditemukan service."""
        from app.routers.plan import get_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        rencana = _make_rencana_response()
 
        with patch("app.routers.plan.get_rencana_by_id", return_value=rencana):
            result = get_plan(plan_id="fake-plan-id-001", current_user=current_user, db=db)
 
        assert result == rencana
 
    def test_get_plan_tidak_ditemukan_raise_404(self):
        """❌ Rencana tidak ada → raise 404."""
        from app.routers.plan import get_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.plan.get_rencana_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                get_plan(plan_id="fake-plan-id-tidak-ada", current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
        assert "rencana" in exc.value.detail.lower()
 
    def test_get_plan_memanggil_service_dengan_plan_id(self):
        """✅ Router harus meneruskan plan_id ke get_rencana_by_id."""
        from app.routers.plan import get_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        rencana = _make_rencana_response()
        target_id = "fake-plan-target-id"
 
        with patch("app.routers.plan.get_rencana_by_id", return_value=rencana) as mock_svc:
            get_plan(plan_id=target_id, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, target_id)
 
    def test_get_plan_tidak_commit(self):
        """✅ get_plan adalah read-only — tidak boleh commit."""
        from app.routers.plan import get_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        rencana = _make_rencana_response()
 
        with patch("app.routers.plan.get_rencana_by_id", return_value=rencana):
            get_plan(plan_id="fake-plan-id-readonly", current_user=current_user, db=db)
 
        db.commit.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestGeneratePlan — POST /plan/generate/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestGeneratePlan:
 
    def test_generate_plan_berhasil_return_rencana(self):
        """✅ generate_plan berhasil harus return RencanaStudiResponse."""
        from app.routers.plan import generate_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        rencana = _make_rencana_response(kelas_id=kelas_id)
 
        async def run():
            with patch("app.routers.plan.generate_rencana_studi", new=AsyncMock(return_value=rencana)):
                return await generate_plan(kelas_id=kelas_id, murid_id=None, current_user=current_user, db=db)
 
        result = asyncio.get_event_loop().run_until_complete(run())
 
        assert result.kelas_id == kelas_id
 
    def test_generate_plan_value_error_raise_404(self):
        """❌ ValueError dari service (kelas/murid tidak ada) → raise 404."""
        from app.routers.plan import generate_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        async def run():
            with patch("app.routers.plan.generate_rencana_studi",
                       new=AsyncMock(side_effect=ValueError("Kelas tidak ditemukan"))):
                return await generate_plan(kelas_id=fake_id(), murid_id=None, current_user=current_user, db=db)
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 404
 
    def test_generate_plan_exception_raise_500(self):
        """❌ Exception umum → raise 500."""
        from app.routers.plan import generate_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        async def run():
            with patch("app.routers.plan.generate_rencana_studi",
                       new=AsyncMock(side_effect=Exception("Fake AI error"))):
                return await generate_plan(kelas_id=fake_id(), murid_id=None, current_user=current_user, db=db)
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 500
        assert "gagal" in exc.value.detail.lower()
 
    def test_generate_plan_dengan_murid_id_diteruskan(self):
        """✅ murid_id opsional harus diteruskan ke generate_rencana_studi."""
        from app.routers.plan import generate_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        murid_id = fake_id()
        rencana = _make_rencana_response(kelas_id=kelas_id, murid_id=murid_id)
 
        async def run():
            with patch("app.routers.plan.generate_rencana_studi", new=AsyncMock(return_value=rencana)) as mock_svc:
                await generate_plan(kelas_id=kelas_id, murid_id=murid_id, current_user=current_user, db=db)
                mock_svc.assert_called_once_with(db, kelas_id, murid_id)
 
        asyncio.get_event_loop().run_until_complete(run())
 
    def test_generate_plan_tanpa_murid_id_generate_untuk_seluruh_kelas(self):
        """✅ Tanpa murid_id → generate untuk seluruh kelas (murid_id=None)."""
        from app.routers.plan import generate_plan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        rencana = _make_rencana_response(kelas_id=kelas_id)
 
        async def run():
            with patch("app.routers.plan.generate_rencana_studi", new=AsyncMock(return_value=rencana)) as mock_svc:
                await generate_plan(kelas_id=kelas_id, murid_id=None, current_user=current_user, db=db)
                mock_svc.assert_called_once_with(db, kelas_id, None)
 
        asyncio.get_event_loop().run_until_complete(run())
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestKnowledgeState — GET /plan/knowledge-state/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestKnowledgeState:
 
    def test_knowledge_state_memanggil_service(self):
        """✅ knowledge_state harus memanggil get_knowledge_state dengan db dan murid_id."""
        from app.routers.plan import knowledge_state
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
 
        with patch("app.routers.plan.get_knowledge_state", return_value={}) as mock_svc:
            knowledge_state(murid_id=murid_id, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, murid_id)
 
    def test_knowledge_state_return_dict_dengan_murid_id(self):
        """✅ Response harus berupa dict dengan key murid_id dan knowledge_state."""
        from app.routers.plan import knowledge_state
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        fake_ks = {"Fake Topik Aljabar": 0.75, "Fake Topik Geometri": 0.50}
 
        with patch("app.routers.plan.get_knowledge_state", return_value=fake_ks):
            result = knowledge_state(murid_id=murid_id, current_user=current_user, db=db)
 
        assert "murid_id"        in result
        assert "knowledge_state" in result
        assert result["murid_id"] == murid_id
 
    def test_knowledge_state_berisi_data_bkt_per_topik(self):
        """✅ knowledge_state harus berisi dict topik → nilai probabilitas (0.0–1.0)."""
        from app.routers.plan import knowledge_state
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        fake_ks = {
            "Fake Topik Aljabar":   0.85,
            "Fake Topik Geometri":  0.60,
            "Fake Topik Statistik": 0.30,
        }
 
        with patch("app.routers.plan.get_knowledge_state", return_value=fake_ks):
            result = knowledge_state(murid_id=murid_id, current_user=current_user, db=db)
 
        ks = result["knowledge_state"]
        assert "Fake Topik Aljabar" in ks
        assert ks["Fake Topik Aljabar"] == 0.85
 
    def test_knowledge_state_kosong_return_dict_kosong(self):
        """✅ Murid baru tanpa history → knowledge_state berupa dict kosong."""
        from app.routers.plan import knowledge_state
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
 
        with patch("app.routers.plan.get_knowledge_state", return_value={}):
            result = knowledge_state(murid_id=murid_id, current_user=current_user, db=db)
 
        assert result["knowledge_state"] == {}
 
    def test_knowledge_state_tidak_commit(self):
        """✅ knowledge_state adalah read-only — tidak boleh commit."""
        from app.routers.plan import knowledge_state
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.plan.get_knowledge_state", return_value={}):
            knowledge_state(murid_id=fake_id(), current_user=current_user, db=db)
 
        db.commit.assert_not_called()
        db.add.assert_not_called()
 
    def test_knowledge_state_nilai_antara_0_dan_1(self):
        """✅ Semua nilai knowledge_state harus berada di antara 0.0 dan 1.0."""
        from app.routers.plan import knowledge_state
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        fake_ks = {
            "Fake Topik A": 0.0,
            "Fake Topik B": 0.5,
            "Fake Topik C": 1.0,
        }
 
        with patch("app.routers.plan.get_knowledge_state", return_value=fake_ks):
            result = knowledge_state(murid_id=murid_id, current_user=current_user, db=db)
 
        for topik, nilai in result["knowledge_state"].items():
            assert 0.0 <= nilai <= 1.0, f"Nilai untuk '{topik}' di luar range: {nilai}"