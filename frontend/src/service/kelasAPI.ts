import { apiFetch } from "./apiFetch";
import type { KelasPayload, KelasResponse } from "./payload";

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