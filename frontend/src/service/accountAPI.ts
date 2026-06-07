import { apiFetch } from "./apiFetch";
import type { PenggunaPayload, PenggunaResponse } from "./payload";

/** GET /admin/list-pengajar — ambil semua data pengguna */
export async function fetchPenggunaList(): Promise<PenggunaResponse[]> {
  const res = await apiFetch(`/admin/list-pengajar`);
  if (!res.ok) throw new Error(`Gagal memuat data pengguna (${res.status})`);
  return res.json();
}

/** POST /admin/tambah-pengajar — buat pengguna baru */
export async function createPengguna(payload: PenggunaPayload): Promise<PenggunaResponse> {
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