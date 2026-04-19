import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"
 
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
 
from tests.test_helpers import fake_id, fake_pengguna, mock_db
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestRouterRegister — POST /auth/register
# ─────────────────────────────────────────────────────────────────────────────
 
class TestRouterRegister:
 
    def test_register_pengajar_return_message_dan_user_id(self):
        """✅ Register pengajar berhasil harus return dict dengan message, user_id, tipe."""
        from app.routers.auth import register
        from app.schemas.schemas import RegisterRequest
 
        db = mock_db()
        mock_user = fake_pengguna(tipe="pengajar", uid=fake_id())
 
        data = RegisterRequest(
            username="fake-guru-register",
            email_address="fake-guru-register@email.com",
            password="Fake-Pass-Guru-123!",
            tipe_pengguna="pengajar",
        )
 
        with patch("app.routers.auth.register_user", return_value=mock_user) as mock_reg:
            result = register(data=data, db=db)
 
        mock_reg.assert_called_once_with(db, data)
        assert "message" in result
        assert "user_id" in result
        assert result["user_id"] == mock_user.id
        assert result["tipe"] == "pengajar"
 
    def test_register_murid_return_tipe_murid(self):
        """✅ Register murid berhasil harus return tipe = 'murid'."""
        from app.routers.auth import register
        from app.schemas.schemas import RegisterRequest
 
        db = mock_db()
        mock_user = fake_pengguna(tipe="murid")
 
        data = RegisterRequest(
            username="fake-murid-register",
            email_address="fake-murid-register@email.com",
            password="Fake-Pass-Murid-123!",
            tipe_pengguna="murid",
        )
 
        with patch("app.routers.auth.register_user", return_value=mock_user):
            result = register(data=data, db=db)
 
        assert result["tipe"] == "murid"
 
    def test_register_email_duplikat_propagate_400(self):
        """❌ register_user raise 400 → router harus meneruskan exception tersebut."""
        from app.routers.auth import register
        from app.schemas.schemas import RegisterRequest
 
        db = mock_db()
 
        data = RegisterRequest(
            username="fake-duplikat-user",
            email_address="fake-duplikat@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="pengajar",
        )
 
        with patch("app.routers.auth.register_user",
                   side_effect=HTTPException(status_code=400, detail="Email sudah terdaftar")):
            with pytest.raises(HTTPException) as exc:
                register(data=data, db=db)
 
        assert exc.value.status_code == 400
        assert "email" in exc.value.detail.lower()
 
    def test_register_username_duplikat_propagate_400(self):
        """❌ Username sudah ada → router meneruskan HTTPException 400."""
        from app.routers.auth import register
        from app.schemas.schemas import RegisterRequest
 
        db = mock_db()
        data = RegisterRequest(
            username="fake-username-duplikat",
            email_address="fake-baru@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="pengajar",
        )
 
        with patch("app.routers.auth.register_user",
                   side_effect=HTTPException(status_code=400, detail="Username sudah digunakan")):
            with pytest.raises(HTTPException) as exc:
                register(data=data, db=db)
 
        assert exc.value.status_code == 400
        assert "username" in exc.value.detail.lower()
 
    def test_register_response_tidak_mengandung_password(self):
        """✅ Response register tidak boleh mengandung field password apapun."""
        from app.routers.auth import register
        from app.schemas.schemas import RegisterRequest
 
        db = mock_db()
        mock_user = fake_pengguna(tipe="pengajar")
 
        data = RegisterRequest(
            username="fake-aman-user",
            email_address="fake-aman@email.com",
            password="Fake-Super-Secret-Pass!",
            tipe_pengguna="pengajar",
        )
 
        with patch("app.routers.auth.register_user", return_value=mock_user):
            result = register(data=data, db=db)
 
        assert "password"        not in result
        assert "hashed_password" not in result
 
    def test_register_memanggil_service_dengan_data_dan_db(self):
        """✅ Router harus meneruskan data dan db ke register_user service."""
        from app.routers.auth import register
        from app.schemas.schemas import RegisterRequest
 
        db = mock_db()
        mock_user = fake_pengguna()
        data = RegisterRequest(
            username="fake-passthrough-user",
            email_address="fake-passthrough@email.com",
            password="Fake-Pass-123!",
            tipe_pengguna="pengajar",
        )
 
        with patch("app.routers.auth.register_user", return_value=mock_user) as mock_svc:
            register(data=data, db=db)
 
        mock_svc.assert_called_once_with(db, data)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestRouterLogin — POST /auth/login
# ─────────────────────────────────────────────────────────────────────────────
 
