import { useCallback, useEffect, useRef, useState } from "react";
import { useDailyLogSiswa } from "./useDailyLogSiswa";
import type { DailyLogResponse, MapelResponse, SiswaResponse } from "../../service/payload";
import type { TingkatPemahaman } from "../daily-log/components/types";
import { btnAddStyle, PENGUASAAN_BADGE } from "../daily-log/components/constants";
import { deleteDailyLogApi } from "../../service/dailyLogAPI";
import type { Toast } from "../../types";

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────
interface DailyLogDetailSiswaProps {
  siswa: SiswaResponse;
  mapel: MapelResponse;
  siswaId: string;
  kelasId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

const TABS = ["Semua", "Sangat Paham", "Paham", "Cukup", "Perlu Review"] as const;
type Tab = (typeof TABS)[number];

// ─────────────────────────────────────────────
// Helpers: defined outside component
// ─────────────────────────────────────────────
const getInitials = (nama: string) =>
  nama.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();

// ─────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────
const s = {
  root: {
    fontFamily: "'Plus Jakarta Sans', 'Segoe UI', sans-serif",
    display: "flex",
    flexDirection: "column" as const,
    height: "100%",
    gap: 0,
  },
  // Header
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 20,
    flexWrap: "wrap" as const,
    gap: 12,
  },
  breadcrumb: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    marginBottom: 8,
  },
  breadcrumbLink: {
    fontSize: 13,
    color: "#94A3B8",
    cursor: "pointer",
    transition: "color 0.15s",
  },
  breadcrumbSep: {
    fontSize: 13,
    color: "#CBD5E1",
  },
  breadcrumbCurrent: {
    fontSize: 13,
    color: "#1E293B",
    fontWeight: 600,
  },
  avatarWrap: {
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: "50%",
    background: "#EEF2FF",
    color: "#4F46E5",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 15,
    fontWeight: 800,
    flexShrink: 0,
  },
  pageTitle: {
    fontSize: 22,
    fontWeight: 800,
    color: "#0F172A",
    margin: 0,
  },
  pageSubtitle: {
    fontSize: 13,
    color: "#94A3B8",
    margin: 0,
  },
  actionGroup: {
    display: "flex",
    gap: 10,
    alignItems: "center",
  },
  btnBack: {
    background: "none",
    border: "1px solid #E2E8F0",
    borderRadius: 8,
    padding: "8px 16px",
    fontSize: 13,
    fontWeight: 600,
    color: "#475569",
    cursor: "pointer",
  },
  // Body
  body: {
    flex: 1,
    overflowY: "auto" as const,
    display: "flex",
    flexDirection: "column" as const,
    gap: 16,
  },
  // Stats
  statsRow: {
    display: "flex",
    gap: 10,
    flexWrap: "wrap" as const,
  },
  statCard: (bg: string) => ({
    background: bg,
    borderRadius: 12,
    padding: "14px 18px",
    minWidth: 88,
    flex: "1 1 88px",
  }),
  statValue: (color: string) => ({
    fontSize: 22,
    fontWeight: 800,
    color,
  }),
  statLabel: (color: string) => ({
    fontSize: 11,
    fontWeight: 600,
    color,
    marginTop: 2,
  }),
  // Tab bar
  tabBar: {
    display: "flex",
    gap: 4,
    padding: "4px",
    background: "#F1F5F9",
    borderRadius: 10,
    width: "fit-content",
  },
  tab: (active: boolean) => ({
    padding: "6px 14px",
    borderRadius: 8,
    fontSize: 12,
    fontWeight: active ? 700 : 500,
    color: active ? "#4F46E5" : "#64748B",
    background: active ? "#fff" : "transparent",
    border: "none",
    cursor: "pointer",
    boxShadow: active ? "0 1px 4px rgba(0,0,0,0.08)" : "none",
    transition: "all 0.15s",
    whiteSpace: "nowrap" as const,
  }),
  // Table card
  tableCard: {
    background: "#fff",
    borderRadius: 14,
    padding: "0",
    boxShadow: "0 1px 4px rgba(0,0,0,.06)",
    overflow: "hidden",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse" as const,
    fontSize: 13,
  },
  thead: {
    background: "#F8FAFC",
    borderBottom: "1px solid #E2E8F0",
  },
  th: {
    padding: "11px 14px",
    textAlign: "left" as const,
    fontSize: 11,
    fontWeight: 700,
    color: "#94A3B8",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    whiteSpace: "nowrap" as const,
  },
  td: {
    padding: "12px 14px",
    verticalAlign: "middle" as const,
  },
  trHover: {
    borderBottom: "1px solid #F8FAFC",
  },
  emptyState: {
    textAlign: "center" as const,
    padding: "40px 20px",
    color: "#94A3B8",
    fontSize: 13,
    fontStyle: "italic" as const,
  },
  // Buttons in table
  btnEdit: {
    display: "inline-flex",
    alignItems: "center",
    background: "#FFFBEB",
    color: "#D97706",
    border: "1px solid #FDE68A",
    borderRadius: 6,
    padding: "5px 12px",
    cursor: "pointer",
    fontSize: 12,
    fontWeight: 700,
  },
  btnDanger: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#FFF5F5",
    color: "#DC2626",
    border: "1px solid #FCA5A5",
    borderRadius: 6,
    padding: "5px 8px",
    cursor: "pointer",
    fontSize: 13,
  },
  // Modal
  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(15,23,42,0.45)",
    backdropFilter: "blur(2px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: 16,
  },
  modal: {
    background: "#fff",
    borderRadius: 14,
    padding: 28,
    width: "100%",
    maxWidth: 380,
    boxShadow: "0 20px 60px rgba(0,0,0,0.18)",
    textAlign: "center" as const,
  },
  modalTitle: {
    fontSize: 16,
    fontWeight: 800,
    color: "#0F172A",
    marginBottom: 6,
  },
  modalSubtitle: {
    fontSize: 13,
    color: "#64748B",
    marginBottom: 4,
  },
  modalMeta: {
    fontSize: 12,
    color: "#94A3B8",
    marginBottom: 20,
  },
  modalFooter: {
    display: "flex",
    justifyContent: "center",
    gap: 10,
    marginTop: 20,
  },
  btnCancel: {
    background: "#F1F5F9",
    color: "#475569",
    border: "none",
    borderRadius: 8,
    padding: "9px 20px",
    fontSize: 13,
    fontWeight: 700,
    cursor: "pointer",
  },
  btnConfirmDelete: (loading: boolean) => ({
    background: loading ? "#FDA4AF" : "#E11D48",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    padding: "9px 20px",
    fontSize: 13,
    fontWeight: 700,
    cursor: loading ? "not-allowed" as const : "pointer" as const,
    opacity: loading ? 0.8 : 1,
  }),
  // Skeleton
  skeleton: {
    background: "linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%)",
    backgroundSize: "200% 100%",
    animation: "shimmer 1.4s infinite",
    borderRadius: 6,
  },
  // Loading row
  loadingWrap: {
    padding: "32px",
    textAlign: "center" as const,
    color: "#94A3B8",
    fontSize: 13,
  },
};

