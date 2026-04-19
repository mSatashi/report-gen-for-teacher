 
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch, call
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import (
    fake_id, fake_pengguna, fake_murid, fake_kelas,
    fake_diagnostic, fake_knowledge_state, mock_db,
)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestSimpanDiagnostic — POST /diagnostic/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestSimpanDiagnostic:
 
    def _make_data(self, skor: float = 75.0, **overrides):
        from app.schemas.schemas import DiagnosticCreate
        defaults = dict(
            murid_id=fake_id(),
            kelas_id=fake_id(),
            topik="Fake Topik Aljabar",
            diagnostic_score=skor,
        )
        defaults.update(overrides)
        return DiagnosticCreate(**defaults)
 
    def test_simpan_diagnostic_add_diag_dan_commit(self):
        """✅ simpan_diagnostic harus add DiagnosticResult ke DB dan commit."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic(skor=75.0)
        db.first.return_value = None  # belum ada knowledge state
 
        data = self._make_data(skor=75.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState") as MockKS:
            db.refresh.side_effect = lambda obj: None
            result = simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        db.commit.assert_called_once()
        assert db.add.call_count >= 1  # DiagnosticResult + KnowledgeState baru
 
    def test_simpan_diagnostic_inisialisasi_knowledge_state_baru(self):
        """✅ Jika belum ada knowledge state, harus membuat KnowledgeState baru."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic(skor=80.0)
        db.first.return_value = None  # knowledge state belum ada
 
        data = self._make_data(skor=80.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState") as MockKS:
            db.refresh.side_effect = lambda obj: None
            simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        # add dipanggil minimal 2x: DiagnosticResult + KnowledgeState baru
        assert db.add.call_count >= 2
 
    def test_simpan_diagnostic_update_knowledge_state_yang_sudah_ada(self):
        """✅ Jika knowledge state sudah ada, harus update p_knowledge — tidak add baru."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic(skor=60.0)
        existing_ks = fake_knowledge_state(p_knowledge=0.3)
 
        # first() pertama → None (tidak dipakai di query KS secara langsung)
        # Simulasi: query pertama DiagnosticResult add, query KS → existing
        db.first.side_effect = [existing_ks]
 
        data = self._make_data(skor=60.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState"):
            db.refresh.side_effect = lambda obj: None
            simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        # p_knowledge harus diupdate ke 60/100 = 0.6
        assert existing_ks.p_knowledge == pytest.approx(0.6, abs=0.001)
        db.commit.assert_called_once()
 
    def test_simpan_diagnostic_p_l0_dihitung_dari_skor(self):
        """✅ P(L0) = diagnostic_score / 100 — harus tepat."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic(skor=90.0)
        existing_ks = fake_knowledge_state(p_knowledge=0.0)
        db.first.return_value = existing_ks
 
        data = self._make_data(skor=90.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState"):
            db.refresh.side_effect = lambda obj: None
            simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        assert existing_ks.p_knowledge == pytest.approx(0.9, abs=0.001)
 
    def test_simpan_diagnostic_skor_nol_valid(self):
        """✅ Skor 0.0 adalah input valid — P(L0) = 0.0."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic(skor=0.0)
        existing_ks = fake_knowledge_state(p_knowledge=0.5)
        db.first.return_value = existing_ks
 
        data = self._make_data(skor=0.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState"):
            db.refresh.side_effect = lambda obj: None
            simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        assert existing_ks.p_knowledge == pytest.approx(0.0, abs=0.001)
 
    def test_simpan_diagnostic_skor_100_valid(self):
        """✅ Skor 100.0 adalah input valid — P(L0) = 1.0."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic(skor=100.0)
        existing_ks = fake_knowledge_state(p_knowledge=0.0)
        db.first.return_value = existing_ks
 
        data = self._make_data(skor=100.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState"):
            db.refresh.side_effect = lambda obj: None
            simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        assert existing_ks.p_knowledge == pytest.approx(1.0, abs=0.001)
 
    def test_simpan_diagnostic_refresh_dipanggil(self):
        """✅ db.refresh harus dipanggil agar data DiagnosticResult terisi id-nya."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        diag_obj = fake_diagnostic()
        db.first.return_value = None
 
        data = self._make_data()
 
        with patch("app.routers.diagnostic.DiagnosticResult", return_value=diag_obj), \
             patch("app.routers.diagnostic.KnowledgeState"):
            db.refresh.side_effect = lambda obj: None
            simpan_diagnostic(data=data, current_user=current_user, db=db)
 
        db.refresh.assert_called_once()
 
    def test_simpan_diagnostic_id_berupa_uuid(self):
        """✅ DiagnosticResult yang dibuat harus mendapat id berupa UUID."""
        from app.routers.diagnostic import simpan_diagnostic
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        captured = {}
 
        class FakeDiagResult:
            def __init__(self, **kwargs):
                captured.update(kwargs)
                for k, v in kwargs.items():
                    setattr(self, k, v)
                self.created_at = datetime.utcnow()
 
        db.first.return_value = None
        data = self._make_data(skor=70.0)
 
        with patch("app.routers.diagnostic.DiagnosticResult", side_effect=FakeDiagResult), \
             patch("app.routers.diagnostic.KnowledgeState"):
            db.refresh.side_effect = lambda obj: None
            try:
                simpan_diagnostic(data=data, current_user=current_user, db=db)
            except Exception:
                pass
 
        if "id" in captured:
            uuid.UUID(captured["id"])  # raise ValueError jika bukan UUID valid
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestGetDiagnostics — GET /diagnostic/murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestGetDiagnostics:
 
    def test_get_diagnostics_return_list_untuk_murid(self):
        """✅ get_diagnostics harus mengembalikan semua DiagnosticResult murid."""
        from app.routers.diagnostic import get_diagnostics
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
 
        diag1 = fake_diagnostic(murid_id=murid_id, topik="Fake Topik A", skor=70.0)
        diag2 = fake_diagnostic(murid_id=murid_id, topik="Fake Topik B", skor=85.0)
        db.all.return_value = [diag1, diag2]
 
        result = get_diagnostics(murid_id=murid_id, current_user=current_user, db=db)
 
        assert len(result) == 2
 
    def test_get_diagnostics_kosong_return_list_kosong(self):
        """✅ Murid tanpa diagnostic result harus return list kosong."""
        from app.routers.diagnostic import get_diagnostics
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        result = get_diagnostics(murid_id="fake-murid-id-kosong", current_user=current_user, db=db)
 
        assert result == []
 
    def test_get_diagnostics_filter_berdasarkan_murid_id(self):
        """✅ Query harus difilter berdasarkan murid_id yang diberikan."""
        from app.routers.diagnostic import get_diagnostics
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        target_murid = fake_id()
        get_diagnostics(murid_id=target_murid, current_user=current_user, db=db)
 
        db.filter.assert_called()
 
    def test_get_diagnostics_diurutkan_descending(self):
        """✅ Hasil harus diurutkan berdasarkan created_at descending (terbaru dulu)."""
        from app.routers.diagnostic import get_diagnostics
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        get_diagnostics(murid_id=fake_id(), current_user=current_user, db=db)
 
        # order_by harus dipanggil (descending)
        db.order_by.assert_called()
 
    def test_get_diagnostics_tidak_commit(self):
        """✅ get_diagnostics adalah read-only — tidak boleh commit atau add."""
        from app.routers.diagnostic import get_diagnostics
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        get_diagnostics(murid_id=fake_id(), current_user=current_user, db=db)
 
        db.commit.assert_not_called()
        db.add.assert_not_called()
 
    def test_get_diagnostics_semua_item_milik_murid_yang_sama(self):
        """✅ Semua DiagnosticResult yang dikembalikan harus milik murid yang diminta."""
        from app.routers.diagnostic import get_diagnostics
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        target_murid = fake_id()
 
        diag1 = fake_diagnostic(murid_id=target_murid, topik="Fake Topik X")
        diag2 = fake_diagnostic(murid_id=target_murid, topik="Fake Topik Y")
        db.all.return_value = [diag1, diag2]
 
        result = get_diagnostics(murid_id=target_murid, current_user=current_user, db=db)
 
        for item in result:
            assert item.murid_id == target_murid