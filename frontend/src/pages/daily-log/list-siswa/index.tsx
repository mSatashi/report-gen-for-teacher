import React from "react";
import type { LogEntry, MapelSiswaState } from "../components/types";
import { PENGUASAAN_BADGE, btnAddStyle } from "../components/constants";

interface DailyListSiswaProps {
  siswaData: MapelSiswaState[];
  logData: LogEntry[];
  onDetail: (siswaId: number) => void;
  onAddSiswa: () => void;
  onBack: () => void;
  namaMapel?: string;
}

const DailyListSiswa: React.FC<DailyListSiswaProps> = ({
  siswaData,
  logData,
  namaMapel,
  onDetail,
  onAddSiswa,
  onBack,
}) => {
  /** Hitung ringkasan log per siswa */
  const getSiswaStats = (namaSiswa: string) => {
    const logs = logData.filter((l) => l.siswa === namaSiswa);
    const lastLog = logs[logs.length - 1];
    return { total: logs.length, lastLog };
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* Page heading */}
      <div style={{ marginBottom: 20, flexShrink: 0 }}>
        {namaMapel && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <span onClick={onBack} style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }}>
              Daily Log
            </span>
            <span style={{ fontSize: 13, color: "#d1d5db" }}>›</span>
            <span style={{ fontSize: 13, color: "#111827", fontWeight: 600 }}>{namaMapel}</span>
          </div>
        )}
        <h2 style={{ fontSize: 24, fontWeight: 700, color: "#111827", margin: "0 0 4px" }}>
          {namaMapel ? `Siswa — ${namaMapel}` : "Daftar Siswa"}
        </h2>
        <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
          {namaMapel
            ? `Daftar siswa yang mengikuti ${namaMapel}`
            : "Kelola data siswa dan lihat progres belajar"}
        </p>
      </div>

      {/* Card */}
      <div
        style={{
          background: "#fff",
          borderRadius: 14,
          padding: "24px 28px",
          boxShadow: "0 1px 4px rgba(0,0,0,.06)",
          flex: 1,
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Card header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexShrink: 0 }}>
          <span style={{ fontWeight: 700, fontSize: 16, color: "#111827" }}>
            List Siswa ({siswaData.length})
          </span>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <button
              onClick={onBack}
              style={{
                background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
                padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
              }}
            >
              ← Kembali
            </button>
            <button style={btnAddStyle}>
              Import Log
            </button>
          </div>
        </div>

        {/* Scrollable table */}
        <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "rgba(228,230,239,0.85)" }}>
                {[
                  { label: "No",             width: 50    },
                  { label: "Nama Siswa",     width: "auto" },
                  { label: "Kelas",          width: 100   },
                  { label: "Total Log",      width: 100   },
                  { label: "Log Terakhir",   width: "auto" },
                  { label: "Pemahaman",      width: 130   },
                  { label: "Actions",        width: 200   },
                ].map((h) => (
                  <th
                    key={h.label}
                    style={{
                      padding: "10px 14px",
                      textAlign: "left",
                      fontWeight: 600,
                      color: "#374151",
                      width: h.width,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {h.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {siswaData.map((siswa, idx) => {
                const { total, lastLog } = getSiswaStats(siswa.nama);
                const badge = lastLog ? PENGUASAAN_BADGE[lastLog.tingkat_penguasaan] : null;

                return (
                  <tr key={siswa.id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                    <td style={{ padding: "12px 14px", color: "#6b7280" }}>{idx + 1}</td>
                    <td style={{ padding: "12px 14px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        {/* Avatar inisial */}
                        <div
                          style={{
                            width: 32, height: 32, borderRadius: "50%",
                            background: "#eff6ff", color: "#3b82f6",
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: 12, fontWeight: 700, flexShrink: 0,
                          }}
                        >
                          {siswa.nama.split(" ").map((w) => w[0]).slice(0, 2).join("")}
                        </div>
                        <span style={{ fontWeight: 500, color: "#111827" }}>{siswa.nama}</span>
                      </div>
                    </td>
                    <td style={{ padding: "12px 14px", color: "#6b7280" }}>{siswa.kelas}</td>
                    <td style={{ padding: "12px 14px" }}>
                      <span
                        style={{
                          background: total > 0 ? "#eff6ff" : "#f3f4f6",
                          color: total > 0 ? "#3b82f6" : "#9ca3af",
                          borderRadius: 6, padding: "3px 10px",
                          fontSize: 12, fontWeight: 600,
                        }}
                      >
                        {total} log
                      </span>
                    </td>
                    <td style={{ padding: "12px 14px", color: "#6b7280" }}>
                      {lastLog ? `${lastLog.mapel} — ${lastLog.materi}` : "—"}
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      {badge && lastLog ? (
                        <span
                          style={{
                            background: badge.bg,
                            color: badge.color,
                            borderRadius: 6,
                            padding: "3px 10px",
                            fontSize: 12,
                            fontWeight: 600,
                          }}
                        >
                          {lastLog.tingkat_penguasaan}
                        </span>
                      ) : (
                        <span style={{ color: "#9ca3af", fontSize: 12 }}>Belum ada log</span>
                      )}
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <button
                        onClick={() => onDetail(siswa.id)}
                        style={{
                          background: "#3b82f6", color: "#fff", border: "none",
                          borderRadius: 6, padding: "5px 12px",
                          fontSize: 12, fontWeight: 600, cursor: "pointer",
                        }}
                      >
                        Detail
                      </button>
                      <button
                        style={{
                            background: "#f59e0b", color: "#fff", border: "none",
                            borderRadius: 8, padding: "5px 10px",
                            fontSize: 13, fontWeight: 700, cursor: "pointer",
                            display: "flex", alignItems: "center", gap: 6,
                        }}
                        >
                        ✦ Generate Report
                        </button>
                    </td>
                  </tr>
                );
              })}

              {siswaData.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ padding: "40px 14px", textAlign: "center", color: "#9ca3af", fontSize: 13 }}>
                    Belum ada data siswa.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DailyListSiswa;