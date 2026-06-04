import React from "react";
import { adminDashboardStyles } from "./styles";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AdminDashboardProps {
  namaLengkap: string;
  onNavigate: (route: string, params?: Record<string, unknown>) => void;
}

interface StatCard {
  label: string;
  value: string;
  sub: string;
  positive: boolean;
  iconColor: string;
  iconBg: string;
  icon: string;
}

interface ActivityItem {
  icon: string;
  iconColor: string;
  iconBg: string;
  text: string;
  actor: string;
  time: string;
}

interface UserRow {
  initials: string;
  avatarBg: string;
  name: string;
  email: string;
  tipe: string;
  lastLogin: string;
  laporan: number;
  status: "aktif" | "nonaktif" | "pending";
}

// ─── Static data (ganti dengan API call sesuai kebutuhan) ─────────────────────

const STATS: StatCard[] = [
  {
    label: "Total Pengguna",
    value: "124",
    sub: "↑ +8 bulan ini",
    positive: true,
    icon: "ti-users",
    iconColor: "#4493f8",
    iconBg: "#dbeafe",
  },
  {
    label: "Total Siswa",
    value: "892",
    sub: "↑ +23 bulan ini",
    positive: true,
    icon: "ti-user-check",
    iconColor: "#16a34a",
    iconBg: "#dcfce7",
  },
  {
    label: "Laporan Dibuat",
    value: "3.471",
    sub: "↑ +412 bulan ini",
    positive: true,
    icon: "ti-file-analytics",
    iconColor: "#7c3aed",
    iconBg: "#ede9fe",
  },
  {
    label: "Kelas Aktif",
    value: "34",
    sub: "↓ -2 dari bulan lalu",
    positive: false,
    icon: "ti-door",
    iconColor: "#b45309",
    iconBg: "#fef3c7",
  },
];

const ACTIVITIES: ActivityItem[] = [
  {
    icon: "ti-user-plus",
    iconColor: "#4493f8",
    iconBg: "#dbeafe",
    text: "Pengguna baru",
    actor: "Rina Susanti",
    time: "2 menit lalu",
  },
  {
    icon: "ti-file-check",
    iconColor: "#16a34a",
    iconBg: "#dcfce7",
    text: "Laporan Kelas 7A berhasil di-generate oleh AI",
    actor: "",
    time: "15 menit lalu",
  },
  {
    icon: "ti-alert-triangle",
    iconColor: "#b45309",
    iconBg: "#fef3c7",
    text: "Gagal login berulang dari",
    actor: "ahmad@guru.id",
    time: "1 jam lalu",
  },
  {
    icon: "ti-edit",
    iconColor: "#7c3aed",
    iconBg: "#ede9fe",
    text: "Master mapel Matematika diperbarui",
    actor: "",
    time: "3 jam lalu",
  },
  {
    icon: "ti-user-x",
    iconColor: "#b91c1c",
    iconBg: "#fee2e2",
    text: "Akun",
    actor: "budi.lim@sekolah.id",
    time: "Kemarin, 15:42",
  },
];

const USERS: UserRow[] = [
  {
    initials: "DS",
    avatarBg: "#3b82f6",
    name: "Dewi Sartika",
    email: "dewi@sekolah.id",
    tipe: "Pengajar",
    lastLogin: "Hari ini",
    laporan: 142,
    status: "aktif",
  },
  {
    initials: "RH",
    avatarBg: "#16a34a",
    name: "Rizky Hakim",
    email: "rizky@sekolah.id",
    tipe: "Pengajar",
    lastLogin: "Kemarin",
    laporan: 98,
    status: "aktif",
  },
  {
    initials: "AS",
    avatarBg: "#b45309",
    name: "Ahmad Santoso",
    email: "ahmad@guru.id",
    tipe: "Pengajar",
    lastLogin: "3 hari lalu",
    laporan: 57,
    status: "pending",
  },
  {
    initials: "BL",
    avatarBg: "#b91c1c",
    name: "Budi Lim",
    email: "budi.lim@sekolah.id",
    tipe: "Pengajar",
    lastLogin: "2 minggu lalu",
    laporan: 203,
    status: "nonaktif",
  },
];

// ─── Chart data ───────────────────────────────────────────────────────────────

