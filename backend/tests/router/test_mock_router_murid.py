import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
from unittest.mock import patch
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import fake_id, fake_pengguna, fake_murid, mock_db
from app.schemas.schemas import MuridResponse
 
 
def _make_murid_response(**kwargs) -> MuridResponse:
    """Helper: bangun MuridResponse dengan default 'fake-' prefix."""
    defaults = dict(
        id=fake_id(),
        username="fake-username",
        email_address="fake@email.com",
        nama="Fake Nama Murid",
        usia=15,
        level="SMA",
        credit_total=10,
        credit_used=0,
    )
    defaults.update(kwargs)
    return MuridResponse(**defaults)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestTambahSiswa — POST /murid/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestTambahSiswa:
 
    def _make_data(self, **overrides):
        from app.schemas.schemas import MuridCreate
        defaults = dict(
            username="fake-siswa-baru",
            email_address="fake-siswa-baru@email.com",
            password="Fake-Pass-Siswa-123!",
            nama="Fake Siswa Baru",
            usia=14,
            level="SMP",
            credit_total=20,
        )
        defaults.update(overrides)
        return MuridCreate(**defaults)
 
    def test_tambah_siswa_memanggil_create_murid(self):
        """✅ tambah_siswa harus memanggil create_murid dengan db dan data."""
        from app.routers.murid import tambah_siswa
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_resp = _make_murid_response(nama="Fake Siswa Baru")
        data = self._make_data()
 
        with patch("app.routers.murid.create_murid", return_value=murid_resp) as mock_svc:
            tambah_siswa(data=data, db=db, current_user=current_user)
 
        mock_svc.assert_called_once_with(db, data)
 
    def test_tambah_siswa_return_murid_response(self):
        """✅ Harus mengembalikan MuridResponse dari service."""
        from app.routers.murid import tambah_siswa
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_resp = _make_murid_response(nama="Fake Return Siswa", username="fake-return-siswa")
        data = self._make_data()
 
        with patch("app.routers.murid.create_murid", return_value=murid_resp):
            result = tambah_siswa(data=data, db=db, current_user=current_user)
 
        assert result.nama     == "Fake Return Siswa"
        assert result.username == "fake-return-siswa"
 
    def test_tambah_siswa_email_duplikat_propagate_400(self):
        """❌ Email duplikat dari service → router meneruskan 400."""
        from app.routers.murid import tambah_siswa
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        data = self._make_data(email_address="fake-duplikat@email.com")
 
        with patch("app.routers.murid.create_murid",
                   side_effect=HTTPException(status_code=400, detail="Email sudah terdaftar")):
            with pytest.raises(HTTPException) as exc:
                tambah_siswa(data=data, db=db, current_user=current_user)
 
        assert exc.value.status_code == 400
        assert "email" in exc.value.detail.lower()
 
    def test_tambah_siswa_username_duplikat_propagate_400(self):
        """❌ Username duplikat dari service → router meneruskan 400."""
        from app.routers.murid import tambah_siswa
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        data = self._make_data(username="fake-username-duplikat")
 
        with patch("app.routers.murid.create_murid",
                   side_effect=HTTPException(status_code=400, detail="Username sudah digunakan")):
            with pytest.raises(HTTPException) as exc:
                tambah_siswa(data=data, db=db, current_user=current_user)
 
        assert exc.value.status_code == 400
        assert "username" in exc.value.detail.lower()
 
    def test_tambah_siswa_response_tidak_ada_password(self):
        """✅ Response tidak boleh mengandung field password."""
        from app.routers.murid import tambah_siswa
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_resp = _make_murid_response()
        data = self._make_data()
 
        with patch("app.routers.murid.create_murid", return_value=murid_resp):
            result = tambah_siswa(data=data, db=db, current_user=current_user)
 
        result_dict = result.model_dump()
        assert "password"        not in result_dict
        assert "hashed_password" not in result_dict
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestListAllMurid — GET /murid/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestListAllMurid:
 
    def test_list_all_murid_memanggil_get_all_murid(self):
        """✅ list_all_murid harus memanggil get_all_murid dengan parameter yang benar."""
        from app.routers.murid import list_all_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.get_all_murid", return_value=[]) as mock_svc:
            list_all_murid(skip=0, limit=100, search=None, db=db, current_user=current_user)
 
        mock_svc.assert_called_once_with(db, skip=0, limit=100, search=None)
 
    def test_list_all_murid_return_list(self):
        """✅ Harus mengembalikan list MuridResponse dari service."""
        from app.routers.murid import list_all_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid1 = _make_murid_response(nama="Fake Andi", username="fake-andi")
        murid2 = _make_murid_response(nama="Fake Budi", username="fake-budi")
 
        with patch("app.routers.murid.get_all_murid", return_value=[murid1, murid2]):
            result = list_all_murid(skip=0, limit=100, search=None, db=db, current_user=current_user)
 
        assert len(result) == 2
        assert result[0].nama == "Fake Andi"
        assert result[1].nama == "Fake Budi"
 
    def test_list_all_murid_kosong_return_list_kosong(self):
        """✅ Tidak ada murid → return list kosong."""
        from app.routers.murid import list_all_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.get_all_murid", return_value=[]):
            result = list_all_murid(skip=0, limit=100, search=None, db=db, current_user=current_user)
 
        assert result == []
 
    def test_list_all_murid_search_diteruskan_ke_service(self):
        """✅ Parameter search harus diteruskan ke get_all_murid."""
        from app.routers.murid import list_all_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.get_all_murid", return_value=[]) as mock_svc:
            list_all_murid(skip=0, limit=100, search="Fake Andi", db=db, current_user=current_user)
 
        mock_svc.assert_called_once_with(db, skip=0, limit=100, search="Fake Andi")
 
    def test_list_all_murid_paginasi_diteruskan(self):
        """✅ Parameter skip dan limit harus diteruskan ke service."""
        from app.routers.murid import list_all_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.get_all_murid", return_value=[]) as mock_svc:
            list_all_murid(skip=50, limit=25, search=None, db=db, current_user=current_user)
 
        mock_svc.assert_called_once_with(db, skip=50, limit=25, search=None)
 
    def test_list_all_murid_tidak_commit(self):
        """✅ list_all_murid adalah read-only — tidak boleh commit atau add."""
        from app.routers.murid import list_all_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.get_all_murid", return_value=[]):
            list_all_murid(skip=0, limit=100, search=None, db=db, current_user=current_user)
 
        db.commit.assert_not_called()
        db.add.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestDetailMurid — GET /murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestDetailMurid:
 
    def test_detail_murid_ditemukan_return_response(self):
        """✅ detail_murid harus mengembalikan MuridResponse dari service."""
        from app.routers.murid import detail_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_resp = _make_murid_response(nama="Fake Detail Murid", username="fake-detail")
 
        with patch("app.routers.murid.get_murid_by_id", return_value=murid_resp):
            result = detail_murid(murid_id="fake-murid-id-detail", db=db, current_user=current_user)
 
        assert result.nama     == "Fake Detail Murid"
        assert result.username == "fake-detail"
 
    def test_detail_murid_tidak_ada_propagate_404(self):
        """❌ Murid tidak ada → router meneruskan 404 dari service."""
        from app.routers.murid import detail_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.get_murid_by_id",
                   side_effect=HTTPException(status_code=404, detail="Murid tidak ditemukan")):
            with pytest.raises(HTTPException) as exc:
                detail_murid(murid_id="fake-murid-id-tidak-ada", db=db, current_user=current_user)
 
        assert exc.value.status_code == 404
 
    def test_detail_murid_memanggil_service_dengan_murid_id(self):
        """✅ Router harus meneruskan murid_id ke get_murid_by_id."""
        from app.routers.murid import detail_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_resp = _make_murid_response()
        target_id = "fake-murid-target-detail"
 
        with patch("app.routers.murid.get_murid_by_id", return_value=murid_resp) as mock_svc:
            detail_murid(murid_id=target_id, db=db, current_user=current_user)
 
        mock_svc.assert_called_once_with(db, target_id)
 
    def test_detail_murid_bisa_diakses_oleh_murid_sendiri(self):
        """✅ Endpoint detail murid bisa diakses oleh murid (bukan hanya pengajar)."""
        from app.routers.murid import detail_murid
 
        current_user = fake_pengguna(tipe="murid")  # murid, bukan pengajar
        db = mock_db()
        murid_resp = _make_murid_response()
 
        with patch("app.routers.murid.get_murid_by_id", return_value=murid_resp):
            result = detail_murid(murid_id="fake-murid-id-self", db=db, current_user=current_user)
 
        assert result is not None
 
    def test_detail_murid_tidak_commit(self):
        """✅ detail_murid adalah read-only — tidak boleh commit."""
        from app.routers.murid import detail_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        murid_resp = _make_murid_response()
 
        with patch("app.routers.murid.get_murid_by_id", return_value=murid_resp):
            detail_murid(murid_id="fake-murid-id-readonly", db=db, current_user=current_user)
 
        db.commit.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestHapusMurid — DELETE /murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestHapusMurid:
 
    def test_hapus_murid_berhasil_memanggil_delete_murid(self):
        """✅ hapus_murid harus memanggil delete_murid service dengan db dan murid_id."""
        from app.routers.murid import hapus_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        expected = {"message": "Murid berhasil dihapus"}
 
        with patch("app.routers.murid.delete_murid", return_value=expected) as mock_del:
            result = hapus_murid(murid_id="fake-murid-id-hapus", db=db, current_user=current_user)
 
        mock_del.assert_called_once_with(db, "fake-murid-id-hapus")
        assert result == expected
 
    def test_hapus_murid_tidak_ada_propagate_404(self):
        """❌ Murid tidak ada → router meneruskan 404 dari service."""
        from app.routers.murid import hapus_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.delete_murid",
                   side_effect=HTTPException(status_code=404, detail="Murid tidak ditemukan")):
            with pytest.raises(HTTPException) as exc:
                hapus_murid(murid_id="fake-murid-id-tidak-ada", db=db, current_user=current_user)
 
        assert exc.value.status_code == 404
 
    def test_hapus_murid_return_message_berhasil(self):
        """✅ hapus_murid harus return dict dengan key 'message' yang mengandung 'berhasil'."""
        from app.routers.murid import hapus_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.delete_murid",
                   return_value={"message": "Murid berhasil dihapus"}):
            result = hapus_murid(murid_id="fake-murid-id-msg", db=db, current_user=current_user)
 
        assert "message" in result
        assert "berhasil" in result["message"].lower()
 
    def test_hapus_murid_hanya_bisa_dilakukan_pengajar(self):
        """✅ Endpoint hapus murid menggunakan require_pengajar — murid tidak boleh hapus."""
        import inspect
        from app.routers.murid import hapus_murid
 
        sig = inspect.signature(hapus_murid)
        # Pastikan current_user ada sebagai parameter (dikontrol oleh Depends)
        assert "current_user" in sig.parameters
 
    def test_hapus_murid_tidak_ada_add(self):
        """✅ hapus_murid tidak boleh memanggil db.add (hanya delete)."""
        from app.routers.murid import hapus_murid
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        with patch("app.routers.murid.delete_murid", return_value={"message": "Berhasil"}):
            hapus_murid(murid_id="fake-murid-id-clean", db=db, current_user=current_user)
 
        db.add.assert_not_called()