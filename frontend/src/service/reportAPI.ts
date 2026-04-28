import { apiFetch } from "./apiFetch";
import type { ReportGeneratorPayload, ReportGeneratorResponse } from "./payload";

/** generate report */
export async function createReportGenerator(payload: ReportGeneratorPayload): Promise<ReportGeneratorResponse> {
  const res = await apiFetch(`/laporan/generate`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal membuat kelas (${res.status})`);
  }
  return res.json();
}

/** list report per siswa */
export async function loadReportSiswa(siswaId: string): Promise<ReportGeneratorResponse[]> {
  const res = await apiFetch(`/laporan/murid/${siswaId}`, {
    method: "GET",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal memuat data report (${res.status})`);
  }
  return res.json();
}

/** PUT /report/:id — update report */
export async function updateReport(id: string, konten: string): Promise<ReportGeneratorResponse> {
  const res = await apiFetch(`/laporan/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      konten: konten,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal mengupdate report (${res.status})`);
  }
  return res.json();
}

export async function updateStatus(id: string): Promise<ReportGeneratorResponse> {
  const res = await apiFetch(`/laporan/${id}/finalisasi`, {
    method: "PUT",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.message ?? `Gagal mengupdate status (${res.status})`);
  }
  return res.json();
}