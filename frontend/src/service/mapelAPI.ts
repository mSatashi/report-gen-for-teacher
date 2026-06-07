import { apiFetch } from "./apiFetch";
import type { MapelPayload, MapelResponse, MapelUpdatePayload, TopikResponse } from "./payload";

/** GET /mata-pelajaran — ambil semua mata pelajaran */
export async function fetchMapelList(): Promise<MapelResponse[]> {
  const res = await apiFetch(`/mata-pelajaran`);
  if (!res.ok) throw new Error(`Gagal memuat data mata pelajaran (${res.status})`);
  return res.json();
}

/** POST /mata-pelajaran — buat mata pelajaran baru */
export async function createMapel(payload: MapelPayload): Promise<MapelResponse> {
  const res = await apiFetch(`/mata-pelajaran`, {
    method: "POST",
    body: JSON.stringify({
      nama_mata_pelajaran: payload.nama_mata_pelajaran,
      topik_awal: payload.topik_awal?.map((t) => ({
        nama: t.nama,
        difficulty_index: t.difficulty_index,
        prasyarat_ids: t.prasyarat_ids ?? [],
      })),
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat mata pelajaran (${res.status})`);
  }
  return res.json();
}


/** PUT /mata-pelajaran — perbarui mata pelajaran */
export async function updateMapel(payload: MapelUpdatePayload, idMapel: string): Promise<MapelResponse> {
  const res = await apiFetch(`/mata-pelajaran/${idMapel}`, {
    method: "PUT",
    body: JSON.stringify({
      nama_mata_pelajaran: payload.nama_mata_pelajaran,
      topik_list: payload.topik_list?.map((t) => ({
        ...(t.id !== null && { id: t.id }),
        nama: t.nama,
        difficulty_index: t.difficulty_index,
        prasyarat_ids: t.prasyarat_ids ?? [],
      })) ?? [],
      }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal memperbarui mata pelajaran (${res.status})`);
  }
  return res.json();
}

/** DELETE /mata-pelajaran/:id — hapus mata pelajaran */
export async function deleteMapelApi(id: string): Promise<void> {
  const res = await apiFetch(`/mata-pelajaran/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Gagal menghapus mata pelajaran (${res.status})`);
}

/** GET /topik/mapel/:id — ambil semua topik untuk mata pelajaran tertentu */
export async function fetchTopikList(idMapel: string): Promise<TopikResponse[]> {
  const res = await apiFetch(`/topik/mapel/${idMapel}`);
  if (!res.ok) throw new Error(`Gagal memuat data topik (${res.status})`);
  return res.json();
}