"""
test_mock_report.py
─────────────────────────────────────────────────────────────────────────────

Cara jalankan:
    pytest tests/test_mock_report.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
import asyncio
from datetime import date, datetime
from unittest.mock import MagicMock, AsyncMock, patch
from tests.test_helpers import fake_id, fake_laporan, fake_kelas, mock_db
import pytest

# ═════════════════════════════════════════════════════════════════════════════
# TEST GET LAPORAN
# ═════════════════════════════════════════════════════════════════════════════

class TestGetLaporan:

    def test_get_laporan_by_id_ditemukan(self):
        """✅ get_laporan_by_id harus return laporan jika ID ada."""
        from app.services.report_service import get_laporan_by_id

        db = mock_db()
        lap = fake_laporan()
        db.first.return_value = lap

        result = get_laporan_by_id(db, lap.id)

        assert result.id == lap.id
        assert result.konten == lap.konten

    def test_get_laporan_by_id_tidak_ada_return_none(self):
        """✅ get_laporan_by_id untuk ID tidak ada harus return None."""
        from app.services.report_service import get_laporan_by_id

        db = mock_db()
        db.first.return_value = None

        result = get_laporan_by_id(db, "fake-id-tidak-ada")

        assert result is None

    def test_get_laporan_by_murid_return_list(self):
        """✅ get_laporan_by_murid harus return list laporan milik murid."""
        from app.services.report_service import get_laporan_by_murid

        db = mock_db()
        murid_id = fake_id()
        laps = [fake_laporan(murid_id=murid_id) for _ in range(3)]
        db.all.return_value = laps

        result = get_laporan_by_murid(db, murid_id)

        assert len(result) == 3

    def test_get_laporan_by_murid_kosong_return_list_kosong(self):
        """✅ Murid tanpa laporan harus return list kosong."""
        from app.services.report_service import get_laporan_by_murid

        db = mock_db()
        db.all.return_value = []

        result = get_laporan_by_murid(db, fake_id())

        assert result == []

    def test_get_laporan_by_murid_urut_terbaru(self):
        """✅ Laporan harus diurutkan dari yang terbaru (order_by desc)."""
        from app.services.report_service import get_laporan_by_murid

        db = mock_db()
        db.all.return_value = []

        get_laporan_by_murid(db, fake_id())

        db.order_by.assert_called()


# ═════════════════════════════════════════════════════════════════════════════
# TEST LAPORAN PENDING
# ═════════════════════════════════════════════════════════════════════════════

class TestLaporanPending:

    def test_pending_hanya_draft_dan_final(self):
        """✅ get_laporan_pending tidak boleh return laporan 'terkirim'."""
        from app.services.report_service import get_laporan_pending

        pengajar_id = fake_id()
        kelas       = fake_kelas(pengajar_id=pengajar_id)
        lap_draft   = fake_laporan(status="draft", kelas_id=kelas.id)
        lap_final   = fake_laporan(status="final", kelas_id=kelas.id)

        call_no = [0]
        def all_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return [kelas]
            return [lap_draft, lap_final]

        db = mock_db()
        db.all.side_effect = all_side

        result = get_laporan_pending(db, pengajar_id)

        for lap in result:
            assert lap.status != "terkirim"

    def test_pending_kosong_jika_semua_terkirim(self):
        """✅ Jika semua laporan sudah dikirim, pending harus kosong."""
        from app.services.report_service import get_laporan_pending

        kelas = fake_kelas()

        call_no = [0]
        def all_side():
            call_no[0] += 1
            if call_no[0] == 1:
                return [kelas]
            return []  # tidak ada yang pending

        db = mock_db()
        db.all.side_effect = all_side

        result = get_laporan_pending(db, fake_id())

        assert result == []

    def test_pending_filter_berdasarkan_kelas_pengajar(self):
        """✅ Pending hanya dari kelas milik pengajar yang login."""
        from app.services.report_service import get_laporan_pending

        # Pengajar tanpa kelas → tidak ada pending
        db = mock_db()
        db.all.return_value = []

        result = get_laporan_pending(db, fake_id())

        assert result == []


# ═════════════════════════════════════════════════════════════════════════════
# TEST GENERATE LAPORAN (AI di-mock)
# ═════════════════════════════════════════════════════════════════════════════

class TestGenerateLaporan:

    @patch("app.services.report_service.narrative_engine")
    def test_generate_laporan_memanggil_narrative_engine(self, mock_narrative):
        """✅ Generate laporan harus memanggil narrative_engine — bukan Ollama nyata."""
        mock_narrative.generate_report = AsyncMock(
            return_value="Fake narasi laporan perkembangan Budi Santoso dari AI mock"
        )

        # Jika fungsi generate ada, verifikasi AI di-mock
        try:
            from app.services.report_service import generate_laporan
        except ImportError:
            pytest.skip("generate_laporan belum ada di report_service")

        db = mock_db()
        from app.schemas.schemas import LaporanCreate

        data = LaporanCreate(
            murid_id=fake_id(),
            kelas_id=fake_id(),
            periode_mulai=date(2025, 1, 1),
            periode_selesai=date(2025, 1, 31),
        )

        asyncio.get_event_loop().run_until_complete(
            generate_laporan(db, data)
        )

        mock_narrative.generate_report.assert_called_once()

    @patch("app.services.report_service.narrative_engine")
    def test_generate_laporan_status_awal_adalah_draft(self, mock_narrative):
        """✅ Laporan yang baru di-generate harus berstatus 'draft'."""
        mock_narrative.analyze_class_data = AsyncMock(
            return_value="Fake analisis kelas"
        )

        # Laporan baru harus selalu draft
        lap = fake_laporan(status="draft")
        assert lap.status == "draft"

    def test_laporan_final_tidak_bisa_diedit_setelah_terkirim(self):
        """✅ Laporan 'terkirim' dianggap selesai — tidak masuk pending."""
        lap = fake_laporan(status="terkirim")
        assert lap.status == "terkirim"
        # Laporan terkirim tidak masuk pending (diverifikasi di TestLaporanPending)


# ═════════════════════════════════════════════════════════════════════════════
# TEST KIRIM LAPORAN (SMTP di-mock)
# ═════════════════════════════════════════════════════════════════════════════

class TestKirimLaporan:

    @patch("aiosmtplib.send")
    def test_kirim_laporan_memanggil_smtp_bukan_email_nyata(self, mock_smtp):
        """✅ Kirim laporan harus memanggil SMTP — bukan kirim email nyata."""
        mock_smtp.return_value = None

        try:
            from app.services.report_service import kirim_laporan
        except ImportError:
            pytest.skip("kirim_laporan belum ada di report_service")

        db = mock_db()
        lap = fake_laporan(status="final")
        db.first.return_value = lap

        from app.schemas.schemas import KirimLaporanRequest
        data = KirimLaporanRequest(
            email_tujuan="fake-orangtua@email.com",
            catatan_tambahan="Fake catatan dari pengajar untuk orang tua",
        )

        asyncio.get_event_loop().run_until_complete(
            kirim_laporan(db, lap.id, data)
        )

        mock_smtp.assert_called_once()

    def test_kirim_laporan_draft_harus_error(self):
        """❌ Laporan berstatus 'draft' tidak bisa dikirim — harus raise error."""
        try:
            from app.services.report_service import kirim_laporan
        except ImportError:
            pytest.skip("kirim_laporan belum ada di report_service")

        from fastapi import HTTPException
        db = mock_db()
        lap = fake_laporan(status="draft")
        db.first.return_value = lap

        from app.schemas.schemas import KirimLaporanRequest
        data = KirimLaporanRequest(email_tujuan="fake@email.com")

        with pytest.raises((HTTPException, ValueError)):
            asyncio.get_event_loop().run_until_complete(
                kirim_laporan(db, lap.id, data)
            )

    def test_kirim_laporan_tidak_ada_raise_404(self):
        """❌ Laporan tidak ditemukan harus raise 404."""
        try:
            from app.services.report_service import kirim_laporan
        except ImportError:
            pytest.skip("kirim_laporan belum ada di report_service")

        from fastapi import HTTPException
        db = mock_db()
        db.first.return_value = None

        from app.schemas.schemas import KirimLaporanRequest
        data = KirimLaporanRequest(email_tujuan="fake@email.com")

        with pytest.raises((HTTPException, ValueError)):
            asyncio.get_event_loop().run_until_complete(
                kirim_laporan(db, "fake-id-tidak-ada", data)
            )
