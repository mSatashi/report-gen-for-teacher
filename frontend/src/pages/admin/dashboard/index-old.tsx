import { useState, useEffect, useCallback } from "react";

const API_BASE = "https://api.anthropic.com/v1/messages";

async function callClaude(systemPrompt, userMessage) {
  const response = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: systemPrompt,
      messages: [{ role: "user", content: userMessage }],
    }),
  });
  const data = await response.json();
  const text = data.content?.map((i) => i.text || "").join("") || "";
  try {
    return JSON.parse(text.replace(/```json|```/g, "").trim());
  } catch {
    return { error: text };
  }
}

const SYSTEM_USER_CRUD = `You are a user management assistant. Respond ONLY with valid JSON, no markdown, no preamble.
For create: return { success: true, user: { id, name, email, role, status, createdAt, avatar } }
For update: return { success: true, user: { id, name, email, role, status, createdAt, avatar } }
For delete: return { success: true, message: string }
For list: return { success: true, users: [...] }
Generate realistic IDs and dates. Roles: admin | editor | viewer. Status: active | inactive.`;

const SYSTEM_PROFILE = `You are a profile management assistant. Respond ONLY with valid JSON, no markdown, no preamble.
For update profile: return { success: true, profile: { name, email, phone, bio, avatar } }
For change password: return { success: true, message: string }
For validation errors: return { success: false, message: string }`;

const INITIAL_USERS = [
  { id: "u1", name: "Budi Santoso", email: "budi@example.com", role: "editor", status: "active", createdAt: "2024-01-15", avatar: "BS" },
  { id: "u2", name: "Siti Rahayu", email: "siti@example.com", role: "viewer", status: "active", createdAt: "2024-02-20", avatar: "SR" },
  { id: "u3", name: "Ahmad Fauzi", email: "ahmad@example.com", role: "editor", status: "inactive", createdAt: "2024-03-10", avatar: "AF" },
];

const ADMIN_PROFILE = { name: "Admin Utama", email: "admin@dashboard.id", phone: "0812-3456-7890", bio: "System Administrator", avatar: "AU" };

const roleColors = { admin: "#7F77DD", editor: "#1D9E75", viewer: "#378ADD" };
const roleLabels = { admin: "Admin", editor: "Editor", viewer: "Viewer" };
const statusColors = { active: "#639922", inactive: "#E24B4A" };

function Avatar({ initials, size = 36, bg = "#7F77DD" }) {
  return (
    <div style={{ width: size, height: size, borderRadius: "50%", background: bg, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 600, fontSize: size * 0.35, flexShrink: 0 }}>
      {initials}
    </div>
  );
}

function Badge({ label, color }) {
  return (
    <span style={{ display: "inline-block", padding: "2px 10px", borderRadius: 99, background: color + "22", color, fontSize: 12, fontWeight: 600, letterSpacing: "0.02em" }}>
      {label}
    </span>
  );
}

function Modal({ title, onClose, children }) {
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)", zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
      <div style={{ background: "var(--color-background-primary)", borderRadius: 16, padding: 28, width: "100%", maxWidth: 480, boxShadow: "0 8px 32px rgba(0,0,0,0.18)", border: "0.5px solid var(--color-border-tertiary)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h3 style={{ margin: 0, fontSize: 17, fontWeight: 600 }}>{title}</h3>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 20, color: "var(--color-text-secondary)", lineHeight: 1 }}>×</button>
        </div>
        {children}
      </div>
    </div>
  );
}

function FormField({ label, type = "text", value, onChange, placeholder, options, required }) {
  const inputStyle = { width: "100%", boxSizing: "border-box", padding: "9px 12px", borderRadius: 8, border: "0.5px solid var(--color-border-secondary)", fontSize: 14, background: "var(--color-background-secondary)", color: "var(--color-text-primary)", outline: "none" };
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: "block", fontSize: 13, color: "var(--color-text-secondary)", marginBottom: 5, fontWeight: 500 }}>{label}{required && " *"}</label>
      {options ? (
        <select value={value} onChange={(e) => onChange(e.target.value)} style={inputStyle}>
          {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      ) : (
        <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} style={inputStyle} />
      )}
    </div>
  );
}

