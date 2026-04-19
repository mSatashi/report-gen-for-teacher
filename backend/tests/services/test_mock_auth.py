"""
test_mock_auth.py
─────────────────────────────────────────────────────────────────────────────
Pure mock unit test untuk app/services/auth_service.py
Tidak butuh database, tidak butuh .env, tidak butuh server nyata.

Cara jalankan:
    pytest tests/test_mock_auth.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch
from tests.test_helpers import fake_id, fake_pengguna, mock_db

import pytest
from fastapi import HTTPException

# ═════════════════════════════════════════════════════════════════════════════
# TEST REGISTER
# ═════════════════════════════════════════════════════════════════════════════

class TestRegisterUser:

    def test_register_pengajar_berhasil(self):
        """✅ register_user pengajar harus add 2 record (Pengguna + Pengajar) lalu commit."""
        from app.services.auth_service import register_user
        from app.schemas.schemas import RegisterRequest

        db = mock_db()
        db.first.return_value = None  # email & username belum ada

        data = RegisterRequest(
            username="fake-guru-baru",
            email_address="fake-guru-baru@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="pengajar",
        )

        with patch("app.services.auth_service.hash_password", return_value="$2b$fake"):
            register_user(db, data)

        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_register_murid_berhasil(self):
        """✅ register_user murid harus add 2 record (Pengguna + Murid) lalu commit."""
        from app.services.auth_service import register_user
        from app.schemas.schemas import RegisterRequest

        db = mock_db()
        db.first.return_value = None

        data = RegisterRequest(
            username="fake-murid-baru",
            email_address="fake-murid-baru@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="murid",
        )

        with patch("app.services.auth_service.hash_password", return_value="$2b$fake"):
            register_user(db, data)

        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_register_email_duplikat_raise_400(self):
        """❌ Email sudah ada harus raise HTTPException 400, DB tidak di-commit."""
        from app.services.auth_service import register_user
        from app.schemas.schemas import RegisterRequest

        db = mock_db()
        db.first.return_value = fake_pengguna(email="fake-duplikat@email.com")

        data = RegisterRequest(
            username="fake-username-baru",
            email_address="fake-duplikat@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="pengajar",
        )

        with pytest.raises(HTTPException) as exc:
            register_user(db, data)

        assert exc.value.status_code == 400
        assert "email" in exc.value.detail.lower()
        db.commit.assert_not_called()

    def test_register_username_duplikat_raise_400(self):
        """❌ Username sudah ada harus raise HTTPException 400."""
        from app.services.auth_service import register_user
        from app.schemas.schemas import RegisterRequest

        db = mock_db()
        # Panggil pertama (cek email) → None, kedua (cek username) → ada
        db.first.side_effect = [None, fake_pengguna(username="fake-username-duplikat")]

        data = RegisterRequest(
            username="fake-username-duplikat",
            email_address="fake-email-baru@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="pengajar",
        )

        with pytest.raises(HTTPException) as exc:
            register_user(db, data)

        assert exc.value.status_code == 400
        assert "username" in exc.value.detail.lower()
        db.commit.assert_not_called()


# ═════════════════════════════════════════════════════════════════════════════
# TEST LOGIN
# ═════════════════════════════════════════════════════════════════════════════

class TestLoginUser:

    def test_login_berhasil_return_token(self):
        """✅ Login benar harus return TokenResponse dengan access_token."""
        from app.services.auth_service import login_user
        from app.schemas.schemas import LoginRequest

        db = mock_db()
        pengguna = fake_pengguna(tipe="pengajar", is_active=True)
        db.first.return_value = pengguna

        data = LoginRequest(
            email_address="fake-guru@email.com",
            password="Fake-Pass-Benar-123!",
        )

        with patch("app.services.auth_service.verify_password", return_value=True), \
             patch("app.services.auth_service.create_access_token", return_value="fake-jwt-token"):
            result = login_user(db, data)

        assert result.access_token  == "fake-jwt-token"
        assert result.tipe_pengguna == "pengajar"
        assert result.user_id       == pengguna.id
        assert result.token_type    == "bearer"

    def test_login_murid_return_tipe_murid(self):
        """✅ Login murid harus return tipe_pengguna = 'murid'."""
        from app.services.auth_service import login_user
        from app.schemas.schemas import LoginRequest

        db = mock_db()
        db.first.return_value = fake_pengguna(tipe="murid", is_active=True)

        data = LoginRequest(
            email_address="fake-murid@email.com",
            password="Fake-Pass-Benar-123!",
        )

        with patch("app.services.auth_service.verify_password", return_value=True), \
             patch("app.services.auth_service.create_access_token", return_value="fake-jwt-murid"):
            result = login_user(db, data)

        assert result.tipe_pengguna == "murid"

    def test_login_password_salah_raise_401(self):
        """❌ Password salah harus raise 401."""
        from app.services.auth_service import login_user
        from app.schemas.schemas import LoginRequest

        db = mock_db()
        db.first.return_value = fake_pengguna(is_active=True)

        data = LoginRequest(
            email_address="fake-guru@email.com",
            password="Fake-Pass-SALAH!",
        )

        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc:
                login_user(db, data)

        assert exc.value.status_code == 401

    def test_login_user_tidak_ada_raise_401(self):
        """❌ Email tidak ditemukan harus raise 401."""
        from app.services.auth_service import login_user
        from app.schemas.schemas import LoginRequest

        db = mock_db()
        db.first.return_value = None  # tidak ada user

        data = LoginRequest(
            email_address="fake-tidak-ada@email.com",
            password="Fake-Pass-123!",
        )

        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc:
                login_user(db, data)

        assert exc.value.status_code == 401

    def test_login_akun_nonaktif_raise_403(self):
        """❌ Akun is_active=False harus raise 403."""
        from app.services.auth_service import login_user
        from app.schemas.schemas import LoginRequest

        db = mock_db()
        db.first.return_value = fake_pengguna(is_active=False)

        data = LoginRequest(
            email_address="fake-nonaktif@email.com",
            password="Fake-Pass-123!",
        )

        with patch("app.services.auth_service.verify_password", return_value=True):
            with pytest.raises(HTTPException) as exc:
                login_user(db, data)

        assert exc.value.status_code == 403


# ═════════════════════════════════════════════════════════════════════════════
# TEST LOGOUT
# ═════════════════════════════════════════════════════════════════════════════

class TestLogoutUser:

    def test_logout_memanggil_blacklist_token(self):
        """✅ logout_user harus memanggil blacklist_token dengan token yang diberikan."""
        from app.services.auth_service import logout_user

        fake_token = f"fake-token-{fake_id()}"

        with patch("app.services.auth_service.blacklist_token") as mock_bl:
            result = logout_user(fake_token)

        mock_bl.assert_called_once_with(fake_token)

    def test_logout_return_pesan_sukses(self):
        """✅ logout_user harus return dict berisi 'message'."""
        from app.services.auth_service import logout_user

        with patch("app.services.auth_service.blacklist_token"):
            result = logout_user("fake-token-apapun")

        assert "message" in result
        assert "logout" in result["message"].lower()


# ═════════════════════════════════════════════════════════════════════════════
# TEST REQUIRE PENGAJAR
# ═════════════════════════════════════════════════════════════════════════════

class TestRequirePengajar:

    def test_pengajar_lolos(self):
        """✅ Pengguna tipe 'pengajar' harus lolos require_pengajar."""
        from app.services.auth_service import require_pengajar

        pengajar = fake_pengguna(tipe="pengajar")
        result   = require_pengajar(current_user=pengajar)

        assert result == pengajar

    def test_murid_raise_403(self):
        """❌ Pengguna tipe 'murid' harus raise 403."""
        from app.services.auth_service import require_pengajar

        murid = fake_pengguna(tipe="murid")

        with pytest.raises(HTTPException) as exc:
            require_pengajar(current_user=murid)

        assert exc.value.status_code == 403
