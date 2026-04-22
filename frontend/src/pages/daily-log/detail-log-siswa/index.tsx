import React, { useState } from "react";
import type { TingkatPemahaman } from "../components/types";
import { PENGUASAAN_BADGE, btnAddStyle } from "../components/constants";
import type { Kelas, Siswa } from "../../../types";
import type { DailyLogResponse } from "../../../service/payload";

interface DailyLogDetailSiswaProps {
  dataSiswa: Siswa;
  dataKelas?: Kelas | null;
  logDataSiswa: DailyLogResponse[];          // semua log — difilter by siswa + idMapel
  onBack: () => void;           // kembali ke listSiswa
  onBackToIndex: () => void;  
  onAddLog: () => void;
  onEditLog: (logId: number) => void;
}

const TABS = ["Semua", "Sangat Paham", "Paham", "Cukup", "Perlu Review"] as const;
type Tab = (typeof TABS)[number];

const DailyLogDetailSiswa: React.FC<DailyLogDetailSiswaProps> = ({
  dataSiswa,
  dataKelas,
  logDataSiswa,
  onBackToIndex,
  onBack,
  onAddLog,
  onEditLog,
}) => {

  const [activeTab, setActiveTab] = useState<Tab>("Semua");

  const siswaLogs = logDataSiswa.filter(
    (l) => l.murid_id === dataSiswa.nama
  );

  const countByLevel = (level: TingkatPemahaman) =>
    siswaLogs.filter((l) => l.tingkat_pemahaman as TingkatPemahaman === level).length;

  const filtered =
    activeTab === "Semua"
      ? siswaLogs
      : siswaLogs.filter((l) => l.tingkat_pemahaman === activeTab);

  const initials = dataSiswa.nama.split(" ").map((w) => w[0]).slice(0, 2).join("");

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* ── Header ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, flexShrink: 0, flexWrap: "wrap", gap: 12 }}>
        <div>
          {/* Breadcrumb: Daily Log › Matematika › Aisya Putri */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }} onClick={onBackToIndex}>
              Daily Log
            </span>
            <span style={{ fontSize: 13, color: "#d1d5db" }}>›</span>
            <span style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }} onClick={onBack}>
              {dataKelas?.mata_pelajaran}
            </span>
            <span style={{ fontSize: 13, color: "#d1d5db" }}>›</span>
            <span style={{ fontSize: 13, color: "#111827", fontWeight: 600 }}>{dataSiswa.nama}</span>
          </div>

          {/* Siswa info row */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ width: 44, height: 44, borderRadius: "50%", background: "#eff6ff", color: "#3b82f6", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 700, flexShrink: 0 }}>
              {initials}
            </div>
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 2px" }}>
                {dataSiswa.nama}
              </h2>
              <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
                {dataSiswa.level} · {dataKelas?.mata_pelajaran}
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={onBack} style={{ background: "none", border: "1px solid #e5e7eb", borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}>
            ← Kembali
          </button>
          <button onClick={onAddLog} style={btnAddStyle}>
            + Tambah Log
          </button>
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>

        {/* Stat cards */}
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", flexShrink: 0 }}>
          {[
            { label: "Total Log",    value: siswaLogs.length,          bg: "#eff6ff", color: "#3b82f6" },
            { label: "Sangat Paham", value: countByLevel("Sangat Paham"), bg: "#dcfce7", color: "#15803d" },
            { label: "Paham",        value: countByLevel("Paham"),        bg: "#dbeafe", color: "#1d4ed8" },
            { label: "Cukup",        value: countByLevel("Cukup"),        bg: "#fef9c3", color: "#ca8a04" },
            { label: "Perlu Review", value: countByLevel("Perlu Review"), bg: "#fee2e2", color: "#dc2626" },
          ].map((s) => (
            <div key={s.label} style={{ background: s.bg, borderRadius: 12, padding: "14px 20px", minWidth: 90, flex: "1 1 90px" }}>
              <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 12, color: s.color, fontWeight: 500, marginTop: 2 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Table card */}
        <div style={{ background: "#fff", borderRadius: 14, padding: "24px 28px", boxShadow: "0 1px 4px rgba(0,0,0,.06)", flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>

          {/* Tab filter */}
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20, flexShrink: 0 }}>
            {TABS.map((tab) => {
              const active = activeTab === tab;
              const count  = tab === "Semua" ? siswaLogs.length : countByLevel(tab as TingkatPemahaman);
              const badge  = tab !== "Semua" ? PENGUASAAN_BADGE[tab as TingkatPemahaman] : null;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    border: active ? "none" : "1px solid #e5e7eb",
                    borderRadius: 8, padding: "6px 14px", fontSize: 12, fontWeight: 600,
                    cursor: "pointer",
                    background: active ? (badge ? badge.bg : "#eff6ff") : "#fff",
                    color:      active ? (badge ? badge.color : "#3b82f6") : "#6b7280",
                    transition: "all .15s",
                  }}
                >
                  {tab} ({count})
                </button>
              );
            })}
          </div>

          {/* Table */}
          <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "rgba(228,230,239,0.85)" }}>
                  {[
                    { label: "No",           width: 50     },
                    { label: "Tanggal",      width: 110    },
                    { label: "Materi",       width: "auto" },
                    { label: "Durasi",       width: 80     },
                    { label: "Metode",       width: 140    },
                    { label: "Pemahaman",    width: 130    },
                    { label: "Keterlibatan", width: 120    },
                    { label: "Catatan",      width: "auto" },
                    { label: "Actions",      width: 100    },
                  ].map((h) => (
                    <th key={h.label} style={{ padding: "10px 14px", textAlign: "left", fontWeight: 600, color: "#374151", width: h.width, whiteSpace: "nowrap" }}>
                      {h.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((log, idx) => {
                  const badge = PENGUASAAN_BADGE[log.tingkat_pemahaman as TingkatPemahaman];
                  return (
                    <tr key={log.id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{idx + 1}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280", whiteSpace: "nowrap" }}>{log.tanggal ?? "—"}</td>
                      <td style={{ padding: "12px 14px", fontWeight: 500, color: "#111827" }}>{log.topik ?? "—"}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{log.durasi_menit ? `${log.durasi_menit} mnt` : "—"}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{log.metode_belajar ?? "—"}</td>
                      <td style={{ padding: "12px 14px" }}>
                        <span style={{ background: badge.bg, color: badge.color, borderRadius: 6, padding: "3px 10px", fontSize: 12, fontWeight: 600 }}>
                          {log.tingkat_pemahaman}
                        </span>
                      </td>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{log.tingkat_keterlibatan ?? "—"}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280", maxWidth: 200 }}>
                        <span style={{ display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                          {log.catatan || "—"}
                        </span>
                      </td>
                      <td style={{ padding: "12px 14px" }}>
                        <button
                          onClick={() => onEditLog(log.id)}
                          style={{ background: "#f59e0b", color: "#fff", border: "none", borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer" }}
                        >
                          Edit
                        </button>
                      </td>
                    </tr>
                  );
                })}

                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={9} style={{ padding: "40px 14px", textAlign: "center", color: "#9ca3af", fontSize: 13 }}>
                      {activeTab === "Semua"
                        ? "Belum ada log untuk siswa ini."
                        : `Tidak ada log dengan pemahaman "${activeTab}".`}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DailyLogDetailSiswa;