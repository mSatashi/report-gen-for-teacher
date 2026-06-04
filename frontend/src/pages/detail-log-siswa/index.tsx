import { useEffect, useState } from "react";
import { useDailyLogSiswa } from "./useDailyLogSiswa";
import type { DailyLogResponse, MapelResponse, SiswaResponse } from "../../service/payload";
import type { TingkatPemahaman } from "../daily-log/components/types";
import { btnAddStyle, PENGUASAAN_BADGE } from "../daily-log/components/constants";
import { styles, statCardStyle, tabBtnStyle, thStyle, toastItemStyle } from "./styles";
import { deleteDailyLogApi } from "../../service/dailyLogAPI";
import type { Toast } from "../../types";
import { IconTrash } from "../../icons";

interface DailyLogDetailSiswaProps {
  siswa: SiswaResponse;
  mapel: MapelResponse;
  siswaId: string;
  kelasId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

const TABS = ["Semua", "Sangat Paham", "Paham", "Cukup", "Perlu Review"] as const;

let toastId = 0;

export default function DailyLogDetailSiswa({ siswa, siswaId, mapel, kelasId, onNavigate }: DailyLogDetailSiswaProps) {
  const [dailyList, setDailyList] = useState<DailyLogResponse[]>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<{ logId: string } | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);

  const { errorMsg, loadLogSiswa } = useDailyLogSiswa();

  useEffect(() => {
    loadLogSiswa(siswaId).then((data) => {
      if (data?.length) setDailyList(data);
    });
  }, []);

  const [activeTab, setActiveTab] = useState<typeof TABS[number]>("Semua");

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const countByLevel = (level: TingkatPemahaman) =>
    dailyList.filter((l) => l.tingkat_pemahaman as TingkatPemahaman === level).length;

  const filtered =
    activeTab === "Semua"
      ? dailyList
      : dailyList.filter((l) => l.tingkat_pemahaman === activeTab);

  const initials = siswa.nama.split(" ").map((w) => w[0]).slice(0, 2).join("");

  const deleteLog = async (logId: string) => {
    try {
      await deleteDailyLogApi(logId);
      setDailyList((prev) => prev.filter((k) => k.id !== logId));
      showToast("Log berhasil dihapus", "success");
    } catch {
      showToast(errorMsg ?? "Gagal menghapus log", "error");
    } finally {
      setDeleteConfirm(null);
    }
  };

