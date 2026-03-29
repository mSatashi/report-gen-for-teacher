import React from "react";
import Notification from "../../ui/Notifications";
import StatCardItem from "../../ui/StatCardItem";
import StudentRow from "../../ui/StudentRow";
import ActivityItem from "../../ui/ActivityItem";
import { STAT_CARDS, STUDENTS, ACTIVITIES } from "../../data";

interface DashboardPageProps {
  /** Optional flash messages forwarded from the layout */
  flash?: {
    success?: string | null;
    error?: string | null;
    errors?: string[];
  };
}

const DashboardPage: React.FC<DashboardPageProps> = ({ flash }) => {
  const today = new Date().toLocaleDateString("id-ID", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <>
      {/* Flash notifications */}
      {flash && (
        <Notification
          success={flash.success}
          error={flash.error}
          errors={flash.errors}
        />
      )}

      {/* Greeting */}
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 26, fontWeight: 700, color: "#111827", margin: "0 0 4px" }}>
          Selamat pagi, Bu Rara 👋
        </h2>
        <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
          {today} · 3 siswa aktif
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 28 }}>
        {STAT_CARDS.map((c) => (
          <StatCardItem key={c.label} card={c} />
        ))}
      </div>

      {/* Two-column section */}
      <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>

        {/* Progress Siswa */}
        <div
          style={{
            background: "#fff",
            borderRadius: 14,
            padding: "20px 22px",
            flex: "2 1 340px",
            minWidth: 0,
            boxShadow: "0 1px 4px rgba(0,0,0,.06)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 4,
            }}
          >
            <span style={{ fontWeight: 700, fontSize: 16, color: "#111827" }}>
              Progress Siswa
            </span>
            <button
              style={{
                background: "#f3f4f6",
                border: "none",
                borderRadius: 8,
                padding: "5px 12px",
                fontSize: 12,
                fontWeight: 600,
                color: "#374151",
                cursor: "pointer",
              }}
            >
              Minggu ini
            </button>
          </div>

          {STUDENTS.map((s) => (
            <StudentRow key={s.name} student={s} />
          ))}
        </div>

        {/* Aktivitas Terbaru */}
        <div
          style={{
            background: "#fff",
            borderRadius: 14,
            padding: "20px 22px",
            flex: "1 1 260px",
            minWidth: 0,
            boxShadow: "0 1px 4px rgba(0,0,0,.06)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <span style={{ fontWeight: 700, fontSize: 16, color: "#111827" }}>
              Aktivitas Terbaru
            </span>
            <button
              style={{
                background: "#f3f4f6",
                border: "none",
                borderRadius: 8,
                padding: "5px 12px",
                fontSize: 12,
                fontWeight: 600,
                color: "#374151",
                cursor: "pointer",
              }}
            >
              Lihat Semua
            </button>
          </div>

          {ACTIVITIES.map((a) => (
            <ActivityItem key={a.title} activity={a} />
          ))}
        </div>

      </div>
    </>
  );
};

export default DashboardPage;