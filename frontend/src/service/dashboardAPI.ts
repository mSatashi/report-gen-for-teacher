import { apiFetch } from "./apiFetch";
import type { DashboardResponse } from "./payload";

/** GET /kelas — ambil semua data plan */
export async function fetchDashboard(): Promise<DashboardResponse> {
  const res = await apiFetch(`/dashboard`);
  if (!res.ok) throw new Error(`Gagal memuat data dashboard (${res.status})`);
  return res.json();
}