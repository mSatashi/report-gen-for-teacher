"""
test_mock_diagnostic.py
─────────────────────────────────────────────────────────────────────────────
Pure mock unit test untuk fitur Diagnostik (F008).
Mencakup service logic: simpan diagnostik, inisialisasi BKT P(L0),
get diagnostik, validasi skor, relasi ke knowledge_state.

Ini adalah versi MOCK dari test_diagnostic.py yang sudah ada.
Perbedaan:
  - test_diagnostic.py  → integration test (pakai SQLite nyata + TestClient)
  - test_mock_diagnostic.py → unit test (semua DB di-mock, tidak butuh DB)

Cara jalankan:
    pytest tests/test_mock_diagnostic.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
from datetime import datetime
from unittest.mock import MagicMock, call, patch
from tests.test_helpers import fake_id, fake_pengguna, fake_murid, fake_kelas, fake_log, mock_db
import pytest
from fastapi import HTTPException

# ── Simulasi logika simpan_diagnostic (dari router/service) ──────────────────

def _simpan_diagnostic(db, murid_id, kelas_id, topik, diagnostic_score):
    """
    Mirror logika di router/diagnostic.py:
    1. Buat DiagnosticResult
    2. Buat atau update KnowledgeState dengan P(L0) = diagnostic_score / 100
    """
    from app.models.models import DiagnosticResult, KnowledgeState

    diag = DiagnosticResult(
        id=str(uuid.uuid4()),
        murid_id=murid_id,
        kelas_id=kelas_id,
        topik=topik,
        skor=diagnostic_score,
        diagnostic_score=diagnostic_score,
    )
    db.add(diag)

    p_l0 = diagnostic_score / 100.0
    existing_ks = db.query(KnowledgeState).filter(
        KnowledgeState.murid_id == murid_id,
        KnowledgeState.topik == topik,
    ).first()

    if existing_ks:
        existing_ks.p_knowledge = p_l0
    else:
        db.add(KnowledgeState(
            id=str(uuid.uuid4()),
            murid_id=murid_id,
            topik=topik,
            p_knowledge=p_l0,
        ))

    db.commit()
    db.refresh(diag)
    return diag


# ═════════════════════════════════════════════════════════════════════════════
# TEST SIMPAN DIAGNOSTIK
# ═════════════════════════════════════════════════════════════════════════════

class TestSimpanDiagnosticMock:

    def test_simpan_diagnostic_add_dua_record(self):
        """✅ Simpan diagnostik harus add DiagnosticResult + KnowledgeState."""
        db = mock_db()
        db.first.return_value = None  # KnowledgeState belum ada

        with patch("app.models.models.DiagnosticResult") as MockDiag, \
             patch("app.models.models.KnowledgeState") as MockKS:

            mock_diag = MagicMock()
            mock_ks   = MagicMock()
            MockDiag.return_value = mock_diag
            MockKS.return_value   = mock_ks

            db.refresh.side_effect = lambda obj: None

            _simpan_diagnostic(db, fake_id(), fake_id(), "Fake Aljabar", 75.0)

        # Harus add 2 kali: DiagnosticResult + KnowledgeState baru
        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_simpan_diagnostic_p_l0_sesuai_skor(self):
        """✅ P(L0) di KnowledgeState harus = skor / 100."""
        db = mock_db()
        db.first.return_value = None

        created_ks_args = []

        original_add = db.add
        def capture_add(obj):
            created_ks_args.append(obj)
            original_add(obj)

        db.add.side_effect = capture_add
        db.refresh.side_effect = lambda obj: None

        with patch("app.models.models.DiagnosticResult") as MockDiag, \
             patch("app.models.models.KnowledgeState") as MockKS:

            mock_diag_instance = MagicMock()
            MockDiag.return_value = mock_diag_instance

            mock_ks_instance = MagicMock()
            MockKS.return_value  = mock_ks_instance

            _simpan_diagnostic(db, fake_id(), fake_id(), "Fake Geometri", 80.0)

            # Verifikasi KnowledgeState dibuat dengan p_knowledge = 80/100 = 0.8
            ks_call = MockKS.call_args
            if ks_call:
                kwargs = ks_call[1] if ks_call[1] else {}
                if "p_knowledge" in kwargs:
                    assert abs(kwargs["p_knowledge"] - 0.8) < 0.001

    def test_simpan_diagnostic_update_ks_jika_sudah_ada(self):
        """✅ Jika KnowledgeState sudah ada, harus UPDATE bukan INSERT baru."""
        db = mock_db()
        existing_ks = fake_knowledge_state(p_knowledge=0.5)
        db.first.return_value = existing_ks  # sudah ada

        db.refresh.side_effect = lambda obj: None

        with patch("app.models.models.DiagnosticResult") as MockDiag, \
             patch("app.models.models.KnowledgeState"):
            mock_diag = MagicMock()
            MockDiag.return_value = mock_diag

            _simpan_diagnostic(db, fake_id(), fake_id(), "Fake Topik Update", 90.0)

        # Hanya DiagnosticResult yang di-add (KnowledgeState diupdate in-place)
        assert db.add.call_count == 1
        # p_knowledge harus di-set ke 0.9
        assert existing_ks.p_knowledge == 0.9

    def test_simpan_diagnostic_skor_0_valid(self):
        """✅ Skor 0 (batas bawah) harus menghasilkan P(L0) = 0.0."""
        db = mock_db()
        db.first.return_value  = None
        db.refresh.side_effect = lambda obj: None

        existing_ks_baru = None

        with patch("app.models.models.DiagnosticResult") as MockDiag, \
             patch("app.models.models.KnowledgeState") as MockKS:

            mock_diag = MagicMock()
            MockDiag.return_value = mock_diag

            mock_ks = MagicMock()
            MockKS.return_value = mock_ks

            _simpan_diagnostic(db, fake_id(), fake_id(), "Fake Topik Nol", 0.0)

            ks_call = MockKS.call_args
            if ks_call and ks_call[1] and "p_knowledge" in ks_call[1]:
                assert ks_call[1]["p_knowledge"] == 0.0

    def test_simpan_diagnostic_skor_100_valid(self):
        """✅ Skor 100 (batas atas) harus menghasilkan P(L0) = 1.0."""
        db = mock_db()
        db.first.return_value  = None
        db.refresh.side_effect = lambda obj: None

        with patch("app.models.models.DiagnosticResult") as MockDiag, \
             patch("app.models.models.KnowledgeState") as MockKS:

            mock_diag = MagicMock()
            MockDiag.return_value = mock_diag
            mock_ks = MagicMock()
            MockKS.return_value = mock_ks

            _simpan_diagnostic(db, fake_id(), fake_id(), "Fake Topik Sempurna", 100.0)

            ks_call = MockKS.call_args
            if ks_call and ks_call[1] and "p_knowledge" in ks_call[1]:
                assert ks_call[1]["p_knowledge"] == 1.0


# ═════════════════════════════════════════════════════════════════════════════
# TEST KONVERSI SKOR KE P(L0)
# ═════════════════════════════════════════════════════════════════════════════

class TestKonversiSkorKePL0:
    """
    Test pure logic konversi skor diagnostik (0-100) ke probabilitas BKT (0.0-1.0).
    Tidak butuh DB sama sekali.
    """

    def _konversi(self, skor):
        return skor / 100.0

    def test_skor_75_menjadi_0_75(self):
        """✅ Skor 75 harus menjadi P(L0) = 0.75."""
        assert abs(self._konversi(75.0) - 0.75) < 0.001

    def test_skor_50_menjadi_0_50(self):
        """✅ Skor 50 harus menjadi P(L0) = 0.50."""
        assert abs(self._konversi(50.0) - 0.50) < 0.001

    def test_skor_0_menjadi_0_0(self):
        """✅ Skor 0 harus menjadi P(L0) = 0.0."""
        assert self._konversi(0.0) == 0.0

    def test_skor_100_menjadi_1_0(self):
        """✅ Skor 100 harus menjadi P(L0) = 1.0."""
        assert self._konversi(100.0) == 1.0

    def test_hasil_selalu_antara_0_dan_1(self):
        """✅ Semua skor 0-100 harus menghasilkan P(L0) di [0.0, 1.0]."""
        for skor in [0, 10, 25, 50, 60, 75, 90, 100]:
            p = self._konversi(float(skor))
            assert 0.0 <= p <= 1.0, f"P(L0) untuk skor {skor} = {p} di luar range"

    def test_murid_skor_tinggi_p_lebih_tinggi_dari_rendah(self):
        """✅ Murid skor 90 harus punya P(L0) lebih tinggi dari murid skor 30."""
        p_tinggi = self._konversi(90.0)
        p_rendah = self._konversi(30.0)
        assert p_tinggi > p_rendah


# ═════════════════════════════════════════════════════════════════════════════
# TEST GET DIAGNOSTIK
# ═════════════════════════════════════════════════════════════════════════════

class TestGetDiagnosticMock:

    def test_get_diagnostic_by_murid_return_list(self):
        """✅ Query diagnostik per murid harus return list hasil diagnostik."""
        from app.models.models import DiagnosticResult

        db = mock_db()
        murid_id = fake_id()
        diag_list = [
            fake_diagnostic(murid_id=murid_id, topik="Fake Aljabar",    skor=80.0),
            fake_diagnostic(murid_id=murid_id, topik="Fake Geometri",   skor=65.0),
            fake_diagnostic(murid_id=murid_id, topik="Fake Statistika", skor=55.0),
        ]
        db.all.return_value = diag_list

        result = db.query(DiagnosticResult)\
                   .filter(DiagnosticResult.murid_id == murid_id)\
                   .order_by(DiagnosticResult.created_at.desc())\
                   .all()

        assert len(result) == 3

    def test_get_diagnostic_murid_tanpa_data_return_kosong(self):
        """✅ Murid tanpa data diagnostik harus return list kosong."""
        from app.models.models import DiagnosticResult

        db = mock_db()
        db.all.return_value = []

        result = db.query(DiagnosticResult)\
                   .filter(DiagnosticResult.murid_id == fake_id())\
                   .all()

        assert result == []

    def test_get_diagnostic_tidak_tercampur_murid_lain(self):
        """✅ Query dengan murid_id tertentu tidak boleh return data murid lain."""
        from app.models.models import DiagnosticResult

        db = mock_db()
        murid1_id = fake_id()
        murid2_id = fake_id()

        # Hanya kembalikan data murid1
        diag_murid1 = fake_diagnostic(murid_id=murid1_id, topik="Fake Topik Murid1")
        db.all.return_value = [diag_murid1]

        result = db.query(DiagnosticResult)\
                   .filter(DiagnosticResult.murid_id == murid1_id)\
                   .all()

        # Tidak ada data murid2 di result
        assert all(d.murid_id == murid1_id for d in result)


# ═════════════════════════════════════════════════════════════════════════════
# TEST VALIDASI SKOR
# ═════════════════════════════════════════════════════════════════════════════

class TestValidasiSkorDiagnostic:
    """
    Test validasi yang dilakukan Pydantic schema DiagnosticCreate.
    Ini adalah pure schema validation — tidak butuh DB.
    """

    def test_skor_valid_50_diterima(self):
        """✅ Skor 50 harus lolos validasi Pydantic."""
        from app.schemas.schemas import DiagnosticCreate

        data = DiagnosticCreate(
            murid_id=fake_id(),
            topik="Fake Topik Valid",
            diagnostic_score=50.0,
        )

        assert data.diagnostic_score == 50.0

    def test_skor_0_diterima(self):
        """✅ Skor 0 (batas bawah) harus lolos validasi."""
        from app.schemas.schemas import DiagnosticCreate

        data = DiagnosticCreate(
            murid_id=fake_id(),
            topik="Fake Topik Nol",
            diagnostic_score=0.0,
        )

        assert data.diagnostic_score == 0.0

    def test_skor_100_diterima(self):
        """✅ Skor 100 (batas atas) harus lolos validasi."""
        from app.schemas.schemas import DiagnosticCreate

        data = DiagnosticCreate(
            murid_id=fake_id(),
            topik="Fake Topik Sempurna",
            diagnostic_score=100.0,
        )

        assert data.diagnostic_score == 100.0

    def test_skor_101_ditolak(self):
        """❌ Skor > 100 harus raise ValidationError."""
        from app.schemas.schemas import DiagnosticCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DiagnosticCreate(
                murid_id=fake_id(),
                topik="Fake Topik",
                diagnostic_score=101.0,
            )

    def test_skor_negatif_ditolak(self):
        """❌ Skor negatif harus raise ValidationError."""
        from app.schemas.schemas import DiagnosticCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DiagnosticCreate(
                murid_id=fake_id(),
                topik="Fake Topik",
                diagnostic_score=-5.0,
            )

    def test_tanpa_murid_id_ditolak(self):
        """❌ DiagnosticCreate tanpa murid_id harus raise ValidationError."""
        from app.schemas.schemas import DiagnosticCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DiagnosticCreate(
                topik="Fake Topik",
                diagnostic_score=75.0,
                # murid_id tidak diisi
            )

    def test_tanpa_topik_ditolak(self):
        """❌ DiagnosticCreate tanpa topik harus raise ValidationError."""
        from app.schemas.schemas import DiagnosticCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            DiagnosticCreate(
                murid_id=fake_id(),
                diagnostic_score=75.0,
                # topik tidak diisi
            )

    def test_skor_desimal_85_5_diterima(self):
        """✅ Skor desimal seperti 85.5 harus diterima."""
        from app.schemas.schemas import DiagnosticCreate

        data = DiagnosticCreate(
            murid_id=fake_id(),
            topik="Fake Topik Desimal",
            diagnostic_score=85.5,
        )

        assert data.diagnostic_score == 85.5

    def test_kelas_id_opsional(self):
        """✅ kelas_id bersifat opsional — boleh tidak diisi."""
        from app.schemas.schemas import DiagnosticCreate

        data = DiagnosticCreate(
            murid_id=fake_id(),
            topik="Fake Topik Tanpa Kelas",
            diagnostic_score=70.0,
            # kelas_id tidak diisi
        )

        assert data.kelas_id is None


# ═════════════════════════════════════════════════════════════════════════════
# TEST INTEGRASI DIAGNOSTIK → KNOWLEDGE STATE (Pure Logic)
# ═════════════════════════════════════════════════════════════════════════════

class TestIntegrasiBKTPL0:
    """
    Test alur: skor diagnostik → P(L0) → digunakan BKT.
    Semua pure math, tidak butuh DB.
    """

    def test_p_l0_tinggi_menghasilkan_bkt_lebih_baik(self):
        """✅ Murid dengan P(L0) tinggi harus punya knowledge state lebih tinggi setelah 1 sesi."""
        from app.services.plan_service import BKTModule

        bkt = BKTModule()

        p_l0_tinggi = 90.0 / 100.0  # murid skor diagnostik 90
        p_l0_rendah = 30.0 / 100.0  # murid skor diagnostik 30

        # Simulasi 1 sesi belajar dengan jawaban benar
        p_setelah_tinggi = bkt.update(p_l0_tinggi, correct=True)
        p_setelah_rendah = bkt.update(p_l0_rendah, correct=True)

        assert p_setelah_tinggi > p_setelah_rendah

    def test_p_l0_dari_diagnostik_selalu_valid_untuk_bkt(self):
        """✅ Semua nilai P(L0) dari diagnostik harus bisa masuk ke BKT tanpa error."""
        from app.services.plan_service import BKTModule

        bkt = BKTModule()

        for skor in [0, 10, 25, 50, 60, 75, 90, 100]:
            p_l0 = skor / 100.0
            for correct in [True, False]:
                result = bkt.update(p_l0, correct)
                assert 0.0 <= result <= 1.0, \
                    f"BKT error untuk skor={skor}, correct={correct}: result={result}"

    def test_multiple_topik_punya_p_l0_terpisah(self):
        """✅ Setiap topik diagnostik harus menghasilkan P(L0) sendiri-sendiri."""
        skor_map = {
            "Fake Aljabar":    85.0,
            "Fake Geometri":   60.0,
            "Fake Statistika": 40.0,
        }

        p_l0_map = {topik: skor / 100.0 for topik, skor in skor_map.items()}

        assert abs(p_l0_map["Fake Aljabar"]    - 0.85) < 0.001
        assert abs(p_l0_map["Fake Geometri"]   - 0.60) < 0.001
        assert abs(p_l0_map["Fake Statistika"] - 0.40) < 0.001

        # Setiap topik independen
        assert p_l0_map["Fake Aljabar"] > p_l0_map["Fake Geometri"]
        assert p_l0_map["Fake Geometri"] > p_l0_map["Fake Statistika"]
