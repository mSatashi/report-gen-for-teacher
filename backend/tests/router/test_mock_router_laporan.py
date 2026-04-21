import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
import asyncio
from datetime import date, datetime
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import (
    fake_id, fake_pengguna, fake_murid, fake_laporan, mock_db,
)
from app.schemas.schemas import LaporanResponse
 
 
def _make_laporan_response(status="draft", **kwargs) -> LaporanResponse:
    defaults = dict(
        id=fake_id(),
        murid_id=fake_id(),
        kelas_id=fake_id(),
        konten="Fake konten laporan perkembangan siswa.",
        tipe_laporan="perkembangan",
        status=status,
        pdf_path=None,
        tanggal=datetime(2025, 1, 15),
        tanggal_dikirim=None,
        is_ai_generated=True,
        periode_mulai=date(2025, 1, 1),
        periode_selesai=date(2025, 1, 31),
    )
    defaults.update(kwargs)
    return LaporanResponse(**defaults)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestLaporanPending — GET /laporan/pending
# ─────────────────────────────────────────────────────────────────────────────
 
class TestLaporanPending:
 
    def test_laporan_pending_memanggil_service_dengan_pengajar_id(self):
        """✅ laporan_pending harus memanggil get_laporan_pending dengan db dan current_user.id."""
        from app.routers.laporan import laporan_pending
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.laporan.get_laporan_pending", return_value=[]) as mock_svc:
            laporan_pending(current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, current_user.id)
 
    def test_laporan_pending_return_list_laporan(self):
        """✅ Harus mengembalikan list laporan dari service."""
        from app.routers.laporan import laporan_pending
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap1 = _make_laporan_response(status="draft")
        lap2 = _make_laporan_response(status="final")
 
        with patch("app.routers.laporan.get_laporan_pending", return_value=[lap1, lap2]):
            result = laporan_pending(current_user=current_user, db=db)
 
        assert len(result) == 2
 
    def test_laporan_pending_kosong_return_list_kosong(self):
        """✅ Tidak ada laporan pending → return list kosong."""
        from app.routers.laporan import laporan_pending
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.laporan.get_laporan_pending", return_value=[]):
            result = laporan_pending(current_user=current_user, db=db)
 
        assert result == []
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestLaporanMurid — GET /laporan/murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestLaporanMurid:
 
    def test_laporan_murid_memanggil_service(self):
        """✅ laporan_murid harus meneruskan murid_id, skip, limit ke get_laporan_by_murid."""
        from app.routers.laporan import laporan_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
 
        with patch("app.routers.laporan.get_laporan_by_murid", return_value=[]) as mock_svc:
            laporan_murid(murid_id=murid_id, skip=0, limit=20, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, murid_id, 0, 20)
 
    def test_laporan_murid_return_list(self):
        """✅ Harus mengembalikan laporan sesuai murid yang diminta."""
        from app.routers.laporan import laporan_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        lap = _make_laporan_response(murid_id=murid_id)
 
        with patch("app.routers.laporan.get_laporan_by_murid", return_value=[lap]):
            result = laporan_murid(murid_id=murid_id, skip=0, limit=20, current_user=current_user, db=db)
 
        assert len(result) == 1
        assert result[0].murid_id == murid_id
 
    def test_laporan_murid_paginasi_diteruskan(self):
        """✅ Parameter skip dan limit harus diteruskan ke service."""
        from app.routers.laporan import laporan_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.laporan.get_laporan_by_murid", return_value=[]) as mock_svc:
            laporan_murid(murid_id=fake_id(), skip=10, limit=5, current_user=current_user, db=db)
 
        args = mock_svc.call_args[0]
        assert args[2] == 10  # skip
        assert args[3] == 5   # limit
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestGetLaporan — GET /laporan/{laporan_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestGetLaporan:
 
    def test_get_laporan_ditemukan_return_laporan(self):
        """✅ get_laporan harus mengembalikan laporan dari service."""
        from app.routers.laporan import get_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap = _make_laporan_response(status="final")
 
        with patch("app.routers.laporan.get_laporan_by_id", return_value=lap):
            result = get_laporan(laporan_id="fake-laporan-id-001", current_user=current_user, db=db)
 
        assert result.status == "final"
 
    def test_get_laporan_tidak_ditemukan_raise_404(self):
        """❌ Laporan tidak ada → raise 404."""
        from app.routers.laporan import get_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.laporan.get_laporan_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                get_laporan(laporan_id="fake-laporan-id-tidak-ada", current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
        assert "laporan" in exc.value.detail.lower()
 
    def test_get_laporan_tidak_commit(self):
        """✅ get_laporan adalah read-only."""
        from app.routers.laporan import get_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap = _make_laporan_response()
 
        with patch("app.routers.laporan.get_laporan_by_id", return_value=lap):
            get_laporan(laporan_id="fake-laporan-id-readonly", current_user=current_user, db=db)
 
        db.commit.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestDownloadPdf — GET /laporan/{laporan_id}/pdf
# ─────────────────────────────────────────────────────────────────────────────
 
class TestDownloadPdf:
 
    def test_download_pdf_laporan_tidak_ada_raise_404(self):
        """❌ Laporan tidak ada → raise 404 sebelum generate PDF."""
        from app.routers.laporan import download_pdf
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.laporan.get_laporan_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                download_pdf(laporan_id="fake-laporan-id-pdf-tidak-ada", current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
 
    def test_download_pdf_generate_gagal_raise_500(self):
        """❌ generate_pdf gagal (return None) → raise 500."""
        from app.routers.laporan import download_pdf
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_obj = fake_laporan(status="final")
        lap_obj.pdf_path = None  # belum ada PDF
 
        with patch("app.routers.laporan.get_laporan_by_id", return_value=lap_obj), \
             patch("app.routers.laporan.generate_pdf", return_value=None):
            with pytest.raises(HTTPException) as exc:
                download_pdf(laporan_id="fake-laporan-id-500", current_user=current_user, db=db)
 
        assert exc.value.status_code == 500
 
    def test_download_pdf_pdf_sudah_ada_tidak_regenerate(self):
        """✅ Jika pdf_path sudah ada dan file exist, tidak perlu regenerate."""
        from app.routers.laporan import download_pdf
        from fastapi.responses import FileResponse
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_obj = fake_laporan(status="final")
        lap_obj.pdf_path = "/fake/path/laporan.pdf"
 
        with patch("app.routers.laporan.get_laporan_by_id", return_value=lap_obj), \
             patch("app.routers.laporan.generate_pdf") as mock_gen, \
             patch("os.path.exists", return_value=True), \
             patch("fastapi.responses.FileResponse.__init__", return_value=None):
            try:
                download_pdf(laporan_id="fake-laporan-id-pdf-ada", current_user=current_user, db=db)
            except Exception:
                pass  # FileResponse mock mungkin error
 
        mock_gen.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestBuatLaporan — POST /laporan/generate
# ─────────────────────────────────────────────────────────────────────────────
 
class TestBuatLaporan:
 
    def _make_data(self, **overrides):
        from app.schemas.schemas import LaporanCreate
        defaults = dict(
            murid_id=fake_id(),
            kelas_id=fake_id(),
            periode_mulai=date(2025, 1, 1),
            periode_selesai=date(2025, 1, 31),
            tipe_laporan="perkembangan",
        )
        defaults.update(overrides)
        return LaporanCreate(**defaults)
 
    def test_buat_laporan_berhasil_return_laporan(self):
        """✅ buat_laporan berhasil harus mengembalikan LaporanResponse."""
        from app.routers.laporan import buat_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_resp = _make_laporan_response(status="draft")
        data = self._make_data()
 
        async def run():
            with patch("app.routers.laporan.generate_laporan", new=AsyncMock(return_value=lap_resp)):
                return await buat_laporan(data=data, current_user=current_user, db=db)
 
        result = asyncio.get_event_loop().run_until_complete(run())
 
        assert result.status == "draft"
 
    def test_buat_laporan_value_error_raise_404(self):
        """❌ ValueError dari generate_laporan (murid tidak ada) → raise 404."""
        from app.routers.laporan import buat_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        data = self._make_data()
 
        async def run():
            with patch("app.routers.laporan.generate_laporan",
                       new=AsyncMock(side_effect=ValueError("Murid tidak ditemukan"))):
                return await buat_laporan(data=data, current_user=current_user, db=db)
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 404
 
    def test_buat_laporan_exception_raise_500(self):
        """❌ Exception umum dari generate_laporan → raise 500."""
        from app.routers.laporan import buat_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        data = self._make_data()
 
        async def run():
            with patch("app.routers.laporan.generate_laporan",
                       new=AsyncMock(side_effect=Exception("Fake AI error"))):
                return await buat_laporan(data=data, current_user=current_user, db=db)
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 500
 
    def test_buat_laporan_memanggil_generate_dengan_data(self):
        """✅ Router harus meneruskan db dan data ke generate_laporan."""
        from app.routers.laporan import buat_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_resp = _make_laporan_response()
        data = self._make_data()
 
        async def run():
            with patch("app.routers.laporan.generate_laporan", new=AsyncMock(return_value=lap_resp)) as mock_svc:
                await buat_laporan(data=data, current_user=current_user, db=db)
                mock_svc.assert_called_once_with(db, data)
 
        asyncio.get_event_loop().run_until_complete(run())
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestEditLaporan — PUT /laporan/{laporan_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestEditLaporan:
 
    def _make_update_data(self):
        from app.schemas.schemas import LaporanUpdate
        return LaporanUpdate(konten="Fake konten laporan diperbarui oleh guru.", status="final")
 
    def test_edit_laporan_berhasil_return_laporan(self):
        """✅ edit_laporan berhasil harus mengembalikan laporan yang sudah diupdate."""
        from app.routers.laporan import edit_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_resp = _make_laporan_response(status="final")
        data = self._make_update_data()
 
        with patch("app.routers.laporan.update_laporan", return_value=lap_resp):
            result = edit_laporan(laporan_id="fake-laporan-id-edit", data=data, current_user=current_user, db=db)
 
        assert result.status == "final"
 
    def test_edit_laporan_tidak_ditemukan_raise_404(self):
        """❌ Laporan tidak ada → raise 404."""
        from app.routers.laporan import edit_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        data = self._make_update_data()
 
        with patch("app.routers.laporan.update_laporan", return_value=None):
            with pytest.raises(HTTPException) as exc:
                edit_laporan(laporan_id="fake-laporan-id-edit-404", data=data, current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
 
    def test_edit_laporan_memanggil_service_dengan_benar(self):
        """✅ Router harus meneruskan db, laporan_id, dan data ke update_laporan."""
        from app.routers.laporan import edit_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_resp = _make_laporan_response()
        data = self._make_update_data()
 
        with patch("app.routers.laporan.update_laporan", return_value=lap_resp) as mock_svc:
            edit_laporan(laporan_id="fake-laporan-id-call", data=data, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, "fake-laporan-id-call", data)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestFinalisasi — PUT /laporan/{laporan_id}/finalisasi
# ─────────────────────────────────────────────────────────────────────────────
 
class TestFinalisasi:
 
    def test_finalisasi_berhasil_return_laporan_final(self):
        """✅ finalisasi berhasil → return laporan dengan status 'final'."""
        from app.routers.laporan import finalisasi
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_resp = _make_laporan_response(status="final")
 
        with patch("app.routers.laporan.finalize_laporan", return_value=lap_resp):
            result = finalisasi(laporan_id="fake-laporan-id-final", current_user=current_user, db=db)
 
        assert result.status == "final"
 
    def test_finalisasi_tidak_ditemukan_raise_404(self):
        """❌ Laporan tidak ada → raise 404."""
        from app.routers.laporan import finalisasi
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.laporan.finalize_laporan", return_value=None):
            with pytest.raises(HTTPException) as exc:
                finalisasi(laporan_id="fake-laporan-id-final-404", current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
 
    def test_finalisasi_memanggil_finalize_service(self):
        """✅ Router harus memanggil finalize_laporan dengan db dan laporan_id."""
        from app.routers.laporan import finalisasi
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_resp = _make_laporan_response(status="final")
 
        with patch("app.routers.laporan.finalize_laporan", return_value=lap_resp) as mock_svc:
            finalisasi(laporan_id="fake-laporan-id-finalize-call", current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, "fake-laporan-id-finalize-call")
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestKirimLaporan — POST /laporan/{laporan_id}/kirim
# ─────────────────────────────────────────────────────────────────────────────
 
class TestKirimLaporan:
 
    def _make_kirim_data(self, email="fake-ortu@email.com", catatan=None):
        from app.schemas.schemas import KirimLaporanRequest
        return KirimLaporanRequest(
            email_tujuan=email,
            catatan_tambahan=catatan,
        )
 
    def test_kirim_laporan_tidak_ada_raise_404(self):
        """❌ Laporan tidak ada → raise 404 sebelum kirim."""
        from app.routers.laporan import kirim_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        req = self._make_kirim_data()
        bg = MagicMock()
 
        async def run():
            with patch("app.routers.laporan.get_laporan_by_id", return_value=None):
                return await kirim_laporan(
                    laporan_id="fake-laporan-id-kirim-404",
                    req=req,
                    background_tasks=bg,
                    current_user=current_user,
                    db=db,
                )
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 404
 
    def test_kirim_laporan_status_draft_raise_400(self):
        """❌ Laporan masih draft → raise 400 (harus difinalisasi dulu)."""
        from app.routers.laporan import kirim_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        lap_obj = fake_laporan(status="draft")
        req = self._make_kirim_data()
        bg = MagicMock()
 
        async def run():
            with patch("app.routers.laporan.get_laporan_by_id", return_value=lap_obj):
                return await kirim_laporan(
                    laporan_id="fake-laporan-id-draft",
                    req=req,
                    background_tasks=bg,
                    current_user=current_user,
                    db=db,
                )
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 400
        assert "finalisasi" in exc.value.detail.lower()
 
    def test_kirim_laporan_final_berhasil_return_message(self):
        """✅ Laporan final → kirim berhasil dan return dict dengan message."""
        from app.routers.laporan import kirim_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        lap_obj = fake_laporan(murid_id=murid_id, status="final")
        murid_obj = fake_murid(nama="Fake Nama Murid Kirim")
        murid_obj.id = murid_id
        db.first.return_value = murid_obj
 
        req = self._make_kirim_data(email="fake-ortu-target@email.com")
        bg = MagicMock()
 
        async def run():
            with patch("app.routers.laporan.get_laporan_by_id", return_value=lap_obj), \
                 patch("app.routers.laporan.generate_pdf", return_value="/fake/path/pdf.pdf"), \
                 patch("app.routers.laporan.kirim_laporan_email"):
                return await kirim_laporan(
                    laporan_id="fake-laporan-id-kirim-ok",
                    req=req,
                    background_tasks=bg,
                    current_user=current_user,
                    db=db,
                )
 
        result = asyncio.get_event_loop().run_until_complete(run())
 
        assert "message" in result
        assert "fake-ortu-target@email.com" in result["message"]
        assert "laporan_id" in result
 
    def test_kirim_laporan_email_di_background_task(self):
        """✅ Pengiriman email harus dilakukan di background_tasks (tidak blocking)."""
        from app.routers.laporan import kirim_laporan
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        lap_obj = fake_laporan(murid_id=murid_id, status="final")
        murid_obj = fake_murid()
        murid_obj.id = murid_id
        db.first.return_value = murid_obj
 
        req = self._make_kirim_data()
        bg = MagicMock()
 
        async def run():
            with patch("app.routers.laporan.get_laporan_by_id", return_value=lap_obj), \
                 patch("app.routers.laporan.generate_pdf", return_value="/fake/path/bg.pdf"), \
                 patch("app.routers.laporan.kirim_laporan_email"):
                await kirim_laporan(
                    laporan_id="fake-laporan-id-bg",
                    req=req,
                    background_tasks=bg,
                    current_user=current_user,
                    db=db,
                )
 
        asyncio.get_event_loop().run_until_complete(run())
 
        # background_tasks.add_task harus dipanggil
        bg.add_task.assert_called_once()