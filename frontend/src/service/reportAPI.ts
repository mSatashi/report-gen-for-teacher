import { apiFetch } from "./apiFetch";
import type { ReportGeneratorPayload, ReportGeneratorResponse } from "./payload";

/** generate report */
export async function createReportGenerator(kelasId: string, siswaId: string, payload: ReportGeneratorPayload): Promise<ReportGeneratorResponse> {
  const res = await apiFetch(`/laporan/generate`, {
    method: "POST",
    body: JSON.stringify({ ...payload, kelas_id: kelasId, siswa_id: siswaId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat kelas (${res.status})`);
  }
  return res.json();
}