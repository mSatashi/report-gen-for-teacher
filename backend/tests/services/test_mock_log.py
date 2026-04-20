"""
test_mock_log.py
─────────────────────────────────────────────────────────────────────────────
Pure mock unit test untuk app/services/log_service.py
Tidak butuh database, tidak butuh file CSV nyata.

Cara jalankan:
    pytest tests/test_mock_log.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
import asyncio
from datetime import date, datetime
from unittest.mock import MagicMock, AsyncMock, patch
from tests.test_helpers import fake_id, fake_log, mock_db
import pytest

# ═════════════════════════════════════════════════════════════════════════════
# TEST CREATE LOG
# ═════════════════════════════════════════════════════════════════════════════

class TestCreateLog:

    def test_create_log_berhasil_add_dan_commit(self):
        """✅ create_log harus add objek ke DB dan commit."""
        from app.services.log_service import create_log
        from app.schemas.schemas import LogPertemuanCreate

        db = mock_db()
        mock_log_obj = fake_log(topik="Fake Persamaan Linear")

        data = LogPertemuanCreate(
            kelas_id=fake_id(),
            murid_id=fake_id(),
            tanggal=date(2025, 3, 10),
            topik="Fake Persamaan Linear",
            nilai=85.0,
            tingkat_pemahaman="paham",
            durasi_menit=90,
        )

        with patch("app.services.log_service.LogPertemuan", return_value=mock_log_obj):
            db.refresh.side_effect = lambda obj: None
            create_log(db, data)

        db.add.assert_called_once_with(mock_log_obj)
        db.commit.assert_called_once()

    def test_create_log_tanpa_murid_id_berhasil(self):
        """✅ Log untuk seluruh kelas (murid_id=None) harus berhasil."""
        from app.services.log_service import create_log
        from app.schemas.schemas import LogPertemuanCreate

        db = mock_db()
        data = LogPertemuanCreate(
            kelas_id=fake_id(),
            murid_id=None,  # untuk seluruh kelas
            tanggal=date(2025, 3, 10),
            topik="Fake Topik Kelas",
        )

        with patch("app.services.log_service.LogPertemuan") as MockLog:
            MockLog.return_value = fake_log(murid_id=None)
            db.refresh.side_effect = lambda obj: None
            create_log(db, data)

        db.commit.assert_called_once()


# ═════════════════════════════════════════════════════════════════════════════
# TEST GET LOG BY ID
# ═════════════════════════════════════════════════════════════════════════════

class TestGetLogById:

    def test_get_log_by_id_ditemukan(self):
        """✅ get_log_by_id harus return log jika ID ada."""
        from app.services.log_service import get_log_by_id

        db = mock_db()
        log = fake_log(topik="Fake Topik Geometri")
        db.first.return_value = log

        result = get_log_by_id(db, log.id)

        assert result.topik == "Fake Topik Geometri"

    def test_get_log_by_id_tidak_ada_return_none(self):
        """✅ get_log_by_id untuk ID tidak ada harus return None."""
        from app.services.log_service import get_log_by_id

        db = mock_db()
        db.first.return_value = None

        result = get_log_by_id(db, "fake-id-tidak-ada")

        assert result is None


# ═════════════════════════════════════════════════════════════════════════════
# TEST GET LOGS BY KELAS
# ═════════════════════════════════════════════════════════════════════════════

class TestGetLogsByKelas:

    def test_get_logs_by_kelas_return_semua(self):
        """✅ get_logs_by_kelas harus return semua log kelas."""
        from app.services.log_service import get_logs_by_kelas

        db = mock_db()
        kelas_id = fake_id()
        db.all.return_value = [fake_log(kelas_id=kelas_id) for _ in range(4)]

        result = get_logs_by_kelas(db, kelas_id)

        assert len(result) == 4

    def test_get_logs_by_kelas_filter_murid(self):
        """✅ Filter murid_id harus memanggil filter tambahan."""
        from app.services.log_service import get_logs_by_kelas

        db = mock_db()
        murid_id = fake_id()
        db.all.return_value = [fake_log(murid_id=murid_id)]

        get_logs_by_kelas(db, fake_id(), murid_id=murid_id)

        # filter harus dipanggil minimal 2x (kelas_id + murid_id)
        assert db.filter.call_count >= 2

    def test_get_logs_by_kelas_paginasi(self):
        """✅ skip dan limit harus diteruskan ke query."""
        from app.services.log_service import get_logs_by_kelas

        db = mock_db()
        db.all.return_value = []

        get_logs_by_kelas(db, fake_id(), skip=5, limit=10)

        db.offset.assert_called_with(5)
        db.limit.assert_called_with(10)

    def test_get_logs_kelas_kosong_return_list_kosong(self):
        """✅ Kelas tanpa log harus return list kosong."""
        from app.services.log_service import get_logs_by_kelas

        db = mock_db()
        db.all.return_value = []

        result = get_logs_by_kelas(db, fake_id())

        assert result == []


# ═════════════════════════════════════════════════════════════════════════════
# TEST UPDATE LOG
# ═════════════════════════════════════════════════════════════════════════════

class TestUpdateLog:

    def test_update_log_nilai_berhasil(self):
        """✅ Update nilai harus mengubah atribut dan commit."""
        from app.services.log_service import update_log
        from app.schemas.schemas import LogPertemuanUpdate

        db = mock_db()
        log = fake_log(nilai=70.0)
        db.first.return_value = log
        db.refresh.side_effect = lambda obj: None

        result = update_log(db, log.id, LogPertemuanUpdate(nilai=92.0))

        assert log.nilai == 92.0
        db.commit.assert_called_once()

    def test_update_log_catatan_berhasil(self):
        """✅ Update catatan harus mengubah atribut dan commit."""
        from app.services.log_service import update_log
        from app.schemas.schemas import LogPertemuanUpdate

        db = mock_db()
        log = fake_log()
        db.first.return_value  = log
        db.refresh.side_effect = lambda obj: None

        update_log(db, log.id, LogPertemuanUpdate(catatan="Fake catatan yang sudah diupdate"))

        assert log.catatan == "Fake catatan yang sudah diupdate"

    def test_update_log_partial_field_lain_tidak_berubah(self):
        """✅ Update satu field tidak mengubah field lain."""
        from app.services.log_service import update_log
        from app.schemas.schemas import LogPertemuanUpdate

        db = mock_db()
        log = fake_log(topik="Fake Topik Tetap", nilai=80.0)
        db.first.return_value  = log
        db.refresh.side_effect = lambda obj: None

        update_log(db, log.id, LogPertemuanUpdate(nilai=95.0))

        # topik tidak boleh berubah
        assert log.topik == "Fake Topik Tetap"
        assert log.nilai == 95.0

    def test_update_log_tidak_ada_return_none(self):
        """❌ Update log yang tidak ada harus return None tanpa commit."""
        from app.services.log_service import update_log
        from app.schemas.schemas import LogPertemuanUpdate

        db = mock_db()
        db.first.return_value = None

        result = update_log(db, "fake-id-tidak-ada", LogPertemuanUpdate(nilai=80.0))

        assert result is None
        db.commit.assert_not_called()


# ═════════════════════════════════════════════════════════════════════════════
# TEST DELETE LOG
# ═════════════════════════════════════════════════════════════════════════════

class TestDeleteLog:

    def test_delete_log_berhasil_return_true(self):
        """✅ delete_log harus hapus log dan return True."""
        from app.services.log_service import delete_log

        db = mock_db()
        log = fake_log()
        db.first.return_value = log

        result = delete_log(db, log.id)

        assert result is True
        db.delete.assert_called_once_with(log)
        db.commit.assert_called_once()

    def test_delete_log_tidak_ada_return_false(self):
        """❌ Log tidak ditemukan harus return False tanpa commit."""
        from app.services.log_service import delete_log

        db = mock_db()
        db.first.return_value = None

        result = delete_log(db, "fake-id-tidak-ada")

        assert result is False
        db.delete.assert_not_called()
        db.commit.assert_not_called()

    def test_delete_log_tidak_pengaruhi_log_lain(self):
        """✅ Hapus satu log hanya menghapus log tersebut, bukan semua log."""
        from app.services.log_service import delete_log

        db = mock_db()
        log_target = fake_log(topik="Fake Target")
        db.first.return_value = log_target

        delete_log(db, log_target.id)

        # delete hanya dipanggil sekali dengan log yang benar
        db.delete.assert_called_once_with(log_target)


# ═════════════════════════════════════════════════════════════════════════════
# TEST VALIDASI FILE BULK UPLOAD
# ═════════════════════════════════════════════════════════════════════════════

class TestValidasiFile:

    def test_ekstensi_csv_diterima(self):
        """✅ File .csv harus diterima."""
        from app.services.log_service import _validate_extension
        assert _validate_extension("fake_data.csv") == ".csv"

    def test_ekstensi_xlsx_diterima(self):
        """✅ File .xlsx harus diterima."""
        from app.services.log_service import _validate_extension
        assert _validate_extension("fake_data.xlsx") == ".xlsx"

    def test_ekstensi_xls_diterima(self):
        """✅ File .xls harus diterima."""
        from app.services.log_service import _validate_extension
        assert _validate_extension("fake_data.xls") == ".xls"

    def test_ekstensi_txt_ditolak(self):
        """❌ File .txt harus raise ValueError."""
        from app.services.log_service import _validate_extension
        with pytest.raises(ValueError) as exc:
            _validate_extension("fake_data.txt")
        assert "tidak didukung" in str(exc.value).lower()

    def test_ekstensi_pdf_ditolak(self):
        """❌ File .pdf harus raise ValueError."""
        from app.services.log_service import _validate_extension
        with pytest.raises(ValueError):
            _validate_extension("fake_laporan.pdf")

    def test_ekstensi_tanpa_nama_file_ditolak(self):
        """❌ File tanpa ekstensi harus raise ValueError."""
        from app.services.log_service import _validate_extension
        with pytest.raises(ValueError):
            _validate_extension("fake_tanpa_ekstensi")


# ═════════════════════════════════════════════════════════════════════════════
# TEST PARSE ROW CSV
# ═════════════════════════════════════════════════════════════════════════════

class TestParseRowCsv:

    def test_baris_valid_return_log_object(self):
        """✅ Baris valid harus return (LogPertemuan, None)."""
        from app.services.log_service import _parse_row

        row = {
            "tanggal": "2025-03-10",
            "topik":   "Fake Topik Valid",
            "nilai":   85.0,
            "catatan": "Fake catatan baris CSV",
        }

        with patch("app.services.log_service.LogPertemuan") as MockLog:
            MockLog.return_value = fake_log(topik="Fake Topik Valid")
            log_obj, err = _parse_row(row, fake_id())

        assert err is None

    def test_baris_tanpa_topik_return_error(self):
        """❌ Baris tanpa topik harus return (None, pesan_error)."""
        from app.services.log_service import _parse_row

        row = {
            "tanggal": "2025-03-10",
            "topik":   "",     # kosong — harus error
            "nilai":   80.0,
        }

        log_obj, err = _parse_row(row, fake_id())

        assert log_obj is None
        assert err is not None
        assert "topik" in err.lower()

    def test_baris_tanggal_kosong_pakai_hari_ini(self):
        """✅ Baris tanpa tanggal harus pakai tanggal hari ini."""
        from app.services.log_service import _parse_row

        row = {
            "tanggal": None,
            "topik":   "Fake Topik Tanpa Tanggal",
            "nilai":   75.0,
        }

        with patch("app.services.log_service.LogPertemuan") as MockLog:
            mock_instance = MagicMock()
            MockLog.return_value = mock_instance
            log_obj, err = _parse_row(row, fake_id())

        assert err is None

    def test_baris_nilai_optional(self):
        """✅ Baris tanpa nilai (nilai=None) harus tetap berhasil diparse."""
        from app.services.log_service import _parse_row

        row = {
            "tanggal": "2025-03-10",
            "topik":   "Fake Topik Tanpa Nilai",
            "nilai":   None,
        }

        with patch("app.services.log_service.LogPertemuan") as MockLog:
            MockLog.return_value = fake_log(nilai=None)
            log_obj, err = _parse_row(row, fake_id())

        assert err is None


# ═════════════════════════════════════════════════════════════════════════════
# TEST BULK UPLOAD
# ═════════════════════════════════════════════════════════════════════════════

class TestBulkUpload:

    def test_bulk_upload_file_kosong_raise_error(self):
        """❌ File dengan 0 bytes harus raise ValueError."""
        from app.services.log_service import bulk_upload_log

        db = mock_db()
        mock_file = MagicMock()
        mock_file.filename = "fake_upload.csv"
        mock_file.read = AsyncMock(return_value=b"")  # kosong

        with pytest.raises(ValueError) as exc:
            asyncio.get_event_loop().run_until_complete(
                bulk_upload_log(db, fake_id(), mock_file)
            )

        assert "kosong" in str(exc.value).lower()

    def test_bulk_upload_format_tidak_valid_raise_error(self):
        """❌ File .txt harus raise ValueError sebelum dibaca."""
        from app.services.log_service import bulk_upload_log

        db = mock_db()
        mock_file = MagicMock()
        mock_file.filename = "fake_data.txt"
        mock_file.read = AsyncMock(return_value=b"isi tidak penting")

        with pytest.raises(ValueError) as exc:
            asyncio.get_event_loop().run_until_complete(
                bulk_upload_log(db, fake_id(), mock_file)
            )

        assert "tidak didukung" in str(exc.value).lower()
