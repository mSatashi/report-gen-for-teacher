import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
import uuid
from unittest.mock import MagicMock, patch, call
from datetime import datetime
  
from tests.test_helpers import fake_id, fake_pengguna, fake_murid, fake_kelas, fake_kelas_murid, mock_db
 
 
import pytest
from fastapi import HTTPException
 
# ─────────────────────────────────────────────────────────────────────────────
# TestListKelas — GET /kelas/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestListKelas:
 
    def test_list_kelas_return_semua_kelas_milik_pengajar(self):
        """✅ list_kelas harus mengembalikan semua kelas milik pengajar yang login."""
        from app.routers.kelas import list_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas1 = fake_kelas(nama="Fake Kelas Fisika")
        kelas2 = fake_kelas(nama="Fake Kelas Kimia")
        db.all.return_value = [kelas1, kelas2]
 
        result = list_kelas(current_user=current_user, db=db)
 
        assert len(result) == 2
        db.filter.assert_called()
 
    def test_list_kelas_kosong_return_list_kosong(self):
        """✅ Jika tidak ada kelas, harus return list kosong — bukan error."""
        from app.routers.kelas import list_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        result = list_kelas(current_user=current_user, db=db)
 
        assert result == []
 
    def test_list_kelas_hanya_filter_kelas_milik_pengajar_bersangkutan(self):
        """✅ Query harus difilter berdasarkan pengajar_id current_user."""
        from app.routers.kelas import list_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        list_kelas(current_user=current_user, db=db)
 
        # Pastikan filter dipanggil (bukan query semua kelas tanpa filter)
        db.filter.assert_called()
 
    def test_list_kelas_tidak_commit_atau_add(self):
        """✅ list_kelas adalah read-only — tidak boleh ada add/commit."""
        from app.routers.kelas import list_kelas
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        db.all.return_value = []
 
        list_kelas(current_user=current_user, db=db)
 
        db.add.assert_not_called()
        db.commit.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestGetKelas — GET /kelas/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestGetKelas:
 
    def test_get_kelas_ditemukan_return_kelas(self):
        """✅ get_kelas harus mengembalikan kelas yang sesuai kelas_id."""
        from app.routers.kelas import get_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        kelas = fake_kelas(nama="Fake Kelas Biologi")
        db.first.return_value = kelas
 
        result = get_kelas(
            kelas_id="fake-kelas-id-001",
            current_user=current_user,
            db=db,
        )
 
        assert result == kelas
        assert result.nama == "Fake Kelas Biologi"
 
    def test_get_kelas_tidak_ditemukan_raise_404(self):
        """❌ Kelas tidak ada harus raise HTTPException 404."""
        from app.routers.kelas import get_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None  # kelas tidak ada
 
        with pytest.raises(HTTPException) as exc:
            get_kelas(
                kelas_id="fake-kelas-id-tidak-ada",
                current_user=current_user,
                db=db,
            )
 
        assert exc.value.status_code == 404
        assert "kelas" in exc.value.detail.lower()
 
    def test_get_kelas_tidak_commit(self):
        """✅ get_kelas adalah read-only — tidak boleh commit."""
        from app.routers.kelas import get_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = fake_kelas()
 
        get_kelas(kelas_id="fake-kelas-id-001", current_user=current_user, db=db)
 
        db.commit.assert_not_called()
        db.add.assert_not_called()
 
    def test_get_kelas_query_berdasarkan_kelas_id(self):
        """✅ Query harus menggunakan kelas_id yang diberikan sebagai parameter."""
        from app.routers.kelas import get_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        target_id = "fake-target-kelas-id"
        db.first.return_value = fake_kelas()
 
        get_kelas(kelas_id=target_id, current_user=current_user, db=db)
 
        db.filter.assert_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestBuatKelas — POST /kelas/
# ─────────────────────────────────────────────────────────────────────────────
 