const CHART_DATA = [
  { label: "Jan", manual: 140, ai: 100 },
  { label: "Feb", manual: 190, ai: 120 },
  { label: "Mar", manual: 160, ai: 120 },
  { label: "Apr", manual: 250, ai: 170 },
  { label: "Mei", manual: 220, ai: 170 },
  { label: "Jun", manual: 271, ai: 200 },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

const SimpleBarChart: React.FC = () => {
  const max = Math.max(...CHART_DATA.flatMap((d) => [d.manual, d.ai]));
  return (
    <>
      <div style={{ display: "flex", gap: 16, marginBottom: 10, fontSize: 11, color: "#9ca3af" }}>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ width: 10, height: 10, borderRadius: 2, background: "#4493f8", display: "inline-block" }} />
          Pengajar
        </span>
        <span style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ width: 10, height: 10, borderRadius: 2, background: "#a78bfa", display: "inline-block" }} />
          AI Generate
        </span>
      </div>
      <div className="adm-chart-wrap">
        {CHART_DATA.map((d) => (
          <div key={d.label} className="adm-chart-col">
            <div className="adm-bar-wrap">
              <div
                className="adm-bar"
                style={{ height: `${(d.manual / max) * 100}%`, background: "#4493f8" }}
                title={`Pengajar: ${d.manual}`}
              />
              <div
                className="adm-bar"
                style={{ height: `${(d.ai / max) * 100}%`, background: "#a78bfa" }}
                title={`AI: ${d.ai}`}
              />
            </div>
            <span className="adm-chart-label">{d.label}</span>
          </div>
        ))}
      </div>
    </>
  );
};

// ─── Main component ───────────────────────────────────────────────────────────

const AdminDashboard: React.FC<AdminDashboardProps> = ({ namaLengkap, onNavigate }) => {
  return (
    <>
      <style>{adminDashboardStyles}</style>

      {/* Header */}
      <div className="adm-content-header">
        <h1>Dashboard Admin</h1>
        <p>Selamat datang kembali, {namaLengkap}. Berikut ringkasan sistem hari ini.</p>
      </div>

      {/* Stat Cards */}
      <div className="adm-stats">
        {STATS.map((s) => (
          <div className="adm-stat" key={s.label}>
            <div className="adm-stat-top">
              <div className="adm-stat-label">{s.label}</div>
              <div className="adm-stat-icon" style={{ background: s.iconBg }}>
                <i className={`ti ${s.icon}`} style={{ color: s.iconColor }} aria-hidden="true" />
              </div>
            </div>
            <div className="adm-stat-val">{s.value}</div>
            <div className="adm-stat-sub" style={{ color: s.positive ? "#16a34a" : "#b91c1c" }}>
              {s.sub}
            </div>
          </div>
        ))}
      </div>

      {/* Chart + Activity */}
      <div className="adm-row2col">
        <div className="adm-card">
          <div className="adm-card-title">
            Laporan Dibuat per Bulan
            <span>Lihat semua ↗</span>
          </div>
          <SimpleBarChart />
        </div>

        <div className="adm-card">
          <div className="adm-card-title">
            Aktivitas Terbaru
            <span>Semua ↗</span>
          </div>
          {ACTIVITIES.map((a, i) => (
            <div className="adm-act-item" key={i}>
              <div className="adm-act-icon" style={{ background: a.iconBg }}>
                <i className={`ti ${a.icon}`} style={{ color: a.iconColor, fontSize: 14 }} aria-hidden="true" />
              </div>
              <div>
                <div className="adm-act-main">
                  {a.text}{" "}
                  {a.actor && <strong>{a.actor}</strong>}
                </div>
                <div className="adm-act-time">{a.time}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* User Table */}
      <div className="adm-card">
        <div className="adm-card-title">
          Daftar Pengguna
          <span onClick={() => onNavigate("adminUsers")}>Kelola semua ↗</span>
        </div>
        <table className="adm-table">
          <thead>
            <tr>
              <th>Pengguna</th>
              <th>Tipe</th>
              <th>Terakhir Login</th>
              <th>Laporan</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {USERS.map((u) => (
              <tr key={u.email}>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div className="adm-user-av" style={{ background: u.avatarBg }}>
                      {u.initials}
                    </div>
                    <div>
                      <div className="adm-user-name">{u.name}</div>
                      <div className="adm-user-role">{u.email}</div>
                    </div>
                  </div>
                </td>
                <td>{u.tipe}</td>
                <td>{u.lastLogin}</td>
                <td>{u.laporan}</td>
                <td>
                  <span className={`adm-pill adm-pill-${u.status}`}>
                    {u.status.charAt(0).toUpperCase() + u.status.slice(1)}
                  </span>
                </td>
                <td>
                  <button className="adm-btn-sm">Kelola</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
};

export default AdminDashboard;