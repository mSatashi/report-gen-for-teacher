import { useEffect, useState } from "react";
import type { ReportGeneratorResponse, SiswaResponse } from "../../service/payload";
import { styles } from "./styles";
import type { Toast } from "../../types";
import { IconTrash } from "../../icons";
import { useReport } from "../report-editor/useReport";
import { useSiswaApi } from "../master-siswa/useSiswaApi";

interface DailyLogDetailSiswaProps {
  siswaId: string,
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

export default function DetailReport({ onNavigate, siswaId }: DailyLogDetailSiswaProps) {
  const [siswaList, setSiswaList] = useState<SiswaResponse[]>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<{ logId: string } | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const [reportList, setReportList] = useState<ReportGeneratorResponse[]>([]);

  const { loadReportBySiswa } = useReport();
  const { loadSiswa } = useSiswaApi();

  useEffect(() => {  
    loadReportBySiswa(siswaId).then((data) => {
      if (data?.length) setReportList(data);
    });

    loadSiswa().then((data) => {
      if (data.length) setSiswaList(data);
    });
  }, []);

  const siswa = siswaList.find((m) => m.id === siswaId) ?? null;


  // const showToast = (message: string, type: "success" | "error") => {
  //   const id = ++toastId;
  //   setToasts((prev) => [...prev, { id, message, type }]);
  //   setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  // };

  // const deleteLog = async (logId: string) => {
  //   try {
  //     await deleteDailyLogApi(logId);
  //     setDailyList((prev) => prev.filter((k) => k.id !== logId));
  //     showToast("Log berhasil dihapus", "success");
  //   } catch {
  //     showToast(errorMsg ?? "Gagal menghapus log", "error");
  //   } finally {
  //     setDeleteConfirm(null);
  //   }
  // };

  const count  = reportList.length;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* ── Header ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, flexShrink: 0, flexWrap: "wrap", gap: 12 }}>
        <div>

          {/* Siswa info row */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 2px" }}>
                Detail Report
              </h2>
              <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
                Detail report siswa
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button 
            onClick={(e) => { e.stopPropagation(); onNavigate?.("listReportGen") }}
            style={{ background: "none", border: "1px solid #e5e7eb", borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}>
            ← Kembali
          </button>
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>

        {/* Table card */}
        <div style={{ background: "#fff", borderRadius: 14, padding: "24px 28px", boxShadow: "0 1px 4px rgba(0,0,0,.06)", flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20, flexShrink: 0 }}>
            <div
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 8, padding: "6px 14px", fontSize: 12, fontWeight: 600,
                cursor: "pointer",
                // background: active ? (badge ? badge.bg : "#eff6ff") : "#fff",
                // color:      active ? (badge ? badge.color : "#3b82f6") : "#6b7280",
                transition: "all .15s",
              }}
            >
              All Report {count}
            </div>
          </div>

          {/* Table */}
          <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "rgba(228,230,239,0.85)" }}>
                  {[
                    { label: "No", width: 50     },
                    { label: "Tanggal", width: 110    },
                    { label: "Nama Siswa", width: 110    },
                    { label: "Tipe Laporan", width: "auto" },
                    { label: "Status", width: 80     },
                    { label: "Actions",      width: 100    },
                  ].map((h) => (
                    <th key={h.label} style={{ padding: "10px 14px", textAlign: "left", fontWeight: 600, color: "#374151", width: h.width, whiteSpace: "nowrap" }}>
                      {h.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reportList.map((log, idx) => {
                  return (
                    <tr key={log.id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{idx + 1}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{log?.tanggal}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280", whiteSpace: "nowrap" }}>{siswa?.nama ?? "—"}</td>
                      <td style={{ padding: "12px 14px", fontWeight: 500, color: "#111827" }}>{log.tipe_laporan ?? "—"}</td>
                      <td style={{ padding: "12px 14px", color: "#6b7280" }}>{log.status ?? "—"}</td>
                      <td style={{ padding: "12px 14px" }}>
                        {log.status === 'draft' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); onNavigate?.('reportEditor', { reportData: log}); }}
                          style={{ background: "#f59e0b", color: "#fff", border: "none", borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer" }}
                        >
                          Edit
                        </button>
                        )}
                        {log.status === 'final' && (
                        <button
                          onClick={(e) => { e.stopPropagation(); onNavigate?.('reportEditor', { reportData: log}); }}
                          style={{ background: "#f59e0b", color: "#fff", border: "none", borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer" }}
                        >
                          Edit
                        </button>
                        )}
                        <button
                          style={styles.btnDanger}
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ logId: log.id }); }}
                        >
                          <IconTrash />
                        </button>
                      </td>
                    </tr>
                  );
                })}

                {reportList.length === 0 && (
                  <tr>
                    <td colSpan={9} style={{ padding: "40px 14px", textAlign: "center", color: "#9ca3af", fontSize: 13 }}>
                      Belum ada report untuk siswa ini.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Delete Confirm ── */}
      {deleteConfirm && (
        <div style={styles.overlay}>
          <div style={{ ...styles.modal, maxWidth: "360px" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "32px", textAlign: "center", marginBottom: "10px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center" }}>
              Hapus log ? 
              {/* "{dailyList.find((k) => k.id === deleteConfirm.logId)?.nama}"? */}
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button
                style={{ ...styles.btnSave, background: "#E11D48" }}
                // onClick={() => deleteLog(deleteConfirm.logId)}
              >
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast Notifications ── */}
      <div style={{
        position: "fixed",
        bottom: "24px",
        right: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        zIndex: 2000,
      }}>
        {toasts.map((t) => (
          <div key={t.id} style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            background: t.type === "success" ? "#F0FDF4" : "#FFF1F2",
            border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`,
            color: t.type === "success" ? "#15803D" : "#9F1239",
            borderRadius: "10px",
            padding: "12px 16px",
            fontSize: "13px",
            fontWeight: 600,
            boxShadow: "0 4px 16px rgba(0,0,0,0.10)",
            minWidth: "260px",
            maxWidth: "360px",
            animation: "slideIn 0.2s ease",
          }}>
            <span style={{ fontSize: "16px" }}>
              {t.type === "success" ? "✅" : "❌"}
            </span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                color: "inherit",
                opacity: 0.6,
                fontSize: "14px",
                padding: "0 2px",
              }}
            >✕</button>
          </div>
        ))}
      </div>
    </div>
  );
};