import { apiFetch } from "./apiFetch";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUser {
  user_id: string;
  access_token: string;
  token_type: string;
  tipe_pengguna: string;
  username: string;
  email_address: string;
}


export async function loginAPI(payload: LoginPayload): Promise<AuthUser> {
  const res = await apiFetch(`/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email_address: payload.email,
      password: payload.password,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message ?? "Login gagal. Periksa email/password.");
  }

  return res.json();
}

export async function logout() {
  const res = await apiFetch(`/auth/logout`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message ?? "Logout gagal.");
  }

  return res.json();
}