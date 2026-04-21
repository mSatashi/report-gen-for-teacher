import { apiFetch } from "./apiFetch";
import type { addSiswaPayload, KelasPayload, KelasResponse, messageResponse, SiswaResponse } from "./payload";

/** GET /kelas — ambil semua kelas */
export async function fetchKelasList(): Promise<KelasResponse[]> {
  const res = await apiFetch(`/kelas`);
  if (!res.ok) throw new Error(`Gagal memuat data kelas (${res.status})`);
  return res.json();
}

/** POST /kelas — buat kelas baru */
export async function createKelas(payload: KelasPayload): Promise<KelasResponse> {
  const res = await apiFetch(`/kelas`, {
    method: "POST",
    body: JSON.stringify({
      nama: payload.nama,
      mata_pelajaran: payload.mata_pelajaran,
      kredit: payload.kredit,
      jadwal: payload.jadwal,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat kelas (${res.status})`);
  }
  return res.json();
}

/** PUT /kelas/:id — update kelas */
export async function updateKelas(id: string, payload: KelasPayload): Promise<KelasResponse> {
  const res = await apiFetch(`/kelas/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      nama: payload.nama,
      mata_pelajaran: payload.mata_pelajaran,
      kredit: payload.kredit,
      jadwal: payload.jadwal,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal mengupdate kelas (${res.status})`);
  }
  return res.json();
}

/** DELETE /kelas/:id — hapus kelas */
export async function deleteKelasApi(id: string): Promise<void> {
  const res = await apiFetch(`/kelas/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Gagal menghapus kelas (${res.status})`);
}

/** GET /kelas/:kelasId/murid — ambil semua siswa dalam kelas */
export async function fetchSiswaByKelas(kelasId: string): Promise<SiswaResponse[]> {
  const res = await apiFetch(`/kelas/${kelasId}/murid`);
  if (!res.ok) throw new Error(`Gagal memuat data siswa (${res.status})`);
  return res.json();
}
 
/** POST /kelas/:kelasId/siswa — siswa di dalam kelas */
export async function siswaDalamKelas(
  kelasId: string
): Promise<SiswaResponse[]> {
  const res = await apiFetch(`/kelas/${kelasId}/murid`, {
    method: "GET",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal menambahkan siswa (${res.status})`);
  }
  return res.json();
}

/** menambahkan data siswa ke dalam kelas */
export async function addSiswaKelas(
  kelasId: string,
  payload: addSiswaPayload
): Promise<messageResponse> {
  const res = await apiFetch(`/kelas/${kelasId}/murid`, {
    method: "POST",
    body: JSON.stringify({
      murid_id: payload.murid_id,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal menambahkan siswa (${res.status})`);
  }
  return res.json();
}

/** DELETE /siswa/:id — hapus siswa */
export async function deleteSiswaKelas(kelasId: string, siswaId: string): Promise<void> {
  const res = await apiFetch(`/kelas/${kelasId}/murid/${siswaId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Gagal menghapus siswa (${res.status})`);
}
 
// /** PUT /siswa/:id — update data siswa */
// export async function updateSiswa(
//   siswaId: string,
//   payload: SiswaPayload
// ): Promise<SiswaResponse> {
//   const res = await apiFetch(`/siswa/${siswaId}`, {
//     method: "PUT",
//     body: JSON.stringify({
//       username: payload.username,
//       email_address: payload.email_address,
//       nama: payload.nama,
//       usia: payload.usia,
//       level: payload.level,
//       credit_total: payload.credit_total,
//     }),
//   });
//   if (!res.ok) {
//     const err = await res.json().catch(() => ({}));
//     throw new Error(err?.message ?? `Gagal mengupdate siswa (${res.status})`);
//   }
//   return res.json();
// }
 

 
// /** PUT /siswa/:id — update data siswa */
// export async function updateSiswa(
//   siswaId: string,
//   payload: SiswaPayload
// ): Promise<SiswaResponse> {
//   const res = await apiFetch(`/siswa/${siswaId}`, {
//     method: "PUT",
//     body: JSON.stringify({
//       nama: payload.nama,
//       nis: payload.nis,
//       jenis_kelamin: payload.jenis_kelamin,
//       tanggal_lahir: payload.tanggal_lahir,
//       alamat: payload.alamat,
//     }),
//   });
//   if (!res.ok) {
//     const err = await res.json().catch(() => ({}));
//     throw new Error(err?.message ?? `Gagal mengupdate siswa (${res.status})`);
//   }
//   return res.json();
// }
 
// /** DELETE /siswa/:id — hapus siswa */
// export async function deleteSiswaApi(siswaId: string): Promise<void> {
//   const res = await apiFetch(`/siswa/${siswaId}`, { method: "DELETE" });
//   if (!res.ok) throw new Error(`Gagal menghapus siswa (${res.status})`);
// }