import { apiFetch } from "./apiFetch";
import type { PenggunaPayload, PenggunaResponse } from "./payload";

/** Validate password strength */
function validatePassword(password: string): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!password) {
    errors.push("Password tidak boleh kosong");
  } else {
    // Check minimum length
    if (password.length < 10) {
      errors.push("Password minimal 10 karakter");
    }

    // Check for uppercase letter
    if (!/[A-Z]/.test(password)) {
      errors.push("Password harus mengandung minimal 1 huruf besar");
    }

    // Check for lowercase letter
    if (!/[a-z]/.test(password)) {
      errors.push("Password harus mengandung minimal 1 huruf kecil");
    }

    // Check for number
    if (!/[0-9]/.test(password)) {
      errors.push("Password harus mengandung minimal 1 angka");
    }

    // Check for special character
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      errors.push("Password harus mengandung minimal 1 karakter spesial (!@#$%^&* dll)");
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/** GET /admin/list-pengajar — ambil semua data pengguna */
export async function fetchPenggunaList(): Promise<PenggunaResponse[]> {
  const res = await apiFetch(`/admin/list-pengajar`);
  if (!res.ok) throw new Error(`Gagal memuat data pengguna (${res.status})`);
  return res.json();
}

/** POST /admin/tambah-pengajar — buat pengguna baru */
export async function createPengguna(payload: PenggunaPayload): Promise<PenggunaResponse> {
  // Validate password before making API call
  const passwordValidation = validatePassword(payload.password);
  if (!passwordValidation.valid) {
    throw new Error(`Password tidak valid: ${passwordValidation.errors.join(", ")}`);
  }

  const res = await apiFetch(`/admin/tambah-pengajar`, {
    method: "POST",
    body: JSON.stringify({
      username: payload.username,
      email_address: payload.email_address,
      tipe_pengguna: "pengajar",
      password: payload.password,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat pengguna (${res.status})`);
  }
  return res.json();
}

/** DELETE /admin/hapus-pengajar/:id — hapus pengguna */
export async function deletePenggunaApi(id: string): Promise<void> {
  const res = await apiFetch(`/admin/hapus-pengajar/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Gagal menghapus pengguna (${res.status})`);
}