import { apiFetch } from "./apiFetch";
import type { DailyLogPayload, DailyLogResponse } from "./payload";

/** GET /log-siswa — ambil semua log siswa */
export async function fetchLogSiswa(siswaId: string): Promise<DailyLogResponse[]> {
  const res = await apiFetch(`/logs/murid/${siswaId}`);
  if (!res.ok) throw new Error(`Gagal memuat data log siswa (${res.status})`);
  return res.json();
}

/** create daily log siswa */
export async function createDailyLog(
  payload: DailyLogPayload
): Promise<DailyLogResponse> {
  const res = await apiFetch("/logs/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat log (${res.status})`);
  }
  return res.json();
}

/** update daily log siswa */
export async function updateDailyLog(
  id: string,
  payload: DailyLogPayload
): Promise<DailyLogResponse> {
  const res = await apiFetch(`/logs/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal memperbarui log (${res.status})`);
  }
  return res.json();
}

/** DELETE /logs/:id — hapus log */
export async function deleteDailyLogApi(id: string): Promise<void> {
  const res = await apiFetch(`/logs/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Gagal menghapus log (${res.status})`);
}