import React, { useEffect, useState } from "react";
import Notification from "../../ui/Notifications";
import StatCardItem from "../dashboard/StatCardItem";
import StudentRow from "../dashboard/studentRow";
import type { DashboardResponse } from "../../service/payload";
import { useDashboard } from "./useDashboard";
import { buildStatCards } from "./statCards";
import ActivityItem from "./ActivityItem";

interface DashboardPageProps {
  /** Optional flash messages forwarded from the layout */
  flash?: {
    success?: string | null;
    error?: string | null;
    errors?: string[];
  };
  namaLengkap: string;
}

const DashboardPage: React.FC<DashboardPageProps> = ({ flash, namaLengkap }) => {
  const [dataDashboard, setDataDashboard] = useState<DashboardResponse | null>(null);

  const { loadDashboard } = useDashboard();

  useEffect(() => {
    loadDashboard().then((data) => {
      if (!data) return;
        setDataDashboard({
          total_siswa: data.total_siswa,
          log_hari_ini: data.log_hari_ini,
          plan_aktif: data.plan_aktif,
          report_pending: data.report_pending,
          aktivitas_terbaru: data.aktivitas_terbaru,
          progress_siswa: data.progress_siswa,
        });
    });
  }, []);

  const statCards = buildStatCards(dataDashboard)
  // ← tambah ini, fallback ke dummy jika kosong
  const progressSiswa = dataDashboard?.progress_siswa?.length
    ? dataDashboard.progress_siswa
    : [];

  const aktivitasTerbaru = dataDashboard?.aktivitas_terbaru?.length
    ? dataDashboard.aktivitas_terbaru
    : [];

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
          Selamat pagi, {namaLengkap} 👋
        </h2>
        <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
          {today}
        </p>
      </div>

      {/* Stat cards */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 28 }}>
        {statCards.map((c) => (
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

          {/* {dataDashboard?.progress_siswa.map((s) => (
            <StudentRow key={s.name} student={s} />
          ))} */}
          {progressSiswa.map((s) => (
            <StudentRow key={s.nama} student={s} />
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
            {/* <button
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
            </button> */}
          </div>

          {aktivitasTerbaru.map((a) => (
            <ActivityItem key={a.kelas_id} activity={a} />
          ))}
        </div>

      </div>
    </>
  );
};

export default DashboardPage;