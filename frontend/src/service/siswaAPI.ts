import { apiFetch } from "./apiFetch";
import type { SiswaPayload, SiswaResponse } from "./payload";

// /** GET /murid — ambil semua murid */
// export async function fetchSiswaList(): Promise<SiswaResponse[]> {
//   const res = await apiFetch(`/murid`);
//   if (!res.ok) throw new Error(`Gagal memuat data murid (${res.status})`);
//   return res.json();
// }

/** POST /murid — buat murid baru */
export async function createSiswa(payload: SiswaPayload): Promise<SiswaResponse> {
  const res = await apiFetch(`/kelas/murid/tambah`, {
    method: "POST",
    body: JSON.stringify({
      username: payload.email_address,
      email_address: payload.email_address,
      password: payload.password,
      nama: payload.nama,
      usia: payload.usia,
      level: payload.level,
      credit_total: payload.credit_total,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat murid (${res.status})`);
  }
  return res.json();
}

/** PUT /murid/:id — update murid */
export async function updateSiswa(id: string, payload: SiswaPayload): Promise<SiswaResponse> {
  const res = await apiFetch(`/kelas/murid/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      nama: payload.nama,
      usia: payload.usia,
      level: payload.level,
      credit_total: payload.credit_total,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal mengupdate murid (${res.status})`);
  }
  return res.json();
}

// /** DELETE /murid/:id — hapus murid */
// export async function deleteSiswaApi(id: string): Promise<void> {
//   const res = await apiFetch(`/murid/${id}`, {
//     method: "DELETE",
//   });
//   if (!res.ok) throw new Error(`Gagal menghapus murid (${res.status})`);
// }

// /** GET /murid/:muridId/siswa — ambil semua siswa dalam murid */
// export async function fetchSiswaBySiswa(muridId: string): Promise<SiswaResponse[]> {
//   const res = await apiFetch(`/murid/${muridId}/murid`);
//   if (!res.ok) throw new Error(`Gagal memuat data siswa (${res.status})`);
//   return res.json();
// }
 