  return (
    <div style={styles.pageWrapper}>

      {/* ── Header ── */}
      <div style={styles.header}>
        <div>
          {/* Breadcrumb */}
          <div style={styles.breadcrumbRow}>
            <span
              style={styles.breadcrumbLink}
              onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog"); }}
            >
              Daily Log
            </span>
            <span style={styles.breadcrumbSeparator}>›</span>
            <span
              style={styles.breadcrumbLink}
              onClick={(e) => { e.stopPropagation(); onNavigate?.("listSiswa"); }}
            >
              {mapel.nama_mata_pelajaran}
            </span>
            <span style={styles.breadcrumbSeparator}>›</span>
            <span style={styles.breadcrumbCurrent}>{siswa.nama}</span>
          </div>

          {/* Siswa info row */}
          <div style={styles.siswaInfoRow}>
            <div style={styles.avatar}>{initials}</div>
            <div>
              <h2 style={styles.siswaName}>{siswa.nama}</h2>
              <p style={styles.siswaMeta}>
                {siswa.education_level} · {mapel.nama_mata_pelajaran}
              </p>
            </div>
          </div>
        </div>

        <div style={styles.headerBtnGroup}>
          <button
            onClick={(e) => { e.stopPropagation(); onNavigate?.("detailKelas", { kelasId }); }}
            style={styles.btnBack}
          >
            ← Kembali
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog", { namaSiswa: siswa.nama, mapel, kelasId, siswa }); }}
            style={btnAddStyle}
          >
            + Tambah Log
          </button>
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div style={styles.scrollBody}>

        {/* Stat cards */}
        <div style={styles.statCardRow}>
          {[
            { label: "Total Log",    value: dailyList.length,             bg: "#eff6ff", color: "#3b82f6" },
            { label: "Sangat Paham", value: countByLevel("Sangat Paham"), bg: "#dcfce7", color: "#15803d" },
            { label: "Paham",        value: countByLevel("Paham"),        bg: "#dbeafe", color: "#1d4ed8" },
            { label: "Cukup",        value: countByLevel("Cukup"),        bg: "#fef9c3", color: "#ca8a04" },
            { label: "Perlu Review", value: countByLevel("Perlu Review"), bg: "#fee2e2", color: "#dc2626" },
          ].map((s) => (
            <div key={s.label} style={statCardStyle(s.bg)}>
              <div style={{ fontSize: 22, fontWeight: 700, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 12, color: s.color, fontWeight: 500, marginTop: 2 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Table card */}
        <div style={styles.tableCard}>

          {/* Tab filter */}
          <div style={styles.tabRow}>
            {TABS.map((tab) => {
              const active = activeTab === tab;
              const count  = tab === "Semua" ? dailyList.length : countByLevel(tab as TingkatPemahaman);
              const badge  = tab !== "Semua" ? PENGUASAAN_BADGE[tab as TingkatPemahaman] : null;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={tabBtnStyle(active, badge?.bg, badge?.color)}
                >
                  {tab} ({count})
                </button>
              );
            })}
          </div>

          {/* Table */}
          <div style={styles.tableWrapper}>
            <table style={styles.table}>
              <thead>
                <tr style={styles.tableHeadRow}>
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
                    <th key={h.label} style={thStyle(h.width)}>
                      {h.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((log, idx) => {
                  const badge = PENGUASAAN_BADGE[log.tingkat_pemahaman as TingkatPemahaman];
                  return (
                    <tr key={log.id} style={styles.tableBodyRow}>
                      <td style={styles.tdDefault}>{idx + 1}</td>
                      <td style={styles.tdNoWrap}>{log.tanggal ?? "—"}</td>
                      <td style={styles.tdBold}>{log.topik ?? "—"}</td>
                      <td style={styles.tdDefault}>{log.durasi_menit ? `${log.durasi_menit} mnt` : "—"}</td>
                      <td style={styles.tdDefault}>{log.metode_belajar ?? "—"}</td>
                      <td style={styles.tdBadge}>
                        <span style={{ background: badge?.bg, color: badge?.color, borderRadius: 6, padding: "3px 10px", fontSize: 12, fontWeight: 600 }}>
                          {log.tingkat_pemahaman}
                        </span>
                      </td>
                      <td style={styles.tdDefault}>{log.tingkat_keterlibatan ?? "—"}</td>
                      <td style={styles.tdNote}>
                        <span style={styles.noteClamp}>{log.catatan || "—"}</span>
                      </td>
                      <td style={styles.tdActions}>
                        <button
                          onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog", { namaSiswa: siswa.nama, mapel, kelasId, siswa, dataLog: log }); }}
                          style={styles.btnEdit}
                        >
                          Edit
                        </button>
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

                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={9} style={styles.emptyCell}>
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

      {/* ── Delete Confirm ── */}
      {deleteConfirm && (
        <div style={styles.overlay}>
          <div style={{ ...styles.modal, maxWidth: "360px" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "32px", textAlign: "center", marginBottom: "10px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center" }}>Hapus log?</div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button
                style={{ ...styles.btnSave, background: "#E11D48" }}
                onClick={() => deleteLog(deleteConfirm.logId)}
              >
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast Notifications ── */}
      <div style={styles.toastContainer}>
        {toasts.map((t) => (
          <div key={t.id} style={{ ...toastItemStyle(t.type), color: t.type === "success" ? "#15803D" : "#9F1239" }}>
            <span style={{ fontSize: "16px" }}>
              {t.type === "success" ? "✅" : "❌"}
            </span>
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