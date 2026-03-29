import React from "react";
import type { MakulEntry } from "../components/types";
import { btnAddStyle } from "../components/constants";

interface DailyLogIndexProps {
  data: MakulEntry[];
  onAddMakul: () => void;
  onDetail: (id: number) => void;
}

const DailyLogIndex: React.FC<DailyLogIndexProps> = ({ data, onAddMakul, onDetail }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* Page heading */}
      <div style={{ marginBottom: 20, flexShrink: 0 }}>
        <h2 style={{ fontSize: 24, fontWeight: 700, color: "#111827", margin: "0 0 4px" }}>
          Daily Log
        </h2>
        <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
          Catatan aktivitas belajar siswa
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
            Daftar Log Aktivitas
          </span>
          <button onClick={onAddMakul} style={btnAddStyle}>
            + Tambah Data
          </button>
        </div>

        {/* Scrollable table */}
        <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "rgba(228,230,239,0.85)" }}>
                {[
                  { label: "No",              width: 50     },
                  { label: "Mata Pelajaran",  width: "auto" },
                  { label: "Jumlah Siswa",    width: "auto" },
                  { label: "Deskripsi",       width: "auto" },
                  { label: "Actions",         width: 100    },
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
              {data.map((row, idx) => {
                return (
                  <tr key={row.id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                    <td style={{ padding: "12px 14px", color: "#6b7280" }}>{idx + 1}</td>
                    <td style={{ padding: "12px 14px", color: "#374151" }}>{row.nama}</td>
                    <td style={{ padding: "12px 14px", color: "#374151" }}>{row.jumlahSiswa}</td>
                    <td style={{ padding: "12px 14px", color: "#111827" }}>{row.deskripsi}</td>
                    <td style={{ padding: "12px 14px" }}>
                      <button
                        onClick={() => onDetail(row.id)}
                        style={{
                          background: "#3b82f6", color: "#fff", border: "none",
                          borderRadius: 6, padding: "5px 12px",
                          fontSize: 12, fontWeight: 600, cursor: "pointer",
                        }}
                      >
                        Detail
                      </button>
                    </td>
                  </tr>
                );
              })}

              {data.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ padding: "40px 14px", textAlign: "center", color: "#9ca3af", fontSize: 13 }}>
                    Belum ada data log.
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

export default DailyLogIndex;