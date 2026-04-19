import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import fake_id, fake_pengguna, mock_db
from app.schemas.schemas import DashboardSummary
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestRouterDashboard — GET /dashboard/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestRouterDashboard:
 
    def _make_summary(
        self,
        total_siswa: int = 0,
        log_hari_ini: int = 0,
        plan_aktif: int = 0,
        report_pending: int = 0,
    ) -> DashboardSummary:
        return DashboardSummary(
            total_siswa=total_siswa,
            log_hari_ini=log_hari_ini,
            plan_aktif=plan_aktif,
            report_pending=report_pending,
            aktivitas_terbaru=[],
            progress_siswa=[],
        )
 
    def test_dashboard_memanggil_service_dengan_user_id(self):
        """✅ Endpoint harus memanggil get_dashboard_data dengan db dan current_user.id."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        summary = self._make_summary()
 
        with patch("app.routers.dashboard.get_dashboard_data", return_value=summary) as mock_svc:
            result = dashboard(current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, current_user.id)
 
    def test_dashboard_return_summary_dari_service(self):
        """✅ Router harus meneruskan return value dari get_dashboard_data."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        summary = self._make_summary(total_siswa=5, log_hari_ini=3, plan_aktif=2, report_pending=1)
 
        with patch("app.routers.dashboard.get_dashboard_data", return_value=summary):
            result = dashboard(current_user=current_user, db=db)
 
        assert result.total_siswa    == 5
        assert result.log_hari_ini   == 3
        assert result.plan_aktif     == 2
        assert result.report_pending == 1
 
    def test_dashboard_kosong_return_semua_nol(self):
        """✅ Pengajar baru tanpa data → semua counter 0, list kosong."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        summary = self._make_summary()
 
        with patch("app.routers.dashboard.get_dashboard_data", return_value=summary):
            result = dashboard(current_user=current_user, db=db)
 
        assert result.total_siswa    == 0
        assert result.log_hari_ini   == 0
        assert result.plan_aktif     == 0
        assert result.report_pending == 0
        assert result.aktivitas_terbaru == []
        assert result.progress_siswa    == []
 
    def test_dashboard_aktivitas_terbaru_bisa_berisi_data(self):
        """✅ aktivitas_terbaru bisa berisi list dict jika ada aktivitas."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        fake_aktivitas = [
            {"tanggal": "2025-03-10", "topik": "Fake Topik", "kelas_id": fake_id(), "nilai": 85.0},
        ]
        summary = DashboardSummary(
            total_siswa=1,
            log_hari_ini=1,
            plan_aktif=0,
            report_pending=0,
            aktivitas_terbaru=fake_aktivitas,
            progress_siswa=[],
        )
 
        with patch("app.routers.dashboard.get_dashboard_data", return_value=summary):
            result = dashboard(current_user=current_user, db=db)
 
        assert len(result.aktivitas_terbaru) == 1
        assert result.aktivitas_terbaru[0]["topik"] == "Fake Topik"
 
    def test_dashboard_progress_siswa_bisa_berisi_data(self):
        """✅ progress_siswa bisa berisi list dict jika ada data progres."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        fake_progress = [
            {"murid_id": fake_id(), "nama": "Fake Andi", "avg_nilai": 78.0, "total_sesi": 5, "status": "On Track"},
        ]
        summary = DashboardSummary(
            total_siswa=1,
            log_hari_ini=0,
            plan_aktif=0,
            report_pending=0,
            aktivitas_terbaru=[],
            progress_siswa=fake_progress,
        )
 
        with patch("app.routers.dashboard.get_dashboard_data", return_value=summary):
            result = dashboard(current_user=current_user, db=db)
 
        assert len(result.progress_siswa) == 1
        item = result.progress_siswa[0]
        assert item["nama"]   == "Fake Andi"
        assert item["status"] == "On Track"
 
    def test_dashboard_service_error_propagate(self):
        """❌ Jika service melempar exception, router harus meneruskannya."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.dashboard.get_dashboard_data",
                   side_effect=Exception("Fake DB error")):
            with pytest.raises(Exception):
                dashboard(current_user=current_user, db=db)
 
    def test_dashboard_hanya_pakai_id_dari_current_user(self):
        """✅ Router meneruskan current_user.id (bukan objek penuh) ke service."""
        from app.routers.dashboard import dashboard
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        summary = self._make_summary()
 
        captured = []
 
        def capture_call(db_arg, pengajar_id):
            captured.append(pengajar_id)
            return summary
 
        with patch("app.routers.dashboard.get_dashboard_data", side_effect=capture_call):
            dashboard(current_user=current_user, db=db)
 
        assert captured[0] == current_user.id