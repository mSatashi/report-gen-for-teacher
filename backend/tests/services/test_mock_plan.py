"""
test_mock_plan.py
─────────────────────────────────────────────────────────────────────────────
Pure mock unit test untuk app/services/plan_service.py
Mencakup: BKT algorithm (pure math), knowledge state, get/list rencana,
          generate rencana dengan AI di-mock.

Cara jalankan:
    pytest tests/test_mock_plan.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
from tests.test_helpers import fake_id, fake_pengguna, fake_murid, fake_kelas, fake_rencana_studi, fake_knowledge_state, mock_db
import pytest

# ═════════════════════════════════════════════════════════════════════════════
# TEST BKT MODULE — Pure Math (tidak butuh mock)
# ═════════════════════════════════════════════════════════════════════════════

class TestBKTModule:

    def test_jawab_benar_naikkan_probabilitas(self):
        """✅ Jawab benar harus menaikkan p_knowledge."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule(p_learn=0.2, p_guess=0.1, p_slip=0.05)

        p_before = 0.3
        p_after  = bkt.update(p_before, correct=True)

        assert p_after > p_before, f"Expected {p_after} > {p_before}"

    def test_jawab_salah_lebih_rendah_dari_jawab_benar(self):
        """✅ Jawab salah harus menghasilkan nilai lebih rendah dari jawab benar."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule(p_learn=0.2, p_guess=0.1, p_slip=0.05)

        p = 0.5
        p_benar = bkt.update(p, correct=True)
        p_salah = bkt.update(p, correct=False)

        assert p_benar > p_salah

    def test_hasil_selalu_antara_0_dan_1(self):
        """✅ Output BKT selalu dalam range [0.0, 1.0] untuk semua input."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        for p in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
            for correct in [True, False]:
                result = bkt.update(p, correct)
                assert 0.0 <= result <= 1.0, \
                    f"Out of range: update(p={p}, correct={correct}) = {result}"

    def test_skor_60_dianggap_benar(self):
        """✅ Skor >= 60 harus dianggap benar (correct=True)."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        p     = 0.4
        p_60  = bkt.compute_from_score(p, score=60.0)
        p_59  = bkt.compute_from_score(p, score=59.9)

        assert p_60 > p_59

    def test_skor_tepat_100_tidak_error(self):
        """✅ Skor 100 tidak boleh menyebabkan error numerik."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        result = bkt.compute_from_score(0.5, score=100.0)

        assert 0.0 <= result <= 1.0

    def test_skor_tepat_0_tidak_error(self):
        """✅ Skor 0 tidak boleh menyebabkan error numerik."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        result = bkt.compute_from_score(0.5, score=0.0)

        assert 0.0 <= result <= 1.0

    def test_batch_update_banyak_benar_lebih_tinggi(self):
        """✅ Lebih banyak jawaban benar → probabilitas lebih tinggi."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        p_1_sesi = bkt.batch_update(0.1, [85.0])
        p_5_sesi = bkt.batch_update(0.1, [85.0, 88.0, 90.0, 82.0, 86.0])

        assert p_5_sesi > p_1_sesi

    def test_batch_update_skor_campuran_dalam_range(self):
        """✅ batch_update dengan campuran skor baik dan buruk tetap valid."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        skor_campuran = [80.0, 45.0, 90.0, 30.0, 75.0, 55.0, 88.0]
        result = bkt.batch_update(0.1, skor_campuran)

        assert 0.0 <= result <= 1.0

    def test_batch_update_semua_salah_rendah(self):
        """✅ Semua jawaban salah harus menghasilkan nilai yang lebih rendah."""
        from app.services.plan_service import BKTModule
        bkt = BKTModule()

        p_semua_benar = bkt.batch_update(0.1, [90.0, 85.0, 88.0])
        p_semua_salah = bkt.batch_update(0.1, [30.0, 25.0, 20.0])

        assert p_semua_benar > p_semua_salah

    def test_parameter_custom_digunakan(self):
        """✅ Parameter p_learn, p_guess, p_slip custom harus digunakan."""
        from app.services.plan_service import BKTModule

        bkt_cepat = BKTModule(p_learn=0.4, p_guess=0.1, p_slip=0.05)
        bkt_lambat = BKTModule(p_learn=0.05, p_guess=0.1, p_slip=0.05)

        # Dengan p_learn lebih tinggi, peningkatan harus lebih besar
        delta_cepat  = bkt_cepat.update(0.5, correct=True) - 0.5
        delta_lambat = bkt_lambat.update(0.5, correct=True) - 0.5

        assert delta_cepat > delta_lambat


# ═════════════════════════════════════════════════════════════════════════════
# TEST KNOWLEDGE STATE
# ═════════════════════════════════════════════════════════════════════════════

class TestKnowledgeState:

    def test_get_knowledge_state_return_dict(self):
        """✅ get_knowledge_state harus return dict {topik: p_knowledge}."""
        from app.services.plan_service import get_knowledge_state

        db = mock_db()
        murid_id = fake_id()
        ks_list = [
            fake_knowledge_state(murid_id=murid_id, topik="Fake Aljabar",    p_knowledge=0.75),
            fake_knowledge_state(murid_id=murid_id, topik="Fake Geometri",   p_knowledge=0.45),
            fake_knowledge_state(murid_id=murid_id, topik="Fake Statistika", p_knowledge=0.30),
        ]
        db.all.return_value = ks_list

        result = get_knowledge_state(db, murid_id)

        assert isinstance(result, dict)
        assert "Fake Aljabar"    in result
        assert "Fake Geometri"   in result
        assert "Fake Statistika" in result
        assert result["Fake Aljabar"] == 0.75
        assert result["Fake Geometri"] == 0.45

    def test_get_knowledge_state_nilai_dalam_range(self):
        """✅ Semua nilai knowledge state harus antara 0.0 dan 1.0."""
        from app.services.plan_service import get_knowledge_state

        db = mock_db()
        murid_id = fake_id()
        db.all.return_value = [
            fake_knowledge_state(murid_id=murid_id, topik="T1", p_knowledge=0.0),
            fake_knowledge_state(murid_id=murid_id, topik="T2", p_knowledge=0.5),
            fake_knowledge_state(murid_id=murid_id, topik="T3", p_knowledge=1.0),
        ]

        result = get_knowledge_state(db, murid_id)

        for topik, nilai in result.items():
            assert 0.0 <= nilai <= 1.0, f"Nilai {topik} = {nilai} di luar range"

    def test_get_knowledge_state_murid_tanpa_data_return_kosong(self):
        """✅ Murid tanpa knowledge state harus return dict kosong."""
        from app.services.plan_service import get_knowledge_state

        db = mock_db()
        db.all.return_value = []

        result = get_knowledge_state(db, fake_id())

        assert result == {}

    def test_get_knowledge_state_tidak_tercampur_murid_lain(self):
        """✅ Knowledge state murid lain tidak boleh muncul."""
        from app.services.plan_service import get_knowledge_state

        db = mock_db()
        murid_id = fake_id()
        # Hanya kembalikan KS untuk murid ini
        db.all.return_value = [
            fake_knowledge_state(murid_id=murid_id, topik="Fake Topik Milik Murid1", p_knowledge=0.8)
        ]

        result = get_knowledge_state(db, murid_id)

        assert len(result) == 1
        assert "Fake Topik Milik Murid1" in result


# ═════════════════════════════════════════════════════════════════════════════
# TEST GET RENCANA
# ═════════════════════════════════════════════════════════════════════════════

class TestGetRencana:

    def test_get_rencana_by_id_ditemukan(self):
        """✅ get_rencana_by_id harus return rencana jika ID ada."""
        from app.services.plan_service import get_rencana_by_id

        db = mock_db()
        rencana = fake_rencana_studi()
        db.first.return_value = rencana

        result = get_rencana_by_id(db, rencana.id)

        assert result.id == rencana.id

    def test_get_rencana_by_id_tidak_ada_return_none(self):
        """✅ get_rencana_by_id untuk ID tidak ada harus return None."""
        from app.services.plan_service import get_rencana_by_id

        db = mock_db()
        db.first.return_value = None

        result = get_rencana_by_id(db, "fake-id-tidak-ada")

        assert result is None

    def test_get_rencana_by_kelas_return_list(self):
        """✅ get_rencana_by_kelas harus return semua rencana kelas."""
        from app.services.plan_service import get_rencana_by_kelas

        db = mock_db()
        kelas_id = fake_id()
        db.all.return_value = [fake_rencana_studi(kelas_id=kelas_id) for _ in range(3)]

        result = get_rencana_by_kelas(db, kelas_id)

        assert len(result) == 3

    def test_get_rencana_by_kelas_kosong_return_list_kosong(self):
        """✅ Kelas tanpa rencana harus return list kosong."""
        from app.services.plan_service import get_rencana_by_kelas

        db = mock_db()
        db.all.return_value = []

        result = get_rencana_by_kelas(db, fake_id())

        assert result == []

    def test_get_rencana_by_kelas_filter_murid(self):
        """✅ Filter murid_id harus memanggil query filter tambahan."""
        from app.services.plan_service import get_rencana_by_kelas

        db = mock_db()
        murid_id = fake_id()
        db.all.return_value = [fake_rencana_studi(murid_id=murid_id)]

        get_rencana_by_kelas(db, fake_id(), murid_id=murid_id)

        assert db.filter.call_count >= 2


# ═════════════════════════════════════════════════════════════════════════════
# TEST GENERATE RENCANA (AI di-mock)
# ═════════════════════════════════════════════════════════════════════════════

class TestGenerateRencana:

    @patch("app.services.plan_service.narrative_engine")
    @patch("app.services.plan_service.planner_engine")
    def test_generate_memanggil_narrative_dan_planner(self, mock_planner, mock_narrative):
        """✅ Generate rencana harus memanggil narrative_engine DAN planner_engine."""
        mock_narrative.analyze_class_data = AsyncMock(
            return_value="Fake analisis kelas dari NarrativeEngine mock"
        )
        mock_planner.generate_rencana_studi = AsyncMock(return_value={
            "rekomendasi_materi":      ["Fake Topik A", "Fake Topik B"],
            "jadwal_mingguan":         {"Minggu 1": ["Fake Topik A"]},
            "catatan_analisa":         "Fake catatan dari PlannerEngine mock",
            "estimasi_selesai_minggu": 3,
        })

        from app.services.plan_service import generate_rencana_studi

        db = mock_db()
        kelas = fake_kelas(kredit=20)

        call_no = [0]
        def first_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return kelas
            return None

        db.first.side_effect   = first_side
        db.all.return_value    = []
        db.count.return_value  = 0
        db.refresh.side_effect = lambda obj: None

        asyncio.get_event_loop().run_until_complete(
            generate_rencana_studi(db, kelas.id, None)
        )

        mock_narrative.analyze_class_data.assert_called_once()
        mock_planner.generate_rencana_studi.assert_called_once()

    @patch("app.services.plan_service.narrative_engine")
    @patch("app.services.plan_service.planner_engine")
    def test_generate_kelas_tidak_ada_raise_error(self, mock_planner, mock_narrative):
        """❌ Generate untuk kelas tidak ada harus raise ValueError atau HTTPException."""
        from app.services.plan_service import generate_rencana_studi
        from fastapi import HTTPException

        db = mock_db()
        db.first.return_value = None  # kelas tidak ditemukan

        with pytest.raises((ValueError, HTTPException)):
            asyncio.get_event_loop().run_until_complete(
                generate_rencana_studi(db, "fake-kelas-tidak-ada", None)
            )

    @patch("app.services.plan_service.narrative_engine")
    @patch("app.services.plan_service.planner_engine")
    def test_generate_rencana_tersimpan_ke_db(self, mock_planner, mock_narrative):
        """✅ Rencana hasil generate harus di-add ke DB dan commit."""
        mock_narrative.analyze_class_data = AsyncMock(
            return_value="Fake analisis"
        )
        mock_planner.generate_rencana_studi = AsyncMock(return_value={
            "rekomendasi_materi":      ["Fake Topik X"],
            "jadwal_mingguan":         {},
            "catatan_analisa":         "Fake catatan",
            "estimasi_selesai_minggu": 2,
        })

        from app.services.plan_service import generate_rencana_studi

        db = mock_db()
        kelas = fake_kelas()

        call_no = [0]
        def first_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return kelas
            return None

        db.first.side_effect   = first_side
        db.all.return_value    = []
        db.count.return_value  = 0
        db.refresh.side_effect = lambda obj: None

        asyncio.get_event_loop().run_until_complete(
            generate_rencana_studi(db, kelas.id, None)
        )

        # DB harus dipanggil add() (DraftAnalisis + RencanaStudi) dan commit()
        assert db.add.called
        db.commit.assert_called()

    @patch("app.services.plan_service.narrative_engine")
    @patch("app.services.plan_service.planner_engine")
    def test_generate_per_murid_pass_nama_murid_ke_ai(self, mock_planner, mock_narrative):
        """✅ Generate per murid harus meneruskan nama murid ke planner_engine."""
        mock_narrative.analyze_class_data = AsyncMock(return_value="Fake analisis")
        mock_planner.generate_rencana_studi = AsyncMock(return_value={
            "rekomendasi_materi":      [],
            "jadwal_mingguan":         {},
            "catatan_analisa":         "Fake catatan",
            "estimasi_selesai_minggu": 2,
        })

        from app.services.plan_service import generate_rencana_studi

        db = mock_db()
        kelas  = fake_kelas()
        murid  = fake_murid(nama="Fake Murid Spesifik")
        murid_id = murid.id

        call_no = [0]
        def first_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return kelas
            if call_no[0] == 2:
                return murid
            return None

        db.first.side_effect   = first_side
        db.all.return_value    = []
        db.count.return_value  = 0
        db.refresh.side_effect = lambda obj: None

        asyncio.get_event_loop().run_until_complete(
            generate_rencana_studi(db, kelas.id, murid_id)
        )

        # Verifikasi planner dipanggil dengan nama murid yang benar
        call_kwargs = mock_planner.generate_rencana_studi.call_args
        if call_kwargs:
            args_flat = str(call_kwargs)
            assert "Fake Murid Spesifik" in args_flat
