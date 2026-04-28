import { useEffect, useState } from "react";
import type { MailPayload, ReportGeneratorResponse, SiswaResponse } from "../../service/payload";
import { styles } from "./styles";
import type { Toast } from "../../types";
import { IconTrash } from "../../icons";
import { useReport } from "../report-editor/useReport";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import { deleteReport } from "../../service/reportAPI";

interface DailyLogDetailSiswaProps {
  siswaId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

let toastId = 0;

const EMPTY_MAIL: MailPayload = {
  email_tujuan: "",
  catatan_tambahan: "",
};

export default function DetailReport({ onNavigate, siswaId }: DailyLogDetailSiswaProps) {
  const [siswaList, setSiswaList] = useState<SiswaResponse[]>([]);
  const [reportList, setReportList] = useState<ReportGeneratorResponse[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);

  // ── Modal state ──────────────────────────────────────────────────────────
  const [kirimModal, setKirimModal] = useState<{ reportId: string } | null>(null);
  const [mailForm, setMailForm] = useState<MailPayload>(EMPTY_MAIL);
  const [sendingId, setSendingId] = useState<string | null>(null);

  const [deleteConfirm, setDeleteConfirm] = useState<{ reportId: string } | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { errorMsg, loadReportBySiswa, submitSendReport } = useReport();
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

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  // ── Kirim ────────────────────────────────────────────────────────────────
  const openKirim = (reportId: string) => {
    setMailForm(EMPTY_MAIL);
    setKirimModal({ reportId });
  };

  const handleKirim = async () => {
    if (!kirimModal) return;
    if (!mailForm.email_tujuan.trim()) {
      showToast("Email tujuan wajib diisi", "error");
      return;
    }

    setSendingId(kirimModal.reportId);
    try {
      await submitSendReport(kirimModal.reportId, mailForm);
      showToast("Report berhasil dikirim ✓", "success");
      setKirimModal(null);
    } catch {
      showToast(errorMsg ?? "Gagal mengirim report", "error");
    } finally {
      setSendingId(null);
    }
  };

  // ── Hapus ────────────────────────────────────────────────────────────────
  const handleDelete = async () => {
    if (!deleteConfirm) return;

    setDeletingId(deleteConfirm.reportId);
    try {
      await deleteReport(deleteConfirm.reportId);
      setReportList((prev) => prev.filter((r) => r.id !== deleteConfirm.reportId));
      showToast("Report berhasil dihapus", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal menghapus report";
      showToast(msg, "error");
    } finally {
      setDeletingId(null);
      setDeleteConfirm(null);
    }
  };

  const count = reportList.length;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* ── Header ── */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, flexShrink: 0, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 2px" }}>
            Detail Report
          </h2>
          <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
            Detail report siswa
          </p>
        </div>
        <button
          onClick={() => onNavigate?.("listReportGen")}
          style={{ background: "none", border: "1px solid #e5e7eb", borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}
        >
          ← Kembali
        </button>
      </div>

      {/* ── Body ── */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>
        <div style={{ background: "#fff", borderRadius: 14, padding: "24px 28px", boxShadow: "0 1px 4px rgba(0,0,0,.06)", flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>

          {/* Filter bar */}
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20, flexShrink: 0 }}>
            <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: "6px 14px", fontSize: 12, fontWeight: 600, color: "#3b82f6", background: "#eff6ff" }}>
              All Report {count}
            </div>
          </div>

          {/* Table */}
          <div style={{ flex: 1, overflowY: "auto", minHeight: 0 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "rgba(228,230,239,0.85)" }}>
                  {["No", "Tanggal", "Nama Siswa", "Tipe Laporan", "Status", "Actions"].map((h) => (
                    <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontWeight: 600, color: "#374151", whiteSpace: "nowrap" }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reportList.map((log, idx) => (
                  <tr key={log.id} style={{ borderBottom: "1px solid #f3f4f6" }}>
                    <td style={{ padding: "12px 14px", color: "#6b7280" }}>{idx + 1}</td>
                    <td style={{ padding: "12px 14px", color: "#6b7280" }}>
                      {log.tanggal?.split("T")[0] ?? "—"}
                    </td>
                    <td style={{ padding: "12px 14px", color: "#6b7280", whiteSpace: "nowrap" }}>
                      {siswa?.nama ?? "—"}
                    </td>
                    <td style={{ padding: "12px 14px", fontWeight: 500, color: "#111827" }}>
                      {log.tipe_laporan ?? "—"}
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <span style={{
                        display: "inline-block",
                        padding: "3px 10px",
                        borderRadius: 20,
                        fontSize: 11,
                        fontWeight: 700,
                        background: log.status === "draft" ? "#FEF3C7" : log.status === "final" ? "#F0FDF4" : "#F3F4F6",
                        color: log.status === "draft" ? "#92400E" : log.status === "final" ? "#15803D" : "#6B7280",
                      }}>
                        {log.status ?? "—"}
                      </span>
                    </td>
                    <td style={{ padding: "12px 14px" }}>
                      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        {/* Edit — hanya saat draft */}
                        {log.status === "draft" && (
                          <button
                            onClick={(e) => { e.stopPropagation(); onNavigate?.("reportEditor", { reportData: log }); }}
                            style={{ background: "#f59e0b", color: "#fff", border: "none", borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer" }}
                          >
                            Edit
                          </button>
                        )}

                        {/* Kirim — hanya saat final */}
                        {log.status === "final" && (
                          <button
                            onClick={(e) => { e.stopPropagation(); openKirim(log.id); }}
                            disabled={sendingId === log.id}
                            style={{ background: "#22c55e", color: "#fff", border: "none", borderRadius: 6, padding: "5px 12px", fontSize: 12, fontWeight: 600, cursor: "pointer", opacity: sendingId === log.id ? 0.6 : 1 }}
                          >
                            {sendingId === log.id ? "Mengirim..." : "Kirim"}
                          </button>
                        )}

                        {/* Hapus */}
                        <button
                          style={{ ...styles.btnDanger, opacity: deletingId === log.id ? 0.6 : 1 }}
                          disabled={deletingId === log.id}
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ reportId: log.id }); }}
                        >
                          <IconTrash />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {reportList.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{ padding: "40px 14px", textAlign: "center", color: "#9ca3af", fontSize: 13 }}>
                      Belum ada report untuk siswa ini.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── Modal Kirim ── */}
      {kirimModal && (
        <div style={styles.overlay} onClick={() => setKirimModal(null)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button type="button" onClick={() => setKirimModal(null)} style={styles.closeBtn}>✕</button>

            <div style={styles.modalTitle}>📧 Kirim Report</div>
            <div style={styles.modalSubtitle}>Isi email tujuan untuk mengirim laporan ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Email Tujuan *</label>
              <input
                type="email"
                value={mailForm.email_tujuan}
                placeholder="contoh@email.com"
                onChange={(e) => setMailForm((f) => ({ ...f, email_tujuan: e.target.value }))}
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Catatan Tambahan</label>
              <textarea
                value={mailForm.catatan_tambahan}
                placeholder="Tulis catatan opsional..."
                rows={3}
                onChange={(e) => setMailForm((f) => ({ ...f, catatan_tambahan: e.target.value }))}
                style={{ ...styles.input, resize: "vertical" as const, fontFamily: "inherit" }}
              />
            </div>

            <div style={styles.modalFooter}>
              <button type="button" onClick={() => setKirimModal(null)} style={styles.btnCancel}>
                Batal
              </button>
              <button
                type="button"
                onClick={handleKirim}
                disabled={!!sendingId}
                style={{ ...styles.btnSave, opacity: sendingId ? 0.7 : 1, cursor: sendingId ? "not-allowed" : "pointer" }}
              >
                {sendingId ? "Mengirim..." : "Kirim Sekarang"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Modal Hapus ── */}
      {deleteConfirm && (
        <div style={styles.overlay} onClick={() => setDeleteConfirm(null)}>
          <div style={{ ...styles.modal, maxWidth: "360px" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "32px", textAlign: "center", marginBottom: "10px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center" }}>
              Yakin ingin menghapus report ini? Tindakan ini tidak dapat dibatalkan.
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>
                Batal
              </button>
              <button
                style={{ ...styles.btnSave, background: "#E11D48", opacity: deletingId ? 0.7 : 1, cursor: deletingId ? "not-allowed" : "pointer" }}
                disabled={!!deletingId}
                onClick={handleDelete}
              >
                {deletingId ? "Menghapus..." : "Ya, Hapus"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast ── */}
      <div style={{ position: "fixed", bottom: 24, right: 24, display: "flex", flexDirection: "column", gap: 10, zIndex: 2000 }}>
        {toasts.map((t) => (
          <div key={t.id} style={{
            display: "flex", alignItems: "center", gap: 10,
            background: t.type === "success" ? "#F0FDF4" : "#FFF1F2",
            border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`,
            color: t.type === "success" ? "#15803D" : "#9F1239",
            borderRadius: 10, padding: "12px 16px", fontSize: 13, fontWeight: 600,
            boxShadow: "0 4px 16px rgba(0,0,0,0.10)", minWidth: 260, maxWidth: 360,
          }}>
            <span style={{ fontSize: 16 }}>{t.type === "success" ? "✅" : "❌"}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
              style={{ background: "none", border: "none", cursor: "pointer", color: "inherit", opacity: 0.6, fontSize: 14 }}
            >✕</button>
          </div>
        ))}
      </div>
    </div>
  );
}