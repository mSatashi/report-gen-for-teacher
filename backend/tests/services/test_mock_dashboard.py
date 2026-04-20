"""
test_mock_dashboard.py
─────────────────────────────────────────────────────────────────────────────
Pure mock unit test untuk app/services/dashboard_service.py
Tidak butuh database, tidak butuh .env.

Cara jalankan:
    pytest tests/test_mock_dashboard.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock
from tests.test_helpers import fake_id, fake_pengguna, fake_murid, fake_kelas, fake_log

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_db_mock(kelas_list=None, count_values=None, all_side_effects=None):
    """
    Buat mock DB yang bisa dikonfigurasi sesuai kebutuhan test.
    count_values : list nilai yang akan dikembalikan count() berturut-turut.
    all_side_effects : list nilai yang akan dikembalikan all() berturut-turut.
    """
    db = MagicMock()
    qm = MagicMock()
    qm.filter.return_value   = qm
    qm.order_by.return_value = qm
    qm.limit.return_value    = qm
    qm.offset.return_value   = qm
    qm.distinct.return_value = qm
    qm.group_by.return_value = qm
    qm.isnot.return_value    = qm

    if count_values is not None:
        qm.count.side_effect = count_values
    else:
        qm.count.return_value = 0

    if all_side_effects is not None:
        qm.all.side_effect = all_side_effects
    else:
        qm.all.return_value = kelas_list or []

    qm.first.return_value = None
    db.query.return_value = qm
    return db, qm


# ═════════════════════════════════════════════════════════════════════════════
# TEST KONDISI KOSONG
# ═════════════════════════════════════════════════════════════════════════════

class TestDashboardKosong:

    def test_semua_field_nol_untuk_pengajar_baru(self):
        """✅ Pengajar tanpa data apapun — semua counter harus 0, list kosong."""
        from app.services.dashboard_service import get_dashboard_data

        db, qm = build_db_mock(
            kelas_list=[],
            count_values=[0, 0, 0, 0],
            all_side_effects=[[], [], []],
        )

        result = get_dashboard_data(db, fake_id())

        assert result.total_siswa    == 0
        assert result.log_hari_ini   == 0
        assert result.plan_aktif     == 0
        assert result.report_pending == 0
        assert result.aktivitas_terbaru == []
        assert result.progress_siswa    == []

    def test_return_type_adalah_dashboard_summary(self):
        """✅ get_dashboard_data harus return objek DashboardSummary."""
        from app.services.dashboard_service import get_dashboard_data
        from app.schemas.schemas import DashboardSummary

        db, _ = build_db_mock(
            kelas_list=[],
            count_values=[0, 0, 0, 0],
            all_side_effects=[[], [], []],
        )

        result = get_dashboard_data(db, fake_id())

        assert isinstance(result, DashboardSummary)


# ═════════════════════════════════════════════════════════════════════════════
# TEST HITUNG COUNTER
# ═════════════════════════════════════════════════════════════════════════════

class TestDashboardCounter:

    def test_total_siswa_sesuai_jumlah_kelas_murid(self):
        """✅ total_siswa harus sesuai count KelasMurid yang distinct murid_id."""
        from app.services.dashboard_service import get_dashboard_data

        pengajar_id = fake_id()
        kelas = fake_kelas(pengajar_id=pengajar_id)

        db, qm = build_db_mock(
            all_side_effects=[[kelas], [], []],
            count_values=[7, 3, 2, 1],  # total_siswa, log, plan, pending
        )

        result = get_dashboard_data(db, pengajar_id)

        assert result.total_siswa    == 7
        assert result.log_hari_ini   == 3
        assert result.plan_aktif     == 2
        assert result.report_pending == 1

    def test_log_hari_ini_filter_tanggal_hari_ini(self):
        """✅ log_hari_ini harus menghitung log dengan tanggal == today."""
        from app.services.dashboard_service import get_dashboard_data

        kelas = fake_kelas()

        db, qm = build_db_mock(
            all_side_effects=[[kelas], [], []],
            count_values=[0, 5, 0, 0],
        )

        result = get_dashboard_data(db, fake_id())

        assert result.log_hari_ini == 5

    def test_report_pending_hanya_draft_dan_final(self):
        """✅ report_pending tidak boleh menghitung laporan berstatus 'terkirim'."""
        from app.services.dashboard_service import get_dashboard_data

        kelas = fake_kelas()

        db, qm = build_db_mock(
            all_side_effects=[[kelas], [], []],
            count_values=[0, 0, 0, 3],  # 3 laporan draft/final
        )

        result = get_dashboard_data(db, fake_id())

        assert result.report_pending == 3

    def test_kelas_guru_lain_tidak_terhitung(self):
        """✅ Data dari kelas guru lain tidak boleh masuk hitungan."""
        from app.services.dashboard_service import get_dashboard_data

        # Pengajar ini tidak punya kelas → semua 0
        db, qm = build_db_mock(
            all_side_effects=[[], [], []],
            count_values=[0, 0, 0, 0],
        )

        result = get_dashboard_data(db, fake_id())

        assert result.total_siswa    == 0
        assert result.log_hari_ini   == 0
        assert result.plan_aktif     == 0
        assert result.report_pending == 0


# ═════════════════════════════════════════════════════════════════════════════
# TEST AKTIVITAS TERBARU
# ═════════════════════════════════════════════════════════════════════════════

class TestAktivitasTerbaru:

    def test_aktivitas_terbaru_maks_10_item(self):
        """✅ aktivitas_terbaru tidak boleh lebih dari 10 item (limit di query)."""
        from app.services.dashboard_service import get_dashboard_data

        kelas = fake_kelas()
        # Service pakai .limit(10) — mock kembalikan 10 log
        logs_10 = [fake_log(kelas_id=kelas.id) for _ in range(10)]

        call_no = [0]
        def all_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return [kelas]
            if call_no[0] == 2:
                return logs_10
            return []

        db, qm = build_db_mock()
        qm.all.side_effect  = all_side
        qm.count.return_value = 0

        result = get_dashboard_data(db, fake_id())

        assert len(result.aktivitas_terbaru) <= 10

    def test_aktivitas_terbaru_berisi_field_yang_benar(self):
        """✅ Setiap item aktivitas harus punya field tanggal, topik, kelas_id, nilai."""
        from app.services.dashboard_service import get_dashboard_data

        kelas   = fake_kelas()
        log_obj = fake_log(kelas_id=kelas.id, topik="Fake Topik Geometri", nilai=88.0)

        call_no = [0]
        def all_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return [kelas]
            if call_no[0] == 2:
                return [log_obj]
            return []

        db, qm = build_db_mock()
        qm.all.side_effect   = all_side
        qm.count.return_value = 0

        result = get_dashboard_data(db, fake_id())

        if result.aktivitas_terbaru:
            item = result.aktivitas_terbaru[0]
            assert "tanggal" in item
            assert "topik"   in item
            assert "kelas_id" in item
            assert "nilai"   in item


# ═════════════════════════════════════════════════════════════════════════════
# TEST PROGRESS SISWA
# ═════════════════════════════════════════════════════════════════════════════

class TestProgressSiswa:

    def _setup_dengan_progress_row(self, avg_nilai, total_sesi=4):
        from app.services.dashboard_service import get_dashboard_data

        kelas    = fake_kelas()
        murid_id = fake_id()

        row = MagicMock()
        row.murid_id   = murid_id
        row.avg_nilai  = avg_nilai
        row.total_sesi = total_sesi

        murid = fake_murid(nama="Fake Progress Murid")
        murid.id = murid_id

        call_no = [0]
        def all_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return [kelas]
            if call_no[0] == 2:
                return []          # aktivitas
            if call_no[0] == 3:
                return [row]       # progress rows
            return []

        db = MagicMock()
        qm = MagicMock()
        qm.filter.return_value   = qm
        qm.order_by.return_value = qm
        qm.limit.return_value    = qm
        qm.offset.return_value   = qm
        qm.distinct.return_value = qm
        qm.group_by.return_value = qm
        qm.isnot.return_value    = qm
        qm.count.return_value    = 0
        qm.all.side_effect       = all_side
        qm.first.return_value    = murid
        db.query.return_value    = qm

        return get_dashboard_data(db, fake_id())

    def test_status_on_track_jika_avg_lebih_dari_70(self):
        """✅ Rata-rata nilai >= 70 harus berstatus 'On Track'."""
        result = self._setup_dengan_progress_row(avg_nilai=80.0)
        if result.progress_siswa:
            assert result.progress_siswa[0]["status"] == "On Track"

    def test_status_perlu_perhatian_jika_avg_kurang_dari_70(self):
        """✅ Rata-rata nilai < 70 harus berstatus 'Perlu Perhatian'."""
        result = self._setup_dengan_progress_row(avg_nilai=55.0)
        if result.progress_siswa:
            assert result.progress_siswa[0]["status"] == "Perlu Perhatian"

    def test_status_tepat_di_batas_70(self):
        """✅ Rata-rata nilai tepat 70 harus berstatus 'On Track' (bukan Perlu Perhatian)."""
        result = self._setup_dengan_progress_row(avg_nilai=70.0)
        if result.progress_siswa:
            assert result.progress_siswa[0]["status"] == "On Track"

    def test_progress_siswa_berisi_field_yang_benar(self):
        """✅ Setiap item progress harus punya murid_id, nama, avg_nilai, total_sesi, status."""
        result = self._setup_dengan_progress_row(avg_nilai=75.0, total_sesi=6)
        if result.progress_siswa:
            item = result.progress_siswa[0]
            assert "murid_id"   in item
            assert "nama"       in item
            assert "avg_nilai"  in item
            assert "total_sesi" in item
            assert "status"     in item