function Toast({ msg, type }) {
  if (!msg) return null;
  const colors = { success: "#639922", error: "#E24B4A", info: "#378ADD" };
  return (
    <div style={{ position: "fixed", bottom: 24, right: 24, background: colors[type] || colors.info, color: "#fff", padding: "12px 20px", borderRadius: 10, fontSize: 14, fontWeight: 500, zIndex: 200, boxShadow: "0 4px 16px rgba(0,0,0,0.15)", maxWidth: 320 }}>
      {msg}
    </div>
  );
}

export default function AdminDashboard() {
  const [page, setPage] = useState("dashboard");
  const [users, setUsers] = useState(INITIAL_USERS);
  const [adminProfile, setAdminProfile] = useState(ADMIN_PROFILE);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [modal, setModal] = useState(null);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({});
  const [profileForm, setProfileForm] = useState(ADMIN_PROFILE);
  const [passwordForm, setPasswordForm] = useState({ current: "", next: "", confirm: "" });
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const showToast = useCallback((msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const filteredUsers = users.filter((u) =>
    u.name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const stats = {
    total: users.length,
    active: users.filter((u) => u.status === "active").length,
    admins: users.filter((u) => u.role === "admin").length,
    editors: users.filter((u) => u.role === "editor").length,
  };

  function openCreate() {
    setForm({ name: "", email: "", role: "viewer", status: "active" });
    setModal("create");
  }

  function openEdit(user) {
    setForm({ ...user });
    setModal("edit");
  }

  function openDelete(user) {
    setForm({ ...user });
    setModal("delete");
  }

  async function handleCreate() {
    if (!form.name || !form.email) return showToast("Nama dan email wajib diisi", "error");
    setLoading(true);
    try {
      const result = await callClaude(SYSTEM_USER_CRUD, `Create a new user: name="${form.name}", email="${form.email}", role="${form.role}", status="${form.status}"`);
      if (result.success) {
        const newUser = { ...result.user, id: "u" + Date.now(), avatar: form.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() };
        setUsers((prev) => [newUser, ...prev]);
        setModal(null);
        showToast("Pengguna berhasil ditambahkan");
      } else {
        showToast(result.message || "Gagal menambahkan pengguna", "error");
      }
    } catch {
      const newUser = { id: "u" + Date.now(), ...form, createdAt: new Date().toISOString().split("T")[0], avatar: form.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() };
      setUsers((prev) => [newUser, ...prev]);
      setModal(null);
      showToast("Pengguna berhasil ditambahkan");
    }
    setLoading(false);
  }

  async function handleEdit() {
    if (!form.name || !form.email) return showToast("Nama dan email wajib diisi", "error");
    setLoading(true);
    try {
      const result = await callClaude(SYSTEM_USER_CRUD, `Update user id="${form.id}": name="${form.name}", email="${form.email}", role="${form.role}", status="${form.status}"`);
      const updated = { ...form, avatar: form.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() };
      setUsers((prev) => prev.map((u) => u.id === form.id ? updated : u));
      setModal(null);
      showToast("Pengguna berhasil diperbarui");
    } catch {
      const updated = { ...form, avatar: form.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() };
      setUsers((prev) => prev.map((u) => u.id === form.id ? updated : u));
      setModal(null);
      showToast("Pengguna berhasil diperbarui");
    }
    setLoading(false);
  }

  async function handleDelete() {
    setLoading(true);
    try {
      await callClaude(SYSTEM_USER_CRUD, `Delete user id="${form.id}", name="${form.name}"`);
    } catch {}
    setUsers((prev) => prev.filter((u) => u.id !== form.id));
    setModal(null);
    showToast("Pengguna berhasil dihapus");
    setLoading(false);
  }

  async function handleSaveProfile() {
    if (!profileForm.name || !profileForm.email) return showToast("Nama dan email wajib diisi", "error");
    setLoading(true);
    try {
      const result = await callClaude(SYSTEM_PROFILE, `Update admin profile: name="${profileForm.name}", email="${profileForm.email}", phone="${profileForm.phone}", bio="${profileForm.bio}"`);
      const updated = { ...profileForm, avatar: profileForm.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() };
      setAdminProfile(updated);
      showToast("Profil berhasil disimpan");
    } catch {
      const updated = { ...profileForm, avatar: profileForm.name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase() };
      setAdminProfile(updated);
      showToast("Profil berhasil disimpan");
    }
    setLoading(false);
  }

  async function handleChangePassword() {
    if (!passwordForm.current) return showToast("Password saat ini wajib diisi", "error");
    if (passwordForm.next.length < 6) return showToast("Password baru minimal 6 karakter", "error");
    if (passwordForm.next !== passwordForm.confirm) return showToast("Konfirmasi password tidak cocok", "error");
    setLoading(true);
    try {
      const result = await callClaude(SYSTEM_PROFILE, `Change password for admin. Current password provided: yes. New password length: ${passwordForm.next.length} chars.`);
      if (result.success === false) {
        showToast(result.message || "Gagal mengubah password", "error");
      } else {
        setPasswordForm({ current: "", next: "", confirm: "" });
        showToast("Password berhasil diubah");
      }
    } catch {
      setPasswordForm({ current: "", next: "", confirm: "" });
      showToast("Password berhasil diubah");
    }
    setLoading(false);
  }

  const navItems = [
    { id: "dashboard", icon: "⊞", label: "Dashboard" },
    { id: "users", icon: "👥", label: "Pengguna" },
    { id: "profile", icon: "👤", label: "Profil Saya" },
  ];

  const sidebarW = sidebarOpen ? 220 : 64;

  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "'Segoe UI', sans-serif", background: "#F8F7F4" }}>
      {/* Sidebar */}
      <aside style={{ width: sidebarW, minHeight: "100vh", background: "#1E1B3A", color: "#fff", display: "flex", flexDirection: "column", transition: "width 0.2s", flexShrink: 0, position: "relative" }}>
        <div style={{ padding: sidebarOpen ? "20px 16px 12px" : "20px 8px 12px", display: "flex", alignItems: "center", gap: 10, borderBottom: "0.5px solid rgba(255,255,255,0.08)" }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #7F77DD, #534AB7)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>⚡</div>
          {sidebarOpen && <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.01em", whiteSpace: "nowrap" }}>AdminPanel</span>}
        </div>
        <nav style={{ flex: 1, padding: "12px 8px" }}>
          {navItems.map((item) => {
            const active = page === item.id;
            return (
              <button key={item.id} onClick={() => setPage(item.id)} style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: sidebarOpen ? "10px 12px" : "10px", borderRadius: 9, border: "none", cursor: "pointer", background: active ? "rgba(127,119,221,0.18)" : "transparent", color: active ? "#AFA9EC" : "rgba(255,255,255,0.55)", fontWeight: active ? 600 : 400, fontSize: 14, marginBottom: 2, transition: "all 0.15s", textAlign: "left" }}>
                <span style={{ fontSize: 18, flexShrink: 0 }}>{item.icon}</span>
                {sidebarOpen && <span style={{ whiteSpace: "nowrap" }}>{item.label}</span>}
              </button>
            );
          })}
        </nav>
        <div style={{ padding: sidebarOpen ? "12px 16px" : "12px 8px", borderTop: "0.5px solid rgba(255,255,255,0.08)", display: "flex", alignItems: "center", gap: 10 }}>
          <Avatar initials={adminProfile.avatar} size={32} bg="#7F77DD" />
          {sidebarOpen && (
            <div style={{ overflow: "hidden" }}>
              <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "#fff", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{adminProfile.name}</p>
              <p style={{ margin: 0, fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Administrator</p>
            </div>
          )}
        </div>
        <button onClick={() => setSidebarOpen((v) => !v)} style={{ position: "absolute", top: 22, right: -12, width: 24, height: 24, borderRadius: "50%", background: "#534AB7", border: "none", cursor: "pointer", color: "#fff", fontSize: 12, display: "flex", alignItems: "center", justifyContent: "center", zIndex: 10 }}>
          {sidebarOpen ? "‹" : "›"}
        </button>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, overflow: "auto" }}>
        {/* Header */}
        <div style={{ background: "#fff", borderBottom: "0.5px solid #E8E6DE", padding: "14px 28px", display: "flex", alignItems: "center", justifyContent: "space-between", position: "sticky", top: 0, zIndex: 50 }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#1E1B3A" }}>
              {page === "dashboard" ? "Dashboard" : page === "users" ? "Manajemen Pengguna" : "Profil Admin"}
            </h1>
            <p style={{ margin: 0, fontSize: 12, color: "#888" }}>
              {new Date().toLocaleDateString("id-ID", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
            </p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {loading && <span style={{ fontSize: 12, color: "#7F77DD", fontWeight: 500 }}>⟳ Memproses...</span>}
            <Avatar initials={adminProfile.avatar} size={36} bg="#7F77DD" />
          </div>
        </div>

        <div style={{ padding: 28 }}>
          {/* DASHBOARD PAGE */}
          {page === "dashboard" && (
            <div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 16, marginBottom: 28 }}>
                {[
                  { label: "Total Pengguna", value: stats.total, icon: "👥", color: "#7F77DD" },
                  { label: "Pengguna Aktif", value: stats.active, icon: "✅", color: "#639922" },
                  { label: "Role Admin", value: stats.admins, icon: "🛡", color: "#E24B4A" },
                  { label: "Role Editor", value: stats.editors, icon: "✏️", color: "#1D9E75" },
                ].map((s) => (
                  <div key={s.label} style={{ background: "#fff", borderRadius: 12, padding: "18px 20px", border: "0.5px solid #E8E6DE" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ fontSize: 22 }}>{s.icon}</span>
                      <span style={{ fontSize: 28, fontWeight: 700, color: s.color }}>{s.value}</span>
                    </div>
                    <p style={{ margin: 0, fontSize: 13, color: "#888", fontWeight: 500 }}>{s.label}</p>
                  </div>
                ))}
              </div>
              <div style={{ background: "#fff", borderRadius: 12, border: "0.5px solid #E8E6DE", overflow: "hidden" }}>
                <div style={{ padding: "16px 20px", borderBottom: "0.5px solid #E8E6DE", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h2 style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>Pengguna Terbaru</h2>
                  <button onClick={() => setPage("users")} style={{ background: "#7F77DD", color: "#fff", border: "none", borderRadius: 8, padding: "7px 14px", fontSize: 13, cursor: "pointer", fontWeight: 500 }}>Lihat Semua</button>
                </div>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: "#F8F7F4" }}>
                      {["Pengguna", "Email", "Role", "Status", "Bergabung"].map((h) => (
                        <th key={h} style={{ padding: "10px 20px", textAlign: "left", fontSize: 12, color: "#888", fontWeight: 600, letterSpacing: "0.04em" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {users.slice(0, 5).map((u) => (
                      <tr key={u.id} style={{ borderTop: "0.5px solid #E8E6DE" }}>
                        <td style={{ padding: "12px 20px" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <Avatar initials={u.avatar} size={32} bg={roleColors[u.role] + "99"} />
                            <span style={{ fontSize: 14, fontWeight: 500 }}>{u.name}</span>
                          </div>
                        </td>
                        <td style={{ padding: "12px 20px", fontSize: 13, color: "#666" }}>{u.email}</td>
                        <td style={{ padding: "12px 20px" }}><Badge label={roleLabels[u.role]} color={roleColors[u.role]} /></td>
                        <td style={{ padding: "12px 20px" }}><Badge label={u.status === "active" ? "Aktif" : "Nonaktif"} color={statusColors[u.status]} /></td>
                        <td style={{ padding: "12px 20px", fontSize: 13, color: "#888" }}>{u.createdAt}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* USERS PAGE */}
          {page === "users" && (
            <div>
              <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
                <input placeholder="🔍  Cari pengguna..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ flex: 1, minWidth: 200, padding: "9px 14px", borderRadius: 9, border: "0.5px solid #D3D1C7", fontSize: 14, background: "#fff", outline: "none" }} />
                <button onClick={openCreate} style={{ background: "#7F77DD", color: "#fff", border: "none", borderRadius: 9, padding: "9px 18px", fontSize: 14, cursor: "pointer", fontWeight: 600, whiteSpace: "nowrap" }}>+ Tambah Pengguna</button>
              </div>
              <div style={{ background: "#fff", borderRadius: 12, border: "0.5px solid #E8E6DE", overflow: "hidden" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ background: "#F8F7F4" }}>
                      {["Pengguna", "Email", "Role", "Status", "Bergabung", "Aksi"].map((h) => (
                        <th key={h} style={{ padding: "11px 18px", textAlign: "left", fontSize: 12, color: "#888", fontWeight: 600, letterSpacing: "0.04em" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.length === 0 ? (
                      <tr><td colSpan={6} style={{ padding: 32, textAlign: "center", color: "#aaa", fontSize: 14 }}>Tidak ada pengguna ditemukan</td></tr>
                    ) : filteredUsers.map((u) => (
                      <tr key={u.id} style={{ borderTop: "0.5px solid #E8E6DE" }}>
                        <td style={{ padding: "12px 18px" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <Avatar initials={u.avatar} size={34} bg={roleColors[u.role] + "99"} />
                            <span style={{ fontSize: 14, fontWeight: 500 }}>{u.name}</span>
                          </div>
                        </td>
                        <td style={{ padding: "12px 18px", fontSize: 13, color: "#555" }}>{u.email}</td>
                        <td style={{ padding: "12px 18px" }}><Badge label={roleLabels[u.role]} color={roleColors[u.role]} /></td>
                        <td style={{ padding: "12px 18px" }}><Badge label={u.status === "active" ? "Aktif" : "Nonaktif"} color={statusColors[u.status]} /></td>
                        <td style={{ padding: "12px 18px", fontSize: 13, color: "#888" }}>{u.createdAt}</td>
                        <td style={{ padding: "12px 18px" }}>
                          <div style={{ display: "flex", gap: 6 }}>
                            <button onClick={() => openEdit(u)} style={{ background: "#E1F5EE", color: "#0F6E56", border: "none", borderRadius: 7, padding: "5px 12px", fontSize: 12, cursor: "pointer", fontWeight: 600 }}>Edit</button>
                            <button onClick={() => openDelete(u)} style={{ background: "#FCEBEB", color: "#A32D2D", border: "none", borderRadius: 7, padding: "5px 12px", fontSize: 12, cursor: "pointer", fontWeight: 600 }}>Hapus</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div style={{ padding: "10px 18px", borderTop: "0.5px solid #E8E6DE", fontSize: 12, color: "#999" }}>
                  Menampilkan {filteredUsers.length} dari {users.length} pengguna
                </div>
              </div>
            </div>
          )}

          {/* PROFILE PAGE */}
          {page === "profile" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20 }}>
              {/* Profile Info */}
              <div style={{ background: "#fff", borderRadius: 14, border: "0.5px solid #E8E6DE", padding: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24, paddingBottom: 20, borderBottom: "0.5px solid #E8E6DE" }}>
                  <Avatar initials={adminProfile.avatar} size={60} bg="#7F77DD" />
                  <div>
                    <h2 style={{ margin: 0, fontSize: 17, fontWeight: 700 }}>{adminProfile.name}</h2>
                    <p style={{ margin: "2px 0 0", fontSize: 13, color: "#888" }}>Administrator</p>
                  </div>
                </div>
                <h3 style={{ margin: "0 0 14px", fontSize: 14, fontWeight: 700, color: "#444", textTransform: "uppercase", letterSpacing: "0.05em" }}>Edit Profil</h3>
                <FormField label="Nama Lengkap" value={profileForm.name} onChange={(v) => setProfileForm({ ...profileForm, name: v })} placeholder="Nama lengkap" required />
                <FormField label="Email" type="email" value={profileForm.email} onChange={(v) => setProfileForm({ ...profileForm, email: v })} placeholder="email@domain.com" required />
                <FormField label="Nomor Telepon" value={profileForm.phone} onChange={(v) => setProfileForm({ ...profileForm, phone: v })} placeholder="08xx-xxxx-xxxx" />
                <FormField label="Bio" value={profileForm.bio} onChange={(v) => setProfileForm({ ...profileForm, bio: v })} placeholder="Tentang Anda" />
                <button onClick={handleSaveProfile} disabled={loading} style={{ width: "100%", background: "#7F77DD", color: "#fff", border: "none", borderRadius: 9, padding: "11px", fontSize: 14, cursor: "pointer", fontWeight: 600, marginTop: 4, opacity: loading ? 0.7 : 1 }}>
                  {loading ? "Menyimpan..." : "Simpan Profil"}
                </button>
              </div>

              {/* Change Password */}
              <div style={{ background: "#fff", borderRadius: 14, border: "0.5px solid #E8E6DE", padding: 24 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20, paddingBottom: 16, borderBottom: "0.5px solid #E8E6DE" }}>
                  <span style={{ fontSize: 24 }}>🔒</span>
                  <div>
                    <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700 }}>Ubah Password</h2>
                    <p style={{ margin: 0, fontSize: 12, color: "#888" }}>Pastikan password baru kuat</p>
                  </div>
                </div>
                <FormField label="Password Saat Ini" type="password" value={passwordForm.current} onChange={(v) => setPasswordForm({ ...passwordForm, current: v })} placeholder="••••••••" required />
                <FormField label="Password Baru" type="password" value={passwordForm.next} onChange={(v) => setPasswordForm({ ...passwordForm, next: v })} placeholder="Min. 6 karakter" required />
                <FormField label="Konfirmasi Password Baru" type="password" value={passwordForm.confirm} onChange={(v) => setPasswordForm({ ...passwordForm, confirm: v })} placeholder="Ulangi password baru" required />
                <div style={{ background: "#F8F7F4", borderRadius: 9, padding: "10px 14px", marginBottom: 16, fontSize: 12, color: "#888" }}>
                  <p style={{ margin: 0, fontWeight: 600, color: "#555" }}>Syarat password:</p>
                  <p style={{ margin: "4px 0 0" }}>• Minimal 6 karakter<br />• Kombinasi huruf dan angka direkomendasikan</p>
                </div>
                <button onClick={handleChangePassword} disabled={loading} style={{ width: "100%", background: "#534AB7", color: "#fff", border: "none", borderRadius: 9, padding: "11px", fontSize: 14, cursor: "pointer", fontWeight: 600, opacity: loading ? 0.7 : 1 }}>
                  {loading ? "Memproses..." : "Ubah Password"}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* MODALS */}
      {modal === "create" && (
        <Modal title="Tambah Pengguna Baru" onClose={() => setModal(null)}>
          <FormField label="Nama Lengkap" value={form.name} onChange={(v) => setForm({ ...form, name: v })} placeholder="Nama lengkap" required />
          <FormField label="Email" type="email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} placeholder="email@domain.com" required />
          <FormField label="Role" value={form.role} onChange={(v) => setForm({ ...form, role: v })} options={[{ value: "viewer", label: "Viewer" }, { value: "editor", label: "Editor" }, { value: "admin", label: "Admin" }]} />
          <FormField label="Status" value={form.status} onChange={(v) => setForm({ ...form, status: v })} options={[{ value: "active", label: "Aktif" }, { value: "inactive", label: "Nonaktif" }]} />
          <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
            <button onClick={() => setModal(null)} style={{ flex: 1, background: "#F8F7F4", color: "#555", border: "0.5px solid #D3D1C7", borderRadius: 9, padding: "10px", fontSize: 14, cursor: "pointer", fontWeight: 500 }}>Batal</button>
            <button onClick={handleCreate} disabled={loading} style={{ flex: 1, background: "#7F77DD", color: "#fff", border: "none", borderRadius: 9, padding: "10px", fontSize: 14, cursor: "pointer", fontWeight: 600, opacity: loading ? 0.7 : 1 }}>{loading ? "Memproses..." : "Tambah"}</button>
          </div>
        </Modal>
      )}

      {modal === "edit" && (
        <Modal title="Edit Pengguna" onClose={() => setModal(null)}>
          <FormField label="Nama Lengkap" value={form.name} onChange={(v) => setForm({ ...form, name: v })} placeholder="Nama lengkap" required />
          <FormField label="Email" type="email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} placeholder="email@domain.com" required />
          <FormField label="Role" value={form.role} onChange={(v) => setForm({ ...form, role: v })} options={[{ value: "viewer", label: "Viewer" }, { value: "editor", label: "Editor" }, { value: "admin", label: "Admin" }]} />
          <FormField label="Status" value={form.status} onChange={(v) => setForm({ ...form, status: v })} options={[{ value: "active", label: "Aktif" }, { value: "inactive", label: "Nonaktif" }]} />
          <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
            <button onClick={() => setModal(null)} style={{ flex: 1, background: "#F8F7F4", color: "#555", border: "0.5px solid #D3D1C7", borderRadius: 9, padding: "10px", fontSize: 14, cursor: "pointer", fontWeight: 500 }}>Batal</button>
            <button onClick={handleEdit} disabled={loading} style={{ flex: 1, background: "#1D9E75", color: "#fff", border: "none", borderRadius: 9, padding: "10px", fontSize: 14, cursor: "pointer", fontWeight: 600, opacity: loading ? 0.7 : 1 }}>{loading ? "Memproses..." : "Simpan"}</button>
          </div>
        </Modal>
      )}

      {modal === "delete" && (
        <Modal title="Hapus Pengguna" onClose={() => setModal(null)}>
          <div style={{ textAlign: "center", padding: "8px 0 20px" }}>
            <div style={{ fontSize: 48, marginBottom: 12 }}>⚠️</div>
            <p style={{ fontSize: 15, color: "#333", margin: "0 0 6px" }}>Apakah Anda yakin ingin menghapus</p>
            <p style={{ fontSize: 16, fontWeight: 700, color: "#E24B4A", margin: "0 0 12px" }}>{form.name}?</p>
            <p style={{ fontSize: 13, color: "#888", margin: 0 }}>Tindakan ini tidak dapat dibatalkan.</p>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <button onClick={() => setModal(null)} style={{ flex: 1, background: "#F8F7F4", color: "#555", border: "0.5px solid #D3D1C7", borderRadius: 9, padding: "10px", fontSize: 14, cursor: "pointer", fontWeight: 500 }}>Batal</button>
            <button onClick={handleDelete} disabled={loading} style={{ flex: 1, background: "#E24B4A", color: "#fff", border: "none", borderRadius: 9, padding: "10px", fontSize: 14, cursor: "pointer", fontWeight: 600, opacity: loading ? 0.7 : 1 }}>{loading ? "Menghapus..." : "Ya, Hapus"}</button>
          </div>
        </Modal>
      )}

      {toast && <Toast msg={toast.msg} type={toast.type} />}
    </div>
  );
}