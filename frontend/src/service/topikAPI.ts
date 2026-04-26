import { apiFetch } from "./apiFetch";
import type { TopikPayload, TopikResponse } from "./payload";

export async function createTopik(payload: TopikPayload): Promise<TopikResponse> {
  const res = await apiFetch(`/topik/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Gagal membuat topik");
  return res.json();
}

export async function updateTopik(id: string, nama: string): Promise<TopikResponse> {
  const res = await apiFetch(`/topik/${id}`, {
    method: "PUT",
    body: JSON.stringify({ nama, difficulty_index: 0.5 }), 
  });
  if (!res.ok) throw new Error("Gagal update topik");
  return res.json();
}

export async function deleteTopikApi(id: string): Promise<void> {
  const res = await apiFetch(`/topik/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Gagal hapus topik");
}

export async function addPrasyaratApi(topikId: string, prasyaratId: string): Promise<void> {
  const res = await apiFetch(`/topik/${topikId}/prasyarat/${prasyaratId}`, { method: "POST" });
  if (!res.ok) throw new Error("Gagal menambah prasyarat");
}

export async function deletePrasyaratApi(topikId: string, prasyaratId: string): Promise<void> {
  const res = await apiFetch(`/topik/${topikId}/prasyarat/${prasyaratId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Gagal menghapus prasyarat");
}