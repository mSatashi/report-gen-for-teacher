import { apiFetch } from "./apiFetch";
import type { GenerateplanResponse } from "./payload";

/** GET /kelas — ambil semua data plan */
export async function fetchPlanList(kelasId: string): Promise<GenerateplanResponse[]> {
  const res = await apiFetch(`/plan/kelas/${kelasId}`);
  if (!res.ok) throw new Error(`Gagal memuat data plan (${res.status})`);
  return res.json();
}

/** generate learning plan */
export async function createLearningPlan(kelasId: string): Promise<GenerateplanResponse> {
  const res = await apiFetch(`/plan/generate/${kelasId}`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat kelas (${res.status})`);
  }
  return res.json();
}