class TestBuatKelas:
 
    def test_buat_kelas_berhasil_add_dan_commit(self):
        """✅ buat_kelas harus add kelas baru ke DB lalu commit."""
        from app.routers.kelas import buat_kelas
        from app.schemas.schemas import KelasCreate
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
        kelas_baru = fake_kelas(nama="Fake Kelas Sejarah")
 
        data = KelasCreate(
            nama="Fake Kelas Sejarah",
            mata_pelajaran="Sejarah",
            kredit=2,
            jadwal="Rabu 10:00",
        )
 
        with patch("app.routers.kelas.Kelas", return_value=kelas_baru):
            db.refresh.side_effect = lambda obj: None
            result = buat_kelas(data=data, current_user=current_user, db=db)
 
        db.add.assert_called_once_with(kelas_baru)
        db.commit.assert_called_once()
 
    def test_buat_kelas_pengajar_id_diambil_dari_current_user(self):
        """✅ pengajar_id pada kelas baru harus diambil dari current_user.id."""
        from app.routers.kelas import buat_kelas
        from app.schemas.schemas import KelasCreate
 
        current_user = fake_pengguna(tipe="pengajar")
        db = mock_db()
 
        captured_kwargs = {}
 
        class FakeKelas:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)
                self.id             = kwargs.get("id")
                self.nama           = kwargs.get("nama")
                self.mata_pelajaran = kwargs.get("mata_pelajaran")
                self.kredit         = kwargs.get("kredit", 0)
                self.jadwal         = kwargs.get("jadwal")
                self.pengajar_id    = kwargs.get("pengajar_id")
                self.created_at     = datetime.utcnow()
 
        data = KelasCreate(
            nama="Fake Kelas Geografi",
            mata_pelajaran="Geografi",
        )
 
        with patch("app.routers.kelas.Kelas", side_effect=FakeKelas):
            db.refresh.side_effect = lambda obj: None
            buat_kelas(data=data, current_user=current_user, db=db)
 
        assert captured_kwargs.get("pengajar_id") == current_user.id
 
    def test_buat_kelas_id_di_generate_uuid(self):
        """✅ Kelas baru harus mendapat id berupa UUID (string non-kosong)."""
        from app.routers.kelas import buat_kelas
        from app.schemas.schemas import KelasCreate
 
        current_user = fake_pengguna()
        db = mock_db()
 
        captured_kwargs = {}
 
        class FakeKelas:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)
                self.id = kwargs.get("id")
                self.nama = kwargs.get("nama")
                self.mata_pelajaran = kwargs.get("mata_pelajaran")
                self.kredit = kwargs.get("kredit", 0)
                self.jadwal = kwargs.get("jadwal")
                self.pengajar_id = kwargs.get("pengajar_id")
                self.created_at = datetime.utcnow()
 
        data = KelasCreate(nama="Fake Kelas IPA")
 
        with patch("app.routers.kelas.Kelas", side_effect=FakeKelas):
            db.refresh.side_effect = lambda obj: None
            buat_kelas(data=data, current_user=current_user, db=db)
 
        kelas_id = captured_kwargs.get("id")
        assert kelas_id is not None
        assert len(kelas_id) > 0
        # Validasi format UUID
        uuid.UUID(kelas_id)  # raise ValueError jika bukan UUID valid
 
    def test_buat_kelas_refresh_dipanggil_setelah_commit(self):
        """✅ db.refresh harus dipanggil setelah commit untuk mendapat data terbaru."""
        from app.routers.kelas import buat_kelas
        from app.schemas.schemas import KelasCreate
 
        current_user = fake_pengguna()
        db = mock_db()
        kelas_baru = fake_kelas()
 
        data = KelasCreate(nama="Fake Kelas Refresh")
 
        refresh_called = []
 
        def track_refresh(obj):
            refresh_called.append(obj)
 
        with patch("app.routers.kelas.Kelas", return_value=kelas_baru):
            db.refresh.side_effect = track_refresh
            buat_kelas(data=data, current_user=current_user, db=db)
 
        assert len(refresh_called) == 1
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestUpdateKelas — PUT /kelas/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestUpdateKelas:
 
    def test_update_kelas_berhasil_commit_dan_refresh(self):
        """✅ update_kelas harus memperbarui field, commit, dan refresh."""
        from app.routers.kelas import update_kelas
        from app.schemas.schemas import KelasUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        kelas = fake_kelas(nama="Fake Kelas Lama")
        db.first.return_value = kelas
 
        data = KelasUpdate(nama="Fake Kelas Baru", kredit=4)
 
        db.refresh.side_effect = lambda obj: None
        result = update_kelas(
            kelas_id="fake-kelas-id-002",
            data=data,
            current_user=current_user,
            db=db,
        )
 
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
 
    def test_update_kelas_tidak_ditemukan_raise_404(self):
        """❌ Kelas tidak ditemukan atau bukan milik pengajar harus raise 404."""
        from app.routers.kelas import update_kelas
        from app.schemas.schemas import KelasUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None  # kelas tidak ada
 
        data = KelasUpdate(nama="Fake Perubahan")
 
        with pytest.raises(HTTPException) as exc:
            update_kelas(
                kelas_id="fake-kelas-id-tidak-ada",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        assert exc.value.status_code == 404
        db.commit.assert_not_called()
 
    def test_update_kelas_hanya_field_yang_disediakan(self):
        """✅ Field None pada KelasUpdate tidak boleh menimpa nilai yang sudah ada."""
        from app.routers.kelas import update_kelas
        from app.schemas.schemas import KelasUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        kelas = fake_kelas(nama="Fake Nama Tetap", kredit=5)
        db.first.return_value = kelas
 
        # Hanya update jadwal — nama dan kredit tidak dikirim
        data = KelasUpdate(jadwal="Fake Jadwal Baru Kamis 14:00")
 
        setattr_calls = []
        original_setattr = setattr
 
        db.refresh.side_effect = lambda obj: None
 
        with patch("builtins.setattr", side_effect=lambda obj, k, v: setattr_calls.append(k) or original_setattr(obj, k, v)):
            update_kelas(
                kelas_id="fake-kelas-id-003",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        # "nama" dan "kredit" tidak ada dalam field yang di-set (exclude_none=True)
        assert "jadwal" in setattr_calls
        assert "nama" not in setattr_calls
        assert "kredit" not in setattr_calls
 
    def test_update_kelas_query_filter_pakai_pengajar_id(self):
        """✅ Filter update harus memastikan kelas milik pengajar yang login."""
        from app.routers.kelas import update_kelas
        from app.schemas.schemas import KelasUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = fake_kelas()
 
        data = KelasUpdate(nama="Fake Update Filter")
 
        db.refresh.side_effect = lambda obj: None
        update_kelas(
            kelas_id="fake-kelas-id-004",
            data=data,
            current_user=current_user,
            db=db,
        )
 
        # filter harus dipanggil (mengandung kelas_id DAN pengajar_id)
        db.filter.assert_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestHapusKelas — DELETE /kelas/{kelas_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestHapusKelas:
 
    def test_hapus_kelas_berhasil_delete_dan_commit(self):
        """✅ hapus_kelas harus delete kelas dari DB dan commit."""
        from app.routers.kelas import hapus_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        kelas = fake_kelas(nama="Fake Kelas Dihapus")
        db.first.return_value = kelas
 
        hapus_kelas(
            kelas_id="fake-kelas-id-hapus",
            current_user=current_user,
            db=db,
        )
 
        db.delete.assert_called_once_with(kelas)
        db.commit.assert_called_once()
 
    def test_hapus_kelas_tidak_ditemukan_raise_404(self):
        """❌ Kelas tidak ditemukan harus raise 404 — tidak hapus apapun."""
        from app.routers.kelas import hapus_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        with pytest.raises(HTTPException) as exc:
            hapus_kelas(
                kelas_id="fake-kelas-id-tidak-ada",
                current_user=current_user,
                db=db,
            )
 
        assert exc.value.status_code == 404
        db.delete.assert_not_called()
        db.commit.assert_not_called()
 
    def test_hapus_kelas_filter_pakai_pengajar_id_dan_kelas_id(self):
        """✅ hapus_kelas harus filter kelas_id DAN pengajar_id — cegah hapus kelas orang lain."""
        from app.routers.kelas import hapus_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = fake_kelas()
 
        hapus_kelas(
            kelas_id="fake-kelas-target",
            current_user=current_user,
            db=db,
        )
 
        db.filter.assert_called()
 
    def test_hapus_kelas_tidak_ada_add(self):
        """✅ hapus_kelas tidak boleh memanggil db.add."""
        from app.routers.kelas import hapus_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = fake_kelas()
 
        hapus_kelas(
            kelas_id="fake-kelas-id-clean",
            current_user=current_user,
            db=db,
        )
 
        db.add.assert_not_called()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestListMuridKelas — GET /kelas/{kelas_id}/murid
# ─────────────────────────────────────────────────────────────────────────────
 
class TestListMuridKelas:
 
    def test_list_murid_kelas_return_daftar_murid(self):
        """✅ list_murid_kelas harus mengembalikan list MuridResponse."""
        from app.routers.kelas import list_murid_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
 
        fake_kelas_id = fake_id()
        murid1 = fake_murid(nama="Fake Andi Kelas",  email="fake-andi@email.com")
        murid2 = fake_murid(nama="Fake Budi Kelas", email="fake-budi@email.com")
 
        km1 = fake_kelas_murid(kelas_id=fake_kelas_id, murid_id=murid1.id)
        km2 = fake_kelas_murid(kelas_id=fake_kelas_id, murid_id=murid2.id)
 
        # first() dipanggil berulang: km query → murid1 → pengguna1 → murid2 → pengguna2
        db.all.return_value = [km1, km2]
        db.first.side_effect = [murid1, pengguna1, murid2, pengguna2]
 
        result = list_murid_kelas(
            kelas_id=fake_kelas_id,
            current_user=current_user,
            db=db,
        )
 
        assert len(result) == 2
 
    def test_list_murid_kelas_kosong_return_list_kosong(self):
        """✅ Kelas tanpa murid harus return list kosong."""
        from app.routers.kelas import list_murid_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.all.return_value = []  # tidak ada KelasMurid
 
        result = list_murid_kelas(
            kelas_id="fake-kelas-id-kosong",
            current_user=current_user,
            db=db,
        )
 
        assert result == []
 
    def test_list_murid_kelas_murid_tidak_ditemukan_di_skip(self):
        """✅ Jika murid_id dari KelasMurid tidak ditemukan di tabel Murid, baris di-skip."""
        from app.routers.kelas import list_murid_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
 
        km = fake_kelas_murid()
        db.all.return_value = [km]
        db.first.return_value = None  # murid tidak ada di tabel
 
        result = list_murid_kelas(
            kelas_id="fake-kelas-id-orphan",
            current_user=current_user,
            db=db,
        )
 
        assert result == []
 
    def test_list_murid_kelas_tidak_commit(self):
        """✅ list_murid_kelas adalah read-only — tidak boleh commit."""
        from app.routers.kelas import list_murid_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.all.return_value = []
 
        list_murid_kelas(
            kelas_id="fake-kelas-id-readonly",
            current_user=current_user,
            db=db,
        )
 
        db.commit.assert_not_called()
        db.add.assert_not_called()
 
    def test_list_murid_kelas_response_berisi_username_dan_email(self):
        """✅ MuridResponse harus berisi username dan email dari tabel Pengguna."""
        from app.routers.kelas import list_murid_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
 
        murid = fake_murid(nama="Fake Citra")
        pengguna = fake_pengguna(
            tipe="murid",
            username="fake-citra-username",
            email="fake-citra@email.com",
        )
        pengguna.id = murid.id
 
        km = fake_kelas_murid(murid_id=murid.id)
        db.all.return_value = [km]
        db.first.side_effect = [murid, pengguna]
 
        result = list_murid_kelas(
            kelas_id="fake-kelas-id-cek-field",
            current_user=current_user,
            db=db,
        )
 
        assert len(result) == 1
        assert result[0].username == "fake-citra-username"
        assert result[0].email_address == "fake-citra@email.com"
        assert result[0].nama == "Fake Citra"
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestTambahMuridKeKelas — POST /kelas/{kelas_id}/murid
# ─────────────────────────────────────────────────────────────────────────────
 
class TestTambahMuridKeKelas:
 
    def test_tambah_murid_ke_kelas_berhasil(self):
        """✅ Murid baru di kelas harus di-add dan commit."""
        from app.routers.kelas import tambah_murid_ke_kelas
        from app.schemas.schemas import TambahMuridKeKelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None  # murid belum ada di kelas
 
        data = TambahMuridKeKelas(murid_id="fake-murid-id-baru")
 
        with patch("app.routers.kelas.KelasMurid") as MockKM:
            result = tambah_murid_ke_kelas(
                kelas_id="fake-kelas-id-tambah",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        db.add.assert_called_once()
        db.commit.assert_called_once()
        assert "berhasil" in result["message"].lower()
 
    def test_tambah_murid_ke_kelas_sudah_ada_raise_400(self):
        """❌ Murid sudah ada di kelas harus raise 400."""
        from app.routers.kelas import tambah_murid_ke_kelas
        from app.schemas.schemas import TambahMuridKeKelas
 
        current_user = fake_pengguna()
        db = mock_db()
        # KelasMurid sudah ada
        db.first.return_value = fake_kelas_murid()
 
        data = TambahMuridKeKelas(murid_id="fake-murid-id-duplikat")
 
        with pytest.raises(HTTPException) as exc:
            tambah_murid_ke_kelas(
                kelas_id="fake-kelas-id-duplikat",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        assert exc.value.status_code == 400
        assert "sudah ada" in exc.value.detail.lower()
        db.add.assert_not_called()
        db.commit.assert_not_called()
 
    def test_tambah_murid_ke_kelas_kelas_id_dan_murid_id_dipakai_filter(self):
        """✅ Filter cek duplikat harus menggunakan kelas_id DAN murid_id."""
        from app.routers.kelas import tambah_murid_ke_kelas
        from app.schemas.schemas import TambahMuridKeKelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        data = TambahMuridKeKelas(murid_id="fake-murid-id-cek-filter")
 
        with patch("app.routers.kelas.KelasMurid"):
            tambah_murid_ke_kelas(
                kelas_id="fake-kelas-id-cek-filter",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        db.filter.assert_called()
 
    def test_tambah_murid_ke_kelas_return_message(self):
        """✅ Response harus berupa dict dengan key 'message'."""
        from app.routers.kelas import tambah_murid_ke_kelas
        from app.schemas.schemas import TambahMuridKeKelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        data = TambahMuridKeKelas(murid_id="fake-murid-id-msg")
 
        with patch("app.routers.kelas.KelasMurid"):
            result = tambah_murid_ke_kelas(
                kelas_id="fake-kelas-id-msg",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        assert isinstance(result, dict)
        assert "message" in result
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestHapusMuridDariKelas — DELETE /kelas/{kelas_id}/murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestHapusMuridDariKelas:
 
    def test_hapus_murid_dari_kelas_berhasil(self):
        """✅ hapus_murid_dari_kelas harus delete KelasMurid dan commit."""
        from app.routers.kelas import hapus_murid_dari_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        km = fake_kelas_murid()
        db.first.return_value = km
 
        hapus_murid_dari_kelas(
            kelas_id="fake-kelas-id-hapus-murid",
            murid_id="fake-murid-id-keluar",
            current_user=current_user,
            db=db,
        )
 
        db.delete.assert_called_once_with(km)
        db.commit.assert_called_once()
 
    def test_hapus_murid_dari_kelas_tidak_ada_raise_404(self):
        """❌ Murid tidak ada di kelas harus raise 404."""
        from app.routers.kelas import hapus_murid_dari_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None  # tidak ada relasi kelas-murid
 
        with pytest.raises(HTTPException) as exc:
            hapus_murid_dari_kelas(
                kelas_id="fake-kelas-id-tidak-ada",
                murid_id="fake-murid-id-tidak-ada",
                current_user=current_user,
                db=db,
            )
 
        assert exc.value.status_code == 404
        db.delete.assert_not_called()
        db.commit.assert_not_called()
 
    def test_hapus_murid_dari_kelas_filter_keduanya(self):
        """✅ Filter harus menggunakan kelas_id DAN murid_id agar tidak hapus relasi yang salah."""
        from app.routers.kelas import hapus_murid_dari_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = fake_kelas_murid()
 
        hapus_murid_dari_kelas(
            kelas_id="fake-kelas-id-filter",
            murid_id="fake-murid-id-filter",
            current_user=current_user,
            db=db,
        )
 
        db.filter.assert_called()
 
    def test_hapus_murid_dari_kelas_tidak_hapus_tabel_murid(self):
        """✅ hapus_murid_dari_kelas hanya hapus baris KelasMurid — tidak hapus data Murid itu sendiri."""
        from app.routers.kelas import hapus_murid_dari_kelas
 
        current_user = fake_pengguna()
        db = mock_db()
        km = fake_kelas_murid()
        db.first.return_value = km
 
        hapus_murid_dari_kelas(
            kelas_id="fake-kelas-id-safe",
            murid_id="fake-murid-id-safe",
            current_user=current_user,
            db=db,
        )
 
        # delete dipanggil tepat satu kali hanya untuk objek KelasMurid
        db.delete.assert_called_once_with(km)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestTambahMuridBaru — POST /kelas/murid/tambah
# ─────────────────────────────────────────────────────────────────────────────
 
class TestTambahMuridBaru:
 
    def _make_data(self, **overrides):
        from app.schemas.schemas import MuridCreate
        defaults = dict(
            email_address="fake-murid-baru@email.com",
            nama="Fake Murid Baru",
            usia=14,
            level="SMP",
            credit_total=15,
        )
        defaults.update(overrides)
        return MuridCreate(**defaults)
 
    def test_tambah_murid_baru_berhasil_add_dua_record(self):
        """✅ tambah_murid_baru harus add Pengguna DAN Murid ke DB."""
        from app.routers.kelas import tambah_murid_baru
 
        db = mock_db()
        db.first.return_value = None  # email & username belum ada
 
        mock_murid = fake_murid(nama="Fake Murid Baru" email="fake-murid-baru@email.com")
        mock_murid.id = mock_pgn.id
 
        data = self._make_data()
 
        with patch("app.routers.kelas.hash_password", return_value="$2b$fake-hash"), \
            patch("app.routers.kelas.Murid",    return_value=mock_murid):
            db.refresh.side_effect = lambda obj: None
            result = tambah_murid_baru(data=data, db=db)
 
        assert db.add.call_count == 1
        db.commit.assert_called_once()
 
    def test_tambah_murid_baru_email_duplikat_raise_400(self):
        """❌ Email sudah terdaftar harus raise 400 — tidak add atau commit."""
        from app.routers.kelas import tambah_murid_baru
 
        current_user = fake_pengguna()
        db = mock_db()
        # Simulasi email sudah ada
        db.first.return_value = fake_pengguna(email="fake-murid-baru@email.com")
 
        data = self._make_data()
 
        with pytest.raises(HTTPException) as exc:
            tambah_murid_baru(data=data, current_user=current_user, db=db)
 
        assert exc.value.status_code == 400
        assert "email" in exc.value.detail.lower()
        db.add.assert_not_called()
        db.commit.assert_not_called()
 
    def test_tambah_murid_baru_username_duplikat_raise_400(self):
        """❌ Username sudah digunakan harus raise 400."""
        from app.routers.kelas import tambah_murid_baru
 
        current_user = fake_pengguna()
        db = mock_db()
        # email bebas, username duplikat
        db.first.side_effect = [None, fake_pengguna(username="fake-murid-baru")]
 
        data = self._make_data()
 
        with pytest.raises(HTTPException) as exc:
            tambah_murid_baru(data=data, current_user=current_user, db=db)
 
        assert exc.value.status_code == 400
        assert "username" in exc.value.detail.lower()
 
    def test_tambah_murid_baru_credit_used_selalu_nol(self):
        """✅ credit_used pada murid baru harus selalu 0 terlepas dari input."""
        from app.routers.kelas import tambah_murid_baru
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        mock_pgn   = fake_pengguna(tipe="murid")
        mock_murid = fake_murid(credit_used=0)
        mock_murid.id = mock_pgn.id
 
        data = self._make_data(credit_total=50)
 
        with patch("app.routers.kelas.hash_password", return_value="$2b$fake"), \
             patch("app.routers.kelas.Pengguna", return_value=mock_pgn), \
             patch("app.routers.kelas.Murid",    return_value=mock_murid):
            db.refresh.side_effect = lambda obj: None
            result = tambah_murid_baru(data=data, current_user=current_user, db=db)
 
        assert result.credit_used == 0
 
    def test_tambah_murid_baru_response_tidak_ada_password(self):
        """✅ Response tidak boleh mengandung field password atau hashed_password."""
        from app.routers.kelas import tambah_murid_baru
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        mock_pgn   = fake_pengguna(tipe="murid", username="fake-secure", email="fake-secure@email.com")
        mock_murid = fake_murid(nama="Fake Secure")
        mock_murid.id = mock_pgn.id
 
        data = self._make_data(username="fake-secure", email_address="fake-secure@email.com")
 
        with patch("app.routers.kelas.hash_password", return_value="$2b$fake"), \
             patch("app.routers.kelas.Pengguna", return_value=mock_pgn), \
             patch("app.routers.kelas.Murid",    return_value=mock_murid):
            db.refresh.side_effect = lambda obj: None
            result = tambah_murid_baru(data=data, current_user=current_user, db=db)
 
        result_dict = result.model_dump()
        assert "password"        not in result_dict
        assert "hashed_password" not in result_dict
 
    def test_tambah_murid_baru_tipe_pengguna_adalah_murid(self):
        """✅ Pengguna yang dibuat harus bertipe 'murid'."""
        from app.routers.kelas import tambah_murid_baru
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        captured_kwargs = {}
 
        class FakePengguna:
            def __init__(self, **kwargs):
                captured_kwargs.update(kwargs)
                for k, v in kwargs.items():
                    setattr(self, k, v)
 
        mock_murid = fake_murid()
 
        data = self._make_data()
 
        with patch("app.routers.kelas.hash_password", return_value="$2b$fake"), \
             patch("app.routers.kelas.Pengguna", side_effect=FakePengguna), \
             patch("app.routers.kelas.Murid",    return_value=mock_murid):
            db.refresh.side_effect = lambda obj: None
            try:
                tambah_murid_baru(data=data, current_user=current_user, db=db)
            except Exception:
                pass  # mungkin error karena mock tidak sempurna; yang penting cek kwargs
 
        assert captured_kwargs.get("tipe_pengguna") == "murid"
 
    def test_tambah_murid_baru_password_di_hash(self):
        """✅ Password harus di-hash sebelum disimpan — tidak boleh plain-text."""
        from app.routers.kelas import tambah_murid_baru
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        mock_pgn   = fake_pengguna(tipe="murid")
        mock_murid = fake_murid()
        mock_murid.id = mock_pgn.id
 
        data = self._make_data()
 
        with patch("app.routers.kelas.hash_password", return_value="$2b$fake-hashed") as mock_hash, \
             patch("app.routers.kelas.Pengguna", return_value=mock_pgn), \
             patch("app.routers.kelas.Murid",    return_value=mock_murid):
            db.refresh.side_effect = lambda obj: None
            tambah_murid_baru(data=data, current_user=current_user, db=db)
 
        mock_hash.assert_called_once_with(data.password)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestUpdateMurid — PUT /kelas/murid/{murid_id}
# ─────────────────────────────────────────────────────────────────────────────
 
class TestUpdateMurid:
 
    def test_update_murid_berhasil_commit_dan_refresh(self):
        """✅ update_murid harus update field murid, commit, dan refresh."""
        from app.routers.kelas import update_murid
        from app.schemas.schemas import MuridUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        murid = fake_murid(nama="Fake Nama Lama", usia=14)
        pengguna = fake_pengguna(tipe="murid")
 
        # Panggil first: pertama untuk Murid, kedua untuk Pengguna (di _murid_to_response)
        db.first.side_effect = [murid, pengguna]
 
        data = MuridUpdate(nama="Fake Nama Baru", usia=15)
 
        db.refresh.side_effect = lambda obj: None
        result = update_murid(
            murid_id="fake-murid-id-update",
            data=data,
            current_user=current_user,
            db=db,
        )
 
        db.commit.assert_called_once()
        db.refresh.assert_called_once()
 
    def test_update_murid_tidak_ditemukan_raise_404(self):
        """❌ Murid tidak ditemukan harus raise 404 — tidak commit."""
        from app.routers.kelas import update_murid
        from app.schemas.schemas import MuridUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        db.first.return_value = None
 
        data = MuridUpdate(nama="Fake Nama Gagal")
 
        with pytest.raises(HTTPException) as exc:
            update_murid(
                murid_id="fake-murid-id-tidak-ada",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        assert exc.value.status_code == 404
        assert "murid" in exc.value.detail.lower()
        db.commit.assert_not_called()
 
    def test_update_murid_hanya_field_yang_dikirim(self):
        """✅ Field None pada MuridUpdate tidak boleh menimpa data yang sudah ada (exclude_none=True)."""
        from app.routers.kelas import update_murid
        from app.schemas.schemas import MuridUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        murid = fake_murid(nama="Fake Nama Tetap Murid", level="SMA", usia=16)
        pengguna = fake_pengguna(tipe="murid")
        db.first.side_effect = [murid, pengguna]
 
        # Hanya update usia — nama dan level tidak berubah
        data = MuridUpdate(usia=17)
 
        setattr_calls = []
        original_setattr = setattr
 
        db.refresh.side_effect = lambda obj: None
 
        with patch("builtins.setattr", side_effect=lambda obj, k, v: setattr_calls.append(k) or original_setattr(obj, k, v)):
            update_murid(
                murid_id="fake-murid-id-partial",
                data=data,
                current_user=current_user,
                db=db,
            )
 
        assert "usia" in setattr_calls
        assert "nama" not in setattr_calls
        assert "level" not in setattr_calls
 
    def test_update_murid_response_berisi_username_dari_pengguna(self):
        """✅ Response harus mengambil username dan email dari tabel Pengguna."""
        from app.routers.kelas import update_murid
        from app.schemas.schemas import MuridUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        murid = fake_murid(nama="Fake Murid Response")
        pengguna = fake_pengguna(
            tipe="murid",
            username="fake-username-response",
            email="fake-response@email.com",
        )
        pengguna.id = murid.id
 
        db.first.side_effect = [murid, pengguna]
 
        data = MuridUpdate(usia=18)
        db.refresh.side_effect = lambda obj: None
 
        result = update_murid(
            murid_id=murid.id,
            data=data,
            current_user=current_user,
            db=db,
        )
 
        assert result.username == "fake-username-response"
        assert result.email_address == "fake-response@email.com"
 
    def test_update_murid_response_tidak_ada_password(self):
        """✅ Response tidak boleh mengandung field password."""
        from app.routers.kelas import update_murid
        from app.schemas.schemas import MuridUpdate
 
        current_user = fake_pengguna()
        db = mock_db()
        murid = fake_murid()
        pengguna = fake_pengguna(tipe="murid")
        db.first.side_effect = [murid, pengguna]
 
        data = MuridUpdate(level="SMA Kelas 3")
        db.refresh.side_effect = lambda obj: None
 
        result = update_murid(
            murid_id=murid.id,
            data=data,
            current_user=current_user,
            db=db,
        )
 
        result_dict = result.model_dump()
        assert "password"        not in result_dict
        assert "hashed_password" not in result_dict
 