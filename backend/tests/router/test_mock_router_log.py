import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
import asyncio
from datetime import date
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import fake_id, fake_pengguna, fake_log, mock_db
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestLogHariIni — GET /logs/hari-ini
# ─────────────────────────────────────────────────────────────────────────────
 
class TestLogHariIni:
 
    def test_log_hari_ini_memanggil_service_dengan_pengajar_id(self):
        """✅ log_hari_ini harus memanggil get_logs_hari_ini dengan db dan current_user.id."""
        from app.routers.log import log_hari_ini
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.get_logs_hari_ini", return_value=[]) as mock_svc:
            log_hari_ini(current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, current_user.id)
 
    def test_log_hari_ini_return_list_log(self):
        """✅ Harus mengembalikan list log dari service."""
        from app.routers.log import log_hari_ini
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log1 = fake_log(topik="Fake Topik Hari Ini A")
        log2 = fake_log(topik="Fake Topik Hari Ini B")
 
        with patch("app.routers.log.get_logs_hari_ini", return_value=[log1, log2]):
            result = log_hari_ini(current_user=current_user, db=db)
 
        assert len(result) == 2
 
    def test_log_hari_ini_kosong_return_list_kosong(self):
        """✅ Tidak ada log hari ini → return list kosong."""
        from app.routers.log import log_hari_ini
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.get_logs_hari_ini", return_value=[]):
            result = log_hari_ini(current_user=current_user, db=db)
 
        assert result == []
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestLogsByKelas — GET /logs/kelas/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestLogsByKelas:
 
    def test_logs_by_kelas_memanggil_service(self):
        """✅ logs_by_kelas harus meneruskan semua parameter ke get_logs_by_kelas."""
        from app.routers.log import logs_by_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
 
        with patch("app.routers.log.get_logs_by_kelas", return_value=[]) as mock_svc:
            logs_by_kelas(
                kelas_id=kelas_id,
                murid_id=None,
                skip=0,
                limit=50,
                current_user=current_user,
                db=db,
            )
 
        mock_svc.assert_called_once_with(db, kelas_id, None, 0, 50)
 
    def test_logs_by_kelas_dengan_filter_murid(self):
        """✅ Filter murid_id harus diteruskan ke service."""
        from app.routers.log import logs_by_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        murid_id = fake_id()
 
        with patch("app.routers.log.get_logs_by_kelas", return_value=[]) as mock_svc:
            logs_by_kelas(
                kelas_id=kelas_id,
                murid_id=murid_id,
                skip=0,
                limit=50,
                current_user=current_user,
                db=db,
            )
 
        mock_svc.assert_called_once_with(db, kelas_id, murid_id, 0, 50)
 
    def test_logs_by_kelas_return_list_log(self):
        """✅ Harus mengembalikan list log yang diberikan service."""
        from app.routers.log import logs_by_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        logs = [fake_log(topik="Fake Log A"), fake_log(topik="Fake Log B")]
 
        with patch("app.routers.log.get_logs_by_kelas", return_value=logs):
            result = logs_by_kelas(
                kelas_id=fake_id(), murid_id=None, skip=0, limit=50,
                current_user=current_user, db=db,
            )
 
        assert len(result) == 2
 
    def test_logs_by_kelas_paginasi_diteruskan(self):
        """✅ Parameter skip dan limit harus diteruskan ke service."""
        from app.routers.log import logs_by_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.get_logs_by_kelas", return_value=[]) as mock_svc:
            logs_by_kelas(
                kelas_id=fake_id(), murid_id=None, skip=20, limit=10,
                current_user=current_user, db=db,
            )
 
        args = mock_svc.call_args[0]
        assert args[3] == 20   # skip
        assert args[4] == 10   # limit
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestLogsByMurid — GET /logs/murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestLogsByMurid:
 
    def test_logs_by_murid_memanggil_service(self):
        """✅ logs_by_murid harus memanggil get_logs_by_murid dengan semua parameter."""
        from app.routers.log import logs_by_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
 
        with patch("app.routers.log.get_logs_by_murid", return_value=[]) as mock_svc:
            logs_by_murid(murid_id=murid_id, skip=0, limit=50, current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, murid_id, 0, 50)
 
    def test_logs_by_murid_return_list(self):
        """✅ Harus mengembalikan log yang diberikan service."""
        from app.routers.log import logs_by_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        logs = [fake_log(murid_id=murid_id, topik="Fake Topik Murid")]
 
        with patch("app.routers.log.get_logs_by_murid", return_value=logs):
            result = logs_by_murid(murid_id=murid_id, skip=0, limit=50, current_user=current_user, db=db)
 
        assert len(result) == 1
        assert result[0].topik == "Fake Topik Murid"
 
    def test_logs_by_murid_kosong_return_list_kosong(self):
        """✅ Murid tanpa log → return list kosong."""
        from app.routers.log import logs_by_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.get_logs_by_murid", return_value=[]):
            result = logs_by_murid(murid_id=fake_id(), skip=0, limit=50, current_user=current_user, db=db)
 
        assert result == []
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestGetLog — GET /logs/{log_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestGetLog:
 
    def test_get_log_ditemukan_return_log(self):
        """✅ get_log harus mengembalikan log yang ditemukan service."""
        from app.routers.log import get_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log_obj = fake_log(topik="Fake Detail Log")
 
        with patch("app.routers.log.get_log_by_id", return_value=log_obj):
            result = get_log(log_id="fake-log-id-001", current_user=current_user, db=db)
 
        assert result.topik == "Fake Detail Log"
 
    def test_get_log_tidak_ditemukan_raise_404(self):
        """❌ Log tidak ada → raise HTTPException 404."""
        from app.routers.log import get_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.get_log_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                get_log(log_id="fake-log-id-tidak-ada", current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
        assert "log" in exc.value.detail.lower()
 
    def test_get_log_memanggil_service_dengan_log_id(self):
        """✅ Router harus meneruskan log_id ke get_log_by_id."""
        from app.routers.log import get_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log_obj = fake_log()
 
        with patch("app.routers.log.get_log_by_id", return_value=log_obj) as mock_svc:
            get_log(log_id="fake-target-log-id", current_user=current_user, db=db)
 
        mock_svc.assert_called_once_with(db, "fake-target-log-id")
 
    def test_get_log_tidak_commit(self):
        """✅ get_log adalah read-only — tidak boleh commit."""
        from app.routers.log import get_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.get_log_by_id", return_value=fake_log()):
            get_log(log_id="fake-log-id-readonly", current_user=current_user, db=db)
 
        db.commit.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestTambahLog — POST /logs/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestTambahLog:
 
    def _make_data(self, dengan_nilai=True, dengan_murid=True):
        from app.schemas.schemas import LogPertemuanCreate
        return LogPertemuanCreate(
            kelas_id=fake_id(),
            murid_id=fake_id() if dengan_murid else None,
            tanggal=date(2025, 3, 10),
            topik="Fake Topik Tambah Log",
            nilai=80.0 if dengan_nilai else None,
            tingkat_pemahaman="paham",
            durasi_menit=90,
        )
 
    def test_tambah_log_memanggil_create_log(self):
        """✅ tambah_log harus memanggil create_log dengan db dan data."""
        from app.routers.log import tambah_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log_obj = fake_log()
        data = self._make_data()
 
        with patch("app.routers.log.create_log", return_value=log_obj) as mock_create, \
             patch("app.routers.log.update_knowledge_states"):
            result = tambah_log(data=data, current_user=current_user, db=db)
 
        mock_create.assert_called_once_with(db, data)
 
    def test_tambah_log_return_log_yang_dibuat(self):
        """✅ tambah_log harus mengembalikan log yang dihasilkan service."""
        from app.routers.log import tambah_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log_obj = fake_log(topik="Fake Log Baru Tersimpan")
        data = self._make_data()
 
        with patch("app.routers.log.create_log", return_value=log_obj), \
             patch("app.routers.log.update_knowledge_states"):
            result = tambah_log(data=data, current_user=current_user, db=db)
 
        assert result.topik == "Fake Log Baru Tersimpan"
 
    def test_tambah_log_dengan_nilai_dan_murid_update_bkt(self):
        """✅ Jika ada nilai DAN murid_id, harus memanggil update_knowledge_states."""
        from app.routers.log import tambah_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        kelas_id = fake_id()
        log_obj = fake_log(kelas_id=kelas_id, murid_id=murid_id, nilai=85.0)
        data = self._make_data(dengan_nilai=True, dengan_murid=True)
 
        with patch("app.routers.log.create_log", return_value=log_obj), \
             patch("app.routers.log.update_knowledge_states") as mock_bkt:
            tambah_log(data=data, current_user=current_user, db=db)
 
        mock_bkt.assert_called_once_with(db, log_obj.murid_id, log_obj.kelas_id)
 
    def test_tambah_log_tanpa_nilai_tidak_update_bkt(self):
        """✅ Jika nilai None, update_knowledge_states tidak dipanggil."""
        from app.routers.log import tambah_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log_obj = fake_log(nilai=None)
        log_obj.nilai = None
        data = self._make_data(dengan_nilai=False, dengan_murid=True)
 
        with patch("app.routers.log.create_log", return_value=log_obj), \
             patch("app.routers.log.update_knowledge_states") as mock_bkt:
            tambah_log(data=data, current_user=current_user, db=db)
 
        mock_bkt.assert_not_called()
 
    def test_tambah_log_tanpa_murid_tidak_update_bkt(self):
        """✅ Jika murid_id None, update_knowledge_states tidak dipanggil."""
        from app.routers.log import tambah_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        log_obj = fake_log(murid_id=None, nilai=80.0)
        log_obj.murid_id = None
        data = self._make_data(dengan_nilai=True, dengan_murid=False)
 
        with patch("app.routers.log.create_log", return_value=log_obj), \
             patch("app.routers.log.update_knowledge_states") as mock_bkt:
            tambah_log(data=data, current_user=current_user, db=db)
 
        mock_bkt.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestBulkLog — POST /logs/bulk/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestBulkLog:
 
    def _make_fake_file(self, filename="fake-log-data.csv"):
        file = MagicMock()
        file.filename = filename
        file.content_type = "text/csv"
        return file
 
    def test_bulk_log_berhasil_return_bulk_response(self):
        """✅ bulk_log berhasil harus return BulkUploadResponse dari service."""
        from app.routers.log import bulk_log
        from app.schemas.schemas import BulkUploadResponse
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        fake_file = self._make_fake_file()
 
        bulk_resp = BulkUploadResponse(total_baris=10, berhasil=9, gagal=1, detail_error=[])
 
        async def run():
            with patch("app.routers.log.bulk_upload_log", new=AsyncMock(return_value=bulk_resp)):
                return await bulk_log(kelas_id=kelas_id, file=fake_file, current_user=current_user, db=db)
 
        result = asyncio.get_event_loop().run_until_complete(run())
 
        assert result.total_baris == 10
        assert result.berhasil    == 9
        assert result.gagal       == 1
 
    def test_bulk_log_value_error_raise_400(self):
        """❌ ValueError dari service (format file salah) harus raise 400."""
        from app.routers.log import bulk_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        fake_file = self._make_fake_file(filename="fake-invalid.txt")
 
        async def run():
            with patch("app.routers.log.bulk_upload_log",
                       new=AsyncMock(side_effect=ValueError("Format file tidak didukung"))):
                return await bulk_log(kelas_id=fake_id(), file=fake_file, current_user=current_user, db=db)
 
        with pytest.raises(HTTPException) as exc:
            asyncio.get_event_loop().run_until_complete(run())
 
        assert exc.value.status_code == 400
 
    def test_bulk_log_memanggil_service_dengan_kelas_id_dan_file(self):
        """✅ bulk_log harus meneruskan kelas_id dan file ke bulk_upload_log."""
        from app.routers.log import bulk_log
        from app.schemas.schemas import BulkUploadResponse
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_id = fake_id()
        fake_file = self._make_fake_file()
        bulk_resp = BulkUploadResponse(total_baris=5, berhasil=5, gagal=0)
 
        async def run():
            with patch("app.routers.log.bulk_upload_log", new=AsyncMock(return_value=bulk_resp)) as mock_svc:
                await bulk_log(kelas_id=kelas_id, file=fake_file, current_user=current_user, db=db)
                mock_svc.assert_called_once_with(db, kelas_id, fake_file)
 
        asyncio.get_event_loop().run_until_complete(run())
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestEditLog — PUT /logs/{log_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestEditLog:
 
    def _make_update_data(self):
        from app.schemas.schemas import LogPertemuanUpdate
        return LogPertemuanUpdate(
            topik="Fake Topik Diperbarui",
            nilai=90.0,
            tingkat_pemahaman="sangat_paham",
        )
 
    def test_edit_log_berhasil_return_log_baru(self):
        """✅ edit_log berhasil harus mengembalikan log yang sudah diupdate."""
        from app.routers.log import edit_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        updated_log = fake_log(topik="Fake Topik Diperbarui", nilai=90.0)
        data = self._make_update_data()
 
        with patch("app.routers.log.update_log", return_value=updated_log), \
             patch("app.routers.log.update_knowledge_states"):
            result = edit_log(log_id="fake-log-id-edit", data=data, current_user=current_user, db=db)
 
        assert result.topik == "Fake Topik Diperbarui"
        assert result.nilai == 90.0
 
    def test_edit_log_tidak_ditemukan_raise_404(self):
        """❌ Log tidak ada → raise 404."""
        from app.routers.log import edit_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        data = self._make_update_data()
 
        with patch("app.routers.log.update_log", return_value=None):
            with pytest.raises(HTTPException) as exc:
                edit_log(log_id="fake-log-id-tidak-ada", data=data, current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
 
    def test_edit_log_dengan_nilai_update_bkt(self):
        """✅ Setelah edit, jika ada nilai dan murid_id, harus update BKT."""
        from app.routers.log import edit_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_id = fake_id()
        kelas_id = fake_id()
        updated_log = fake_log(kelas_id=kelas_id, murid_id=murid_id, nilai=88.0)
        data = self._make_update_data()
 
        with patch("app.routers.log.update_log", return_value=updated_log), \
             patch("app.routers.log.update_knowledge_states") as mock_bkt:
            edit_log(log_id="fake-log-id-bkt", data=data, current_user=current_user, db=db)
 
        mock_bkt.assert_called_once_with(db, updated_log.murid_id, updated_log.kelas_id)
 
    def test_edit_log_tanpa_nilai_tidak_update_bkt(self):
        """✅ Edit log tanpa nilai → update_knowledge_states tidak dipanggil."""
        from app.routers.log import edit_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        updated_log = fake_log(nilai=None)
        updated_log.nilai = None
        data = self._make_update_data()
 
        with patch("app.routers.log.update_log", return_value=updated_log), \
             patch("app.routers.log.update_knowledge_states") as mock_bkt:
            edit_log(log_id="fake-log-id-tanpa-nilai", data=data, current_user=current_user, db=db)
 
        mock_bkt.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestHapusLog — DELETE /logs/{log_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestHapusLog:
 
    def test_hapus_log_berhasil_return_none(self):
        """✅ hapus_log berhasil → return None (status 204)."""
        from app.routers.log import hapus_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.delete_log", return_value=True):
            result = hapus_log(log_id="fake-log-id-hapus", current_user=current_user, db=db)
 
        assert result is None
 
    def test_hapus_log_tidak_ditemukan_raise_404(self):
        """❌ Log tidak ada → raise 404."""
        from app.routers.log import hapus_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.delete_log", return_value=False):
            with pytest.raises(HTTPException) as exc:
                hapus_log(log_id="fake-log-id-tidak-ada", current_user=current_user, db=db)
 
        assert exc.value.status_code == 404
        assert "log" in exc.value.detail.lower()
 
    def test_hapus_log_memanggil_delete_service(self):
        """✅ hapus_log harus memanggil delete_log dengan db dan log_id yang benar."""
        from app.routers.log import hapus_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        target_log_id = "fake-target-log-id-hapus"
 
        with patch("app.routers.log.delete_log", return_value=True) as mock_del:
            hapus_log(log_id=target_log_id, current_user=current_user, db=db)
 
        mock_del.assert_called_once_with(db, target_log_id)
 
    def test_hapus_log_tidak_ada_add(self):
        """✅ hapus_log tidak boleh memanggil db.add."""
        from app.routers.log import hapus_log
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.log.delete_log", return_value=True):
            hapus_log(log_id="fake-log-id-clean", current_user=current_user, db=db)
 
        db.add.assert_not_called()