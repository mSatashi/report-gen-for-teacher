import { apiFetch } from "./apiFetch";
import type { SiswaPayload, SiswaResponse } from "./payload";

/** GET /murid — ambil semua data siswa */
export async function fetchSiswaList(): Promise<SiswaResponse[]> {
  const res = await apiFetch(`/murid`);
  if (!res.ok) throw new Error(`Gagal memuat data murid (${res.status})`);
  return res.json();
}

/** POST /murid — buat murid baru */
export async function createSiswa(payload: SiswaPayload): Promise<SiswaResponse> {
  const res = await apiFetch(`/murid`, {
    method: "POST",
    body: JSON.stringify({
      email_address: payload.email_address,
      nama: payload.nama,
      jenis_kelamin: payload.jenis_kelamin,
      education_level: payload.education_level,
      is_active: payload.is_active,
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
      email_address: payload.email_address,
      nama: payload.nama,
      jenis_kelamin: payload.jenis_kelamin,
      education_level: payload.education_level,
      is_active: payload.is_active,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal mengupdate murid (${res.status})`);
  }
  return res.json();
}

/** DELETE /murid/:id — hapus murid */
export async function deleteSiswaApi(id: string): Promise<void> {
  const res = await apiFetch(`/murid/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Gagal menghapus murid (${res.status})`);
}
// export async function deleteSiswaApi(id: string): Promise<boolean> {
//   const res = await apiFetch(`/murid/${id}`, { 
//     method: "DELETE" 
//   });

//   if (!res.ok) {
//     const err = await res.json().catch(() => ({}));
//     console.log("Error detail:", err);
//     throw new Error(err?.message ?? `Gagal menghapus siswa (${res.status})`);
//   }
//   return true;
// }

// /** GET /murid/:muridId/siswa — ambil semua siswa dalam murid */
// export async function fetchSiswaBySiswa(muridId: string): Promise<SiswaResponse[]> {
//   const res = await apiFetch(`/murid/${muridId}/murid`);
//   if (!res.ok) throw new Error(`Gagal memuat data siswa (${res.status})`);
//   return res.json();
// }
 