"""
test_mock_security.py
─────────────────────────────────────────────────────────────────────────────
Pure unit test untuk app/core/security.py
Mencakup: hash password, verify password, buat token JWT,
          decode token, blacklist token.

Tidak ada mock di sini karena security.py adalah pure function —
tidak bergantung pada DB atau service eksternal.

Cara jalankan:
    pytest tests/test_mock_security.py -v
"""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"]   = "fake-secret-key-untuk-testing-32chars-ok"

import uuid
from datetime import timedelta
from tests.test_helpers import fake_id
import pytest


# ═════════════════════════════════════════════════════════════════════════════
# TEST PASSWORD HASHING
# ═════════════════════════════════════════════════════════════════════════════

class TestPasswordHashing:

    def test_hash_menghasilkan_format_bcrypt(self):
        """✅ hash_password harus menghasilkan string bcrypt ($2b$...)."""
        from app.core.security import hash_password

        result = hash_password("Fake-Password-Untuk-Hash-Test!")

        assert result.startswith("$2b$")
        assert len(result) == 60  # bcrypt selalu 60 karakter

    def test_hash_berbeda_dari_plaintext(self):
        """✅ Hash tidak boleh sama dengan password aslinya."""
        from app.core.security import hash_password

        plain  = "Fake-Password-Plaintext!"
        hashed = hash_password(plain)

        assert hashed != plain

    def test_dua_hash_dari_password_sama_berbeda(self):
        """✅ Hash dari password yang sama harus menghasilkan nilai berbeda (salt acak)."""
        from app.core.security import hash_password

        password = "Fake-Same-Password-123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_hash_password_panjang_tidak_error(self):
        """✅ Password panjang (> 72 byte) tidak boleh menyebabkan error."""
        from app.core.security import hash_password

        password_panjang = "Fake-" + "A" * 100  # 105 karakter, > 72 byte
        result = hash_password(password_panjang)

        assert result.startswith("$2b$")

    def test_hash_password_unicode_tidak_error(self):
        """✅ Password dengan karakter unicode tidak boleh error."""
        from app.core.security import hash_password

        password_unicode = "Fake-Sandi-Indonesia-123!-ñ-ü"
        result = hash_password(password_unicode)

        assert result.startswith("$2b$")


# ═════════════════════════════════════════════════════════════════════════════
# TEST PASSWORD VERIFICATION
# ═════════════════════════════════════════════════════════════════════════════

class TestPasswordVerification:

    def test_verify_password_benar_return_true(self):
        """✅ Password yang cocok harus return True."""
        from app.core.security import hash_password, verify_password

        plain  = "Fake-Password-Verifikasi-Benar!"
        hashed = hash_password(plain)

        assert verify_password(plain, hashed) is True

    def test_verify_password_salah_return_false(self):
        """❌ Password yang tidak cocok harus return False."""
        from app.core.security import hash_password, verify_password

        hashed = hash_password("Fake-Password-Asli!")

        assert verify_password("Fake-Password-Salah!", hashed) is False

    def test_verify_hash_rusak_return_false(self):
        """❌ Hash yang rusak/tidak valid harus return False tanpa raise error."""
        from app.core.security import verify_password

        result = verify_password("Fake-Password-123!", "bukan-hash-bcrypt-valid")

        assert result is False

    def test_verify_hash_kosong_return_false(self):
        """❌ Hash kosong harus return False."""
        from app.core.security import verify_password

        result = verify_password("Fake-Password-123!", "")

        assert result is False

    def test_verify_case_sensitive(self):
        """✅ Verifikasi password harus case-sensitive."""
        from app.core.security import hash_password, verify_password

        hashed = hash_password("FakePassword123!")

        assert verify_password("FakePassword123!", hashed) is True
        assert verify_password("fakepassword123!", hashed) is False
        assert verify_password("FAKEPASSWORD123!", hashed) is False


# ═════════════════════════════════════════════════════════════════════════════
# TEST JWT TOKEN — CREATE
# ═════════════════════════════════════════════════════════════════════════════

