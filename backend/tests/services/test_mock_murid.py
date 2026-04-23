"""
test_mock_murid.py
─────────────────────────────────────────────────────────────────────────────
Pure mock unit test untuk app/services/murid_service.py
Tidak butuh database, tidak butuh .env.

Cara jalankan:
    pytest tests/test_mock_murid.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
from unittest.mock import MagicMock, patch
from tests.test_helpers import fake_id, fake_pengguna, fake_murid, mock_db
import pytest
from fastapi import HTTPException

# ═════════════════════════════════════════════════════════════════════════════
# TEST CREATE MURID
# ═════════════════════════════════════════════════════════════════════════════

class TestCreateMurid:

    def test_create_murid_berhasil(self):
        """✅ create_murid harus add Pengguna + Murid ke DB lalu commit."""
        from app.services.murid_service import create_murid
        from app.schemas.schemas import MuridCreate

        db = mock_db()
        db.first.return_value = None  # email & username belum ada

        mock_murid_obj = fake_murid(nama="Fake Budi Santoso", email="fake-budi@email.com")

        data = MuridCreate(
            email_address="fake-budi@email.com",
            nama="Fake Budi Santoso",
            usia=15,
            level="SMA Kelas 1",
            credit_total=20,
        )

        with patch("app.services.murid_service.hash_password", return_value="$2b$fake"), \
            patch("app.services.murid_service.Murid",    return_value=mock_murid_obj):
            db.refresh.side_effect = lambda obj: None
            result = create_murid(db, data)

        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_create_murid_email_duplikat_raise_400(self):
        """❌ Email sudah ada harus raise 400, tidak commit."""
        from app.services.murid_service import create_murid
        from app.schemas.schemas import MuridCreate

        db = mock_db()
        db.first.return_value = fake_murid(email="fake-duplikat@email.com")

        data = MuridCreate(
            email_address="fake-duplikat@email.com",
            nama="Fake Nama",
        )

        with pytest.raises(HTTPException) as exc:
            create_murid(db, data)

        assert exc.value.status_code == 400
        assert "email" in exc.value.detail.lower()
        db.commit.assert_not_called()


    def test_create_murid_credit_used_selalu_nol(self):
        """✅ Murid baru harus selalu punya credit_used = 0."""
        from app.services.murid_service import create_murid
        from app.schemas.schemas import MuridCreate

        db = mock_db()
        db.first.return_value = None

        mock_murid_obj = fake_murid()
        mock_murid_obj.credit_used = 0

        data = MuridCreate(
            username="fake-zero-credit",
            email_address="fake-zero@email.com",
            password="Fake-Pass-123!",
            nama="Fake Zero Credit",
            credit_total=30,
        )

        with patch("app.services.murid_service.hash_password", return_value="$2b$fake"), \
             patch("app.services.murid_service.Murid",    return_value=mock_murid_obj):
            db.refresh.side_effect = lambda obj: None
            result = create_murid(db, data)

        assert result.credit_used == 0


# ═════════════════════════════════════════════════════════════════════════════
# TEST GET ALL MURID
# ═════════════════════════════════════════════════════════════════════════════

class TestGetAllMurid:

    def test_get_all_murid_return_semua(self):
        """✅ get_all_murid harus mengembalikan semua murid aktif."""
        from app.services.murid_service import get_all_murid

        db = mock_db()
        murid1 = fake_murid(nama="Fake Andi", email="fake-andi@email.com")
        murid2 = fake_murid(nama="Fake Budi", email="fake-budi@email.com")
        murid3 = fake_murid(nama="Fake Citra", email="fake-citra@email.com")
        db.all.return_value = [murid1, murid2, murid3]

        result = get_all_murid(db)

        assert len(result) == 3
        assert result[0].nama == "Fake Andi"
        assert result[1].nama == "Fake Budi"
        assert result[2].nama == "Fake Citra"

    def test_get_all_murid_kosong_return_list_kosong(self):
        """✅ Jika tidak ada murid, harus return list kosong."""
        from app.services.murid_service import get_all_murid

        db = mock_db()
        db.all.return_value = []

        result = get_all_murid(db)

        assert result == []

    def test_get_all_murid_dengan_search_filter_nama(self):
        """✅ Parameter search harus memfilter berdasarkan nama."""
        from app.services.murid_service import get_all_murid

        db = mock_db()
        murid = fake_murid(nama="Fake Andi Searching")
        db.all.return_value = [(murid)]

        result = get_all_murid(db, search="Andi")

        # filter harus dipanggil (untuk nama ilike)
        assert db.filter.called
        assert len(result) == 1
        assert result[0].nama == "Fake Andi Searching"

    def test_get_all_murid_paginasi_skip_limit(self):
        """✅ Parameter skip dan limit harus diteruskan ke query."""
        from app.services.murid_service import get_all_murid

        db = mock_db()
        db.all.return_value = []

        get_all_murid(db, skip=10, limit=5)

        db.offset.assert_called_with(10)
        db.limit.assert_called_with(5)


# ═════════════════════════════════════════════════════════════════════════════
# TEST GET MURID BY ID
# ═════════════════════════════════════════════════════════════════════════════

class TestGetMuridById:

    def test_get_murid_by_id_berhasil(self):
        """✅ Murid ditemukan harus return MuridResponse dengan data yang benar."""
        from app.services.murid_service import get_murid_by_id

        murid_id = fake_id()
        db = mock_db()

        m = fake_murid(nama="Fake Detail Murid",  email="fake-detail@email.com",  is_active=True)
        m.id = murid_id

        db.first.side_effect = [m]

        result = get_murid_by_id(db, murid_id)

        assert result.nama  == "Fake Detail Murid"
        assert result.id    == murid_id

    def test_get_murid_by_id_tidak_ada_raise_404(self):
        """❌ Murid tidak ditemukan harus raise 404."""
        from app.services.murid_service import get_murid_by_id

        db = mock_db()
        db.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            get_murid_by_id(db, "fake-id-tidak-ada")

        assert exc.value.status_code == 404

    def test_get_murid_nonaktif_raise_404(self):
        """❌ Murid dengan is_active=False harus raise 404."""
        from app.services.murid_service import get_murid_by_id

        db = mock_db()
        murid = fake_murid(is_active=False)
        db.first.side_effect = [murid]

        with pytest.raises(HTTPException) as exc:
            get_murid_by_id(db, murid.id)

        assert exc.value.status_code == 404


# ═════════════════════════════════════════════════════════════════════════════
# TEST DELETE MURID
# ═════════════════════════════════════════════════════════════════════════════

class TestDeleteMurid:
    def test_delete_murid_tidak_ada_raise_404(self):
        """❌ Murid tidak ditemukan harus raise 404, tidak hapus apapun."""
        from app.services.murid_service import delete_murid

        db = mock_db()
        db.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            delete_murid(db, "fake-id-tidak-ada")

        assert exc.value.status_code == 404
        db.delete.assert_not_called()
        db.commit.assert_not_called()

    def test_delete_pengajar_via_endpoint_murid_raise_404(self):
        """❌ Tidak bisa hapus pengajar via delete_murid — harus raise 404."""
        from app.services.murid_service import delete_murid

        db = mock_db()
        pengajar = fake_pengguna(tipe="pengajar")  # bukan murid
        db.first.return_value = pengajar

        with pytest.raises(HTTPException) as exc:
            delete_murid(db, pengajar.id)

        assert exc.value.status_code == 404
        db.delete.assert_not_called()
