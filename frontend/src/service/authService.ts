
export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUser {
  user_id: string;
  access_token: string;
  token_type: string;
  tipe_pengguna: string;
}

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export async function loginAPI(payload: LoginPayload): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email_address: payload.email,
      password: payload.password,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message ?? "Login gagal. Periksa username/password.");
  }

  return res.json();
}