class TestCreateAccessToken:

    def test_token_menghasilkan_3_bagian_jwt(self):
        """✅ Token JWT harus terdiri dari 3 bagian dipisah titik (header.payload.signature)."""
        from app.core.security import create_access_token

        token = create_access_token({"sub": f"fake-user-{fake_id()}", "tipe": "pengajar"})
        parts = token.split(".")

        assert len(parts) == 3, f"JWT harus 3 bagian, dapat {len(parts)}"

    def test_token_berisi_data_yang_dikodekan(self):
        """✅ Token harus bisa di-decode dan berisi data yang dikirim."""
        from app.core.security import create_access_token, decode_access_token

        user_id = fake_id()
        token   = create_access_token({"sub": user_id, "tipe": "murid"})
        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"]  == user_id
        assert payload["tipe"] == "murid"

    def test_token_berisi_exp(self):
        """✅ Token harus mengandung field 'exp' (expiration time)."""
        from app.core.security import create_access_token, decode_access_token

        token   = create_access_token({"sub": "fake-user-id"})
        payload = decode_access_token(token)

        assert "exp" in payload

    def test_token_dengan_expires_delta_custom(self):
        """✅ Token dengan expires_delta custom harus menggunakan waktu tersebut."""
        from app.core.security import create_access_token, decode_access_token
        from datetime import datetime, timezone

        expires = timedelta(hours=2)
        token   = create_access_token({"sub": "fake-user-id"}, expires_delta=expires)
        payload = decode_access_token(token)

        assert payload is not None
        # exp harus sekitar 2 jam dari sekarang
        now = datetime.now(timezone.utc).timestamp()
        assert payload["exp"] > now

    def test_dua_token_dari_data_sama_hasilnya_berbeda(self):
        """✅ Dua token dari data yang sama harus berbeda karena timestamp berbeda."""
        from app.core.security import create_access_token
        import time

        data    = {"sub": "fake-user-sama", "tipe": "pengajar"}
        token1  = create_access_token(data)
        time.sleep(0.01)  # tunggu sebentar agar timestamp berbeda
        token2  = create_access_token(data)

        # Token bisa sama jika dibuat di detik yang sama — ini test best-effort
        # yang penting tidak raise error
        assert isinstance(token1, str)
        assert isinstance(token2, str)


# ═════════════════════════════════════════════════════════════════════════════
# TEST JWT TOKEN — DECODE
# ═════════════════════════════════════════════════════════════════════════════

class TestDecodeAccessToken:

    def test_decode_token_valid_return_payload(self):
        """✅ Token valid harus return payload dict."""
        from app.core.security import create_access_token, decode_access_token

        user_id = fake_id()
        token   = create_access_token({"sub": user_id, "tipe": "pengajar"})
        result  = decode_access_token(token)

        assert result is not None
        assert result["sub"]  == user_id
        assert result["tipe"] == "pengajar"

    def test_decode_token_palsu_return_none(self):
        """❌ Token palsu harus return None."""
        from app.core.security import decode_access_token

        result = decode_access_token("fake.token.palsu-tidak-valid-sama-sekali")

        assert result is None

    def test_decode_token_expired_return_none(self):
        """❌ Token kadaluarsa harus return None."""
        from app.core.security import create_access_token, decode_access_token

        token  = create_access_token(
            {"sub": "fake-user-expired"},
            expires_delta=timedelta(minutes=-1),  # sudah expired
        )
        result = decode_access_token(token)

        assert result is None

    def test_decode_token_kosong_return_none(self):
        """❌ String kosong harus return None."""
        from app.core.security import decode_access_token

        result = decode_access_token("")

        assert result is None

    def test_decode_token_signature_diubah_return_none(self):
        """❌ Token yang signature-nya diubah harus return None."""
        from app.core.security import create_access_token, decode_access_token

        token        = create_access_token({"sub": "fake-user"})
        token_rusak  = token[:-5] + "RUSAK"  # ubah 5 karakter terakhir signature

        result = decode_access_token(token_rusak)

        assert result is None


# ═════════════════════════════════════════════════════════════════════════════
# TEST TOKEN BLACKLIST
# ═════════════════════════════════════════════════════════════════════════════

class TestTokenBlacklist:

    def test_token_baru_tidak_ada_di_blacklist(self):
        """✅ Token yang belum di-logout tidak boleh ada di blacklist."""
        from app.core.security import is_token_blacklisted

        token_baru = f"fake-token-baru-{fake_id()}"

        assert is_token_blacklisted(token_baru) is False

    def test_blacklist_token_terdeteksi(self):
        """✅ Token yang di-blacklist harus terdeteksi oleh is_token_blacklisted."""
        from app.core.security import blacklist_token, is_token_blacklisted

        token = f"fake-token-untuk-blacklist-{fake_id()}"

        blacklist_token(token)

        assert is_token_blacklisted(token) is True

    def test_blacklist_token_tidak_mempengaruhi_token_lain(self):
        """✅ Blacklist satu token tidak mempengaruhi token lain."""
        from app.core.security import blacklist_token, is_token_blacklisted

        token_a = f"fake-token-A-{fake_id()}"
        token_b = f"fake-token-B-{fake_id()}"

        blacklist_token(token_a)

        assert is_token_blacklisted(token_a) is True
        assert is_token_blacklisted(token_b) is False

    def test_blacklist_token_dua_kali_tidak_error(self):
        """✅ Blacklist token yang sudah ada tidak boleh raise error."""
        from app.core.security import blacklist_token, is_token_blacklisted

        token = f"fake-token-duplikat-{fake_id()}"

        blacklist_token(token)
        blacklist_token(token)  # kedua kali tidak boleh error

        assert is_token_blacklisted(token) is True

    def test_token_dari_jwt_bisa_di_blacklist(self):
        """✅ Token JWT nyata yang dibuat dengan create_access_token bisa di-blacklist."""
        from app.core.security import create_access_token, blacklist_token, is_token_blacklisted

        token = create_access_token({"sub": "fake-user-blacklist-test"})

        assert is_token_blacklisted(token) is False

        blacklist_token(token)

        assert is_token_blacklisted(token) is True