class TestRouterLogin:
 
    def _make_login_data(self, email="fake-login@email.com", password="Fake-Pass-Login-123!"):
        from app.schemas.schemas import LoginRequest
        return LoginRequest(email_address=email, password=password)
 
    def _make_token_response(self, tipe="pengajar"):
        from app.schemas.schemas import TokenResponse
        return TokenResponse(
            access_token=f"fake-jwt-token-{fake_id()}",
            token_type="bearer",
            tipe_pengguna=tipe,
            user_id=fake_id(),
        )
 
    def test_login_berhasil_return_token_response(self):
        """✅ Login berhasil harus return TokenResponse dari service."""
        from app.routers.auth import login
 
        db = mock_db()
        token_resp = self._make_token_response(tipe="pengajar")
        data = self._make_login_data()
 
        with patch("app.routers.auth.login_user", return_value=token_resp) as mock_login:
            result = login(data=data, db=db)
 
        mock_login.assert_called_once_with(db, data)
        assert result == token_resp
        assert result.access_token.startswith("fake-jwt-token-")
        assert result.tipe_pengguna == "pengajar"
 
    def test_login_murid_return_tipe_murid(self):
        """✅ Login murid harus mengembalikan tipe_pengguna = 'murid'."""
        from app.routers.auth import login
 
        db = mock_db()
        token_resp = self._make_token_response(tipe="murid")
        data = self._make_login_data(email="fake-murid-login@email.com")
 
        with patch("app.routers.auth.login_user", return_value=token_resp):
            result = login(data=data, db=db)
 
        assert result.tipe_pengguna == "murid"
 
    def test_login_password_salah_propagate_401(self):
        """❌ Password salah → router meneruskan HTTPException 401."""
        from app.routers.auth import login
 
        db = mock_db()
        data = self._make_login_data(password="Fake-Pass-SALAH!")
 
        with patch("app.routers.auth.login_user",
                   side_effect=HTTPException(status_code=401, detail="Email atau password salah")):
            with pytest.raises(HTTPException) as exc:
                login(data=data, db=db)
 
        assert exc.value.status_code == 401
 
    def test_login_akun_nonaktif_propagate_403(self):
        """❌ Akun nonaktif → router meneruskan HTTPException 403."""
        from app.routers.auth import login
 
        db = mock_db()
        data = self._make_login_data(email="fake-nonaktif@email.com")
 
        with patch("app.routers.auth.login_user",
                   side_effect=HTTPException(status_code=403, detail="Akun tidak aktif")):
            with pytest.raises(HTTPException) as exc:
                login(data=data, db=db)
 
        assert exc.value.status_code == 403
 
    def test_login_token_type_adalah_bearer(self):
        """✅ token_type pada response harus 'bearer'."""
        from app.routers.auth import login
 
        db = mock_db()
        token_resp = self._make_token_response()
        data = self._make_login_data()
 
        with patch("app.routers.auth.login_user", return_value=token_resp):
            result = login(data=data, db=db)
 
        assert result.token_type == "bearer"
 
 
# ─────────────────────────────────────────────────────────────────────────────
# TestRouterLogout — POST /auth/logout
# ─────────────────────────────────────────────────────────────────────────────
 
class TestRouterLogout:
 
    def _make_credentials(self, token: str = None):
        cred = MagicMock()
        cred.credentials = token or f"fake-jwt-token-logout-{fake_id()}"
        return cred
 
    def test_logout_berhasil_memanggil_logout_user(self):
        """✅ logout harus memanggil logout_user dengan token dari credentials."""
        from app.routers.auth import logout
 
        cred = self._make_credentials("fake-token-logout-valid")
 
        with patch("app.routers.auth.logout_user", return_value={"message": "Logout berhasil."}) as mock_lo:
            result = logout(credentials=cred)
 
        mock_lo.assert_called_once_with("fake-token-logout-valid")
 
    def test_logout_return_message(self):
        """✅ logout harus mengembalikan dict dengan key 'message'."""
        from app.routers.auth import logout
 
        cred = self._make_credentials()
 
        with patch("app.routers.auth.logout_user", return_value={"message": "Logout berhasil. Token telah dinonaktifkan."}):
            result = logout(credentials=cred)
 
        assert "message" in result
        assert "logout" in result["message"].lower()
 
    def test_logout_token_diteruskan_dari_credentials(self):
        """✅ Token yang diteruskan ke logout_user harus berasal dari credentials.credentials."""
        from app.routers.auth import logout
 
        target_token = f"fake-bearer-token-{fake_id()}"
        cred = self._make_credentials(target_token)
 
        passed_token = []
 
        def capture_token(token):
            passed_token.append(token)
            return {"message": "Logout berhasil."}
 
        with patch("app.routers.auth.logout_user", side_effect=capture_token):
            logout(credentials=cred)
 
        assert passed_token[0] == target_token
 
    def test_logout_tidak_butuh_db(self):
        """✅ Endpoint logout tidak memerlukan database (JWT stateless)."""
        from app.routers.auth import logout
        import inspect
 
        sig = inspect.signature(logout)
        # Pastikan tidak ada parameter 'db' di signature logout
        assert "db" not in sig.parameters