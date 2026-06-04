import { useEffect, useState } from "react";
import type { KelasResponse, MailPayload, MapelResponse, ReportGeneratorResponse, SiswaResponse } from "../../service/payload";
import { styles, statusBadgeStyle, toastItemStyle } from "./styles";
import type { Toast } from "../../types";
import { IconTrash } from "../../icons";
import { useReport } from "../report-editor/useReport";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import { deleteReport } from "../../service/reportAPI";
import { useKelasApi } from "../master-kelas/useKelasApi";
import { useMapelApi } from "../master-mapel/useMapelApi";

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
  const [kelasList, setKelasList] = useState<KelasResponse[]>([]);
  const [mataPelajaranList, setMataPelajaranList] = useState<MapelResponse[]>([]);

  // ── Modal state ──────────────────────────────────────────────────────────
  const [kirimModal, setKirimModal] = useState<{ reportId: string } | null>(null);
  const [mailForm, setMailForm] = useState<MailPayload>(EMPTY_MAIL);
  const [sendingId, setSendingId] = useState<string | null>(null);

  const [deleteConfirm, setDeleteConfirm] = useState<{ reportId: string } | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const { errorMsg, loadReportBySiswa, submitSendReport } = useReport();
  const { loadKelas } = useKelasApi();
  const { loadSiswa } = useSiswaApi();
  const { loadMapelList } = useMapelApi();

  useEffect(() => {
    loadReportBySiswa(siswaId).then((data) => {
      if (data?.length) setReportList(data);
    });
    loadSiswa().then((data) => {
      if (data.length) setSiswaList(data);
    });
    loadKelas().then((data) => {
      if (data?.length) setKelasList(data);
    });
    loadMapelList().then((data) => {
      if (data?.length) setMataPelajaranList(data);
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
    <div style={styles.pageWrapper}>

      {/* ── Header ── */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.pageTitle}>Detail Report</h2>
          <p style={styles.pageSubtitle}>Detail report siswa</p>
        </div>
        <button onClick={() => onNavigate?.("listReportGen")} style={styles.btnBack}>
          ← Kembali
        </button>
      </div>

      {/* ── Body ── */}
      <div style={styles.scrollBody}>
        <div style={styles.tableCard}>

          {/* Filter bar */}
          <div style={styles.filterBar}>
            <div style={styles.filterBadge}>All Report ({count})</div>
          </div>

          {/* Table */}
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeadRow}>
                  {["No", "Tanggal", "Nama Siswa", "Mata Pelajaran", "Tipe Laporan", "Status", "Actions"].map((h) => (
                    <th key={h} style={styles.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {reportList.map((log, idx) => {
                  const kelas = kelasList.find((m) => m.id === log.kelas_id) ?? null;
                  const mapel = mataPelajaranList.find((m) => m.id === kelas?.mata_pelajaran_id) ?? null;

                  return (
                    <tr key={log.id} style={styles.tableBodyRow}>
                      <td style={styles.tdDefault}>{idx + 1}</td>
                      <td style={styles.tdDefault}>{log.tanggal?.split("T")[0] ?? "—"}</td>
                      <td style={styles.tdNoWrap}>{siswa?.nama ?? "—"}</td>
                      <td style={styles.tdNoWrap}>{mapel?.nama_mata_pelajaran ?? "—"}</td>
                      <td style={styles.tdBold}>{log.tipe_laporan ?? "—"}</td>
                      <td style={styles.tdBadge}>
                        <span style={statusBadgeStyle(log.status)}>{log.status ?? "—"}</span>
                      </td>
                      <td style={styles.tdActions}>
                        <div style={styles.actionGroup}>
                          {/* Edit — hanya saat draft */}
                          {log.status === "draft" && (
                            <button
                              onClick={(e) => { e.stopPropagation(); onNavigate?.("reportEditor", { reportData: log }); }}
                              style={styles.btnEdit}
                            >
                              Edit
                            </button>
                          )}

                          {/* Kirim — hanya saat final */}
                          {log.status === "final" && (
                            <button
                              onClick={(e) => { e.stopPropagation(); openKirim(log.id); }}
                              disabled={sendingId === log.id}
                              style={{ ...styles.btnKirim, opacity: sendingId === log.id ? 0.6 : 1 }}
                            >
                              {sendingId === log.id ? "Mengirim..." : "Kirim"}
                            </button>
                          )}

                          {/* View — hanya saat final */}
                          {log.status === "final" && (
                            <button
                              onClick={(e) => { e.stopPropagation(); onNavigate?.("reportEditor", { reportData: log }); }}
                              style={{ ...styles.btnView, opacity: sendingId === log.id ? 0.6 : 1 }}
                            >
                              View
                            </button>
                          )}

                          {/* Hapus — hanya saat draft */}
                          {log.status === "draft" && (
                            <button
                              style={{ ...styles.btnDanger, opacity: deletingId === log.id ? 0.6 : 1 }}
                              disabled={deletingId === log.id}
                              onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ reportId: log.id }); }}
                            >
                              <IconTrash />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                )}

                {reportList.length === 0 && (
                  <tr>
                    <td colSpan={6} style={styles.emptyCell}>
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
                style={{ ...styles.input, resize: "vertical", fontFamily: "inherit" }}
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
      <div style={styles.toastContainer}>
        {toasts.map((t) => (
          <div key={t.id} style={{ ...toastItemStyle(t.type), color: t.type === "success" ? "#15803D" : "#9F1239" }}>
            <span style={{ fontSize: 16 }}>{t.type === "success" ? "✅" : "❌"}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
              style={{ ...styles.toastCloseBtn, color: "inherit" }}
            >✕</button>
          </div>
        ))}
      </div>
    </div>
  );
}