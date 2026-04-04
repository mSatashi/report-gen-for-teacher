// src/services/apiFetch.ts

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem("auth_token");

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  // Token expired / tidak valid → logout otomatis
  if (res.status === 401) {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
    window.location.reload(); // kembali ke login
  }

  return res;
}