// ─────────────────────────────────────────────
// Skeleton row
// ─────────────────────────────────────────────
function SkeletonRow() {
  return (
    <tr style={{ borderBottom: "1px solid #F8FAFC" }}>
      {[40, 80, 140, 90, 80].map((w, i) => (
        <td key={i} style={s.td}>
          <div style={{ ...s.skeleton, width: w, height: 13 }} />
        </td>
      ))}
    </tr>
  );
}

// ─────────────────────────────────────────────
// Stats config
// ─────────────────────────────────────────────
const STAT_CONFIG: { label: string; level: TingkatPemahaman | "total"; bg: string; color: string }[] = [
  { label: "Total Log",    level: "total",        bg: "#EFF6FF", color: "#3B82F6" },
  { label: "Sangat Paham", level: "Sangat Paham", bg: "#DCFCE7", color: "#15803D" },
  { label: "Paham",        level: "Paham",        bg: "#DBEAFE", color: "#1D4ED8" },
  { label: "Cukup",        level: "Cukup",        bg: "#FEF9C3", color: "#CA8A04" },
  { label: "Perlu Review", level: "Perlu Review", bg: "#FEE2E2", color: "#DC2626" },
];

// ─────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────
export default function DailyLogDetailSiswa({
  siswa,
  siswaId,
  mapel,
  kelasId,
  onNavigate,
}: DailyLogDetailSiswaProps) {
  // ── All hooks at top ─────────────────────────
  const [dailyList, setDailyList]         = useState<DailyLogResponse[]>([]);
  const [loading, setLoading]             = useState(true);
  const [activeTab, setActiveTab]         = useState<Tab>("Semua");
  const [deleteLogId, setDeleteLogId]     = useState<string | null>(null);
  const [isDeleting, setIsDeleting]       = useState(false);
  const [toasts, setToasts]               = useState<Toast[]>([]);

  // ✅ FIX: useRef — no shared module-level mutable state
  const toastIdRef = useRef(0);

  const { loadLogSiswa } = useDailyLogSiswa();

  // ─────────────────────────────────────────────
  // Toast helpers
  // ─────────────────────────────────────────────
  const showToast = useCallback((message: string, type: "success" | "error") => {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  }, []);

  const dismissToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  // ─────────────────────────────────────────────
  // Data loading
  // ✅ FIX: .catch() + loading state
  // ─────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    loadLogSiswa(siswaId)
      .then((data) => {
        if (cancelled) return;
        // ✅ Guard: API mungkin return object/null bukan array
        const arr = Array.isArray(data) ? data : [];
        setDailyList(arr);
      })
      .catch(() => {
        if (cancelled) return;
        showToast("Gagal memuat data log siswa", "error");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [siswaId, loadLogSiswa, showToast]);

  // ─────────────────────────────────────────────
  // Derived data
  // ─────────────────────────────────────────────
  const countByLevel = useCallback(
    (level: TingkatPemahaman) =>
      dailyList.filter((l) => (l.tingkat_pemahaman as TingkatPemahaman) === level).length,
    [dailyList]
  );

  const filtered =
    activeTab === "Semua"
      ? dailyList
      : dailyList.filter((l) => l.tingkat_pemahaman === activeTab);

  // ✅ FIX: find delete target for meaningful modal info
  const deleteTarget = deleteLogId
    ? dailyList.find((l) => l.id === deleteLogId)
    : null;

  const initials = getInitials(siswa.nama);

  // ─────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────
  const openDeleteModal = useCallback((logId: string) => {
    setDeleteLogId(logId);
  }, []);

  const closeDeleteModal = useCallback(() => {
    if (isDeleting) return; // prevent closing while deleting
    setDeleteLogId(null);
  }, [isDeleting]);

  // ✅ FIX: try/catch/finally; isDeleting prevents double-click
  const confirmDelete = useCallback(async () => {
    if (!deleteLogId) return;
    setIsDeleting(true);
    try {
      await deleteDailyLogApi(deleteLogId);
      setDailyList((prev) => prev.filter((l) => l.id !== deleteLogId));
      showToast("Log berhasil dihapus", "success");
      setDeleteLogId(null);
    } catch {
      showToast("Gagal menghapus log", "error");
    } finally {
      setIsDeleting(false);
    }
  }, [deleteLogId, showToast]);

  // ─────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────
  return (
    <div style={s.root}>
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeInSlide {
          from { opacity: 0; transform: translateX(10px); }
          to   { opacity: 1; transform: translateX(0); }
        }
      `}</style>

      {/* ── Header ── */}
      <div style={s.header}>
        <div>
          {/* Breadcrumb */}
          {/* ✅ FIX: breadcrumb destinations yang logis */}
          <div style={s.breadcrumb}>
            <span
              style={s.breadcrumbLink}
              onClick={() => onNavigate?.("masterKelas")}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#4F46E5")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#94A3B8")}
            >
              Master Kelas
            </span>
            <span style={s.breadcrumbSep}>›</span>
            <span
              style={s.breadcrumbLink}
              onClick={() => onNavigate?.("detailKelas", { kelasId })}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#4F46E5")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "#94A3B8")}
            >
              {mapel.nama_mata_pelajaran}
            </span>
            <span style={s.breadcrumbSep}>›</span>
            <span style={s.breadcrumbCurrent}>{siswa.nama}</span>
          </div>

          {/* Avatar + Nama */}
          <div style={s.avatarWrap}>
            <div style={s.avatar}>{initials}</div>
            <div>
              <h2 style={s.pageTitle}>{siswa.nama}</h2>
              <p style={s.pageSubtitle}>
                {siswa.education_level} · {mapel.nama_mata_pelajaran}
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={s.actionGroup}>
          <button
            style={s.btnBack}
            onClick={() => onNavigate?.("detailKelas", { kelasId })}
          >
            ← Kembali
          </button>
          <button
            style={btnAddStyle}
            onClick={() =>
              onNavigate?.("formDailyLog", {
                namaSiswa: siswa.nama,
                mapel,
                kelasId,
                siswa,
              })
            }
          >
            + Tambah Log
          </button>
        </div>
      </div>

      {/* ── Body ── */}
      <div style={s.body}>

        {/* Stats */}
        <div style={s.statsRow}>
          {STAT_CONFIG.map((stat) => {
            const value =
              stat.level === "total"
                ? dailyList.length
                : countByLevel(stat.level as TingkatPemahaman);
            return (
              <div key={stat.label} style={s.statCard(stat.bg)}>
                <div style={s.statValue(stat.color)}>{loading ? "—" : value}</div>
                <div style={s.statLabel(stat.color)}>{stat.label}</div>
              </div>
            );
          })}
        </div>

        {/* ✅ FIX: Tab bar sekarang dirender dan berfungsi */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
          <div style={s.tabBar}>
            {TABS.map((tab) => (
              <button
                key={tab}
                style={s.tab(activeTab === tab)}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
                {tab !== "Semua" && !loading && (
                  <span style={{
                    marginLeft: 5,
                    background: activeTab === tab ? "#EEF2FF" : "#E2E8F0",
                    color: activeTab === tab ? "#4F46E5" : "#94A3B8",
                    borderRadius: "999px",
                    padding: "1px 6px",
                    fontSize: 10,
                    fontWeight: 700,
                  }}>
                    {countByLevel(tab as TingkatPemahaman)}
                  </span>
                )}
              </button>
            ))}
          </div>
          <span style={{ fontSize: 12, color: "#94A3B8" }}>
            {loading ? "" : `${filtered.length} entri`}
          </span>
        </div>

        {/* ✅ FIX: Tabel dengan <thead>, kolom jelas, style konsisten */}
        <div style={s.tableCard}>
          <table style={s.table}>
            <thead style={s.thead}>
              <tr>
                <th style={{ ...s.th, width: 40 }}>#</th>
                <th style={s.th}>Tanggal</th>
                <th style={s.th}>Topik</th>
                <th style={s.th}>Tingkat Pemahaman</th>
                <th style={{ ...s.th, width: 120 }}>Aksi</th>
              </tr>
            </thead>
            <tbody>
              {/* ✅ FIX: loading skeleton rows */}
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} style={s.emptyState}>
                    {activeTab === "Semua"
                      ? "Belum ada data log untuk siswa ini."
                      : `Tidak ada log dengan status "${activeTab}".`}
                  </td>
                </tr>
              ) : (
                filtered.map((log, idx) => {
                  const badge =
                    PENGUASAAN_BADGE[log.tingkat_pemahaman as keyof typeof PENGUASAAN_BADGE] ?? {
                      bg: "#F3F4F6",
                      color: "#6B7280",
                    };

                  return (
                    <tr
                      key={log.id}
                      style={s.trHover}
                    >
                      <td style={{ ...s.td, color: "#94A3B8", fontWeight: 600 }}>
                        {idx + 1}
                      </td>
                      <td style={{ ...s.td, color: "#475569" }}>
                        {log.tanggal ?? "—"}
                      </td>
                      <td style={{ ...s.td, fontWeight: 600, color: "#1E293B" }}>
                        {log.topik ?? "—"}
                      </td>
                      <td style={s.td}>
                        <span
                          style={{
                            background: badge.bg,
                            color: badge.color,
                            borderRadius: 6,
                            padding: "3px 10px",
                            fontWeight: 700,
                            fontSize: 11,
                            whiteSpace: "nowrap",
                          }}
                        >
                          {log.tingkat_pemahaman ?? "—"}
                        </span>
                      </td>
                      <td style={s.td}>
                        <div style={{ display: "flex", gap: 6 }}>
                          {/* ✅ FIX: style konsisten dengan sistem desain */}
                          <button
                            style={s.btnEdit}
                            onClick={() =>
                              onNavigate?.("formDailyLog", {
                                namaSiswa: siswa.nama,
                                mapel,
                                kelasId,
                                siswa,
                                dataLog: log,
                              })
                            }
                          >
                            ✏️ Edit
                          </button>
                          <button
                            style={s.btnDanger}
                            onClick={() => openDeleteModal(log.id)}
                            title="Hapus log ini"
                          >
                            🗑
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ────────────────────────────────────────
          MODAL: Konfirmasi Hapus Log
          ✅ FIX: overlay click closes modal
          ✅ FIX: tampilkan info log yang akan dihapus
          ✅ FIX: isDeleting state mencegah double-click
      ──────────────────────────────────────── */}
      {deleteLogId && (
        <div style={s.overlay} onClick={closeDeleteModal}>
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: 34, marginBottom: 12 }}>🗑️</div>
            <div style={s.modalTitle}>Hapus Log Ini?</div>

            {/* ✅ FIX: info log yang akan dihapus ditampilkan */}
            {deleteTarget ? (
              <>
                <div style={s.modalSubtitle}>
                  Topik: <b>{deleteTarget.topik ?? "—"}</b>
                </div>
                <div style={s.modalMeta}>
                  {deleteTarget.tanggal ?? "Tanggal tidak tersedia"} · {deleteTarget.tingkat_pemahaman ?? "—"}
                </div>
              </>
            ) : (
              <div style={s.modalSubtitle}>Aksi ini tidak dapat dibatalkan.</div>
            )}

            <div style={s.modalFooter}>
              <button
                style={s.btnCancel}
                onClick={closeDeleteModal}
                disabled={isDeleting}
              >
                Batal
              </button>
              <button
                style={s.btnConfirmDelete(isDeleting)}
                onClick={confirmDelete}
                disabled={isDeleting}
              >
                {isDeleting ? "Menghapus..." : "Ya, Hapus"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────
          Toast Container
          ✅ FIX: full styling — success/error colors, animation, dismiss button
      ──────────────────────────────────────── */}
      <div
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          display: "flex",
          flexDirection: "column",
          gap: 10,
          zIndex: 2000,
        }}
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              background: t.type === "success" ? "#F0FDF4" : "#FFF1F2",
              border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`,
              color: t.type === "success" ? "#15803D" : "#9F1239",
              borderRadius: 10,
              padding: "12px 16px",
              fontSize: 13,
              fontWeight: 600,
              boxShadow: "0 4px 16px rgba(0,0,0,0.10)",
              minWidth: 260,
              maxWidth: 360,
              animation: "fadeInUp 0.2s ease",
            }}
          >
            <span style={{ fontSize: 16 }}>{t.type === "success" ? "✅" : "❌"}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => dismissToast(t.id)}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                color: "inherit",
                opacity: 0.6,
                fontSize: 14,
                padding: "0 2px",
              }}
              aria-label="Tutup notifikasi"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}