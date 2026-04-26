import { useCallback, useEffect, useRef, useState } from "react";
import type { KelasResponse, SiswaResponse, MapelResponse } from "../../service/payload";
import { useKelasApi } from "../master-kelas/useKelasApi";
import { IconClose, IconPlus, IconTrash } from "../../icons";
import type { Siswa, Toast } from "../../types";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import { addSiswaKelas, deleteSiswaKelas } from "../../service/kelasAPI";
import { useLearningPlan } from "../learning-plan/useLearningPlan";
import { useMapelApi } from "../master-mapel/useMapelApi";

// ─────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────
interface DetailKelasProps {
  kelasId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

type ModalMode = "add-siswa" | "confirm-delete" | "confirm-generate" | null;

// ─────────────────────────────────────────────
// Helper: map API → internal Siswa type
// Defined outside component to avoid recreating on every render
// ─────────────────────────────────────────────
const mapApiToSiswa = (data: SiswaResponse): Siswa => ({
  id: data.id,
  nama: data.nama,
  email_address: data.email_address,
  jenis_kelamin: data.jenis_kelamin,
  education_level: data.education_level,
  is_active: data.is_active,
});

// ─────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────
const s = {
  root: {
    fontFamily: "'Plus Jakarta Sans', 'Segoe UI', sans-serif",
    background: "#F8FAFC",
    minHeight: "100vh",
    padding: "24px",
    boxSizing: "border-box" as const,
  },
  backBtn: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "none",
    border: "1px solid #E2E8F0",
    color: "#475569",
    borderRadius: "8px",
    padding: "7px 14px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
    marginBottom: "20px",
    transition: "all 0.15s",
  },
  pageTitle: {
    fontSize: "22px",
    fontWeight: 800,
    color: "#0F172A",
    margin: 0,
  },
  pageSubtitle: {
    fontSize: "13px",
    color: "#94A3B8",
    margin: "4px 0 24px",
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "1fr 300px",
    gap: "20px",
    alignItems: "start",
  },
  card: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: "12px",
    padding: "20px",
    marginBottom: "16px",
  },
  infoGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "14px",
  },
  infoLabel: {
    fontSize: "11px",
    fontWeight: 700,
    color: "#94A3B8",
    textTransform: "uppercase" as const,
    letterSpacing: "0.06em",
    display: "block",
    marginBottom: "3px",
  },
  infoValue: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#1E293B",
  },
  toolbar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "14px",
  },
  sectionTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#1E293B",
    margin: 0,
  },
  badge: {
    display: "inline-flex",
    alignItems: "center",
    background: "#EEF2FF",
    color: "#4338CA",
    borderRadius: "999px",
    padding: "2px 10px",
    fontSize: "11px",
    fontWeight: 700,
    marginLeft: "8px",
  },
  btnPrimary: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "8px 14px",
    fontSize: "13px",
    fontWeight: 700,
    cursor: "pointer",
  },
  siswaRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "10px 12px",
    background: "#F8FAFC",
    border: "1px solid #F1F5F9",
    borderRadius: "8px",
    marginBottom: "8px",
    transition: "border-color 0.15s",
  },
  siswaName: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#1E293B",
  },
  actionGroup: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    flexShrink: 0,
  },
  btnOutline: {
    display: "inline-flex",
    alignItems: "center",
    gap: "5px",
    border: "1px solid #E2E8F0",
    background: "#F8FAFC",
    borderRadius: "7px",
    padding: "6px 12px",
    fontSize: "12px",
    fontWeight: 600,
    color: "#475569",
    whiteSpace: "nowrap" as const,
    cursor: "pointer",
  },
  btnDanger: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    border: "1px solid #FCA5A5",
    background: "#FFF5F5",
    color: "#DC2626",
    borderRadius: "7px",
    padding: "6px 8px",
    cursor: "pointer",
    fontSize: "13px",
  },
  emptyState: {
    textAlign: "center" as const,
    padding: "32px 16px",
    color: "#94A3B8",
    fontSize: "13px",
    fontStyle: "italic" as const,
  },
  // Right panel
  rightCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: "12px",
    padding: "20px",
  },
  mapelName: {
    fontSize: "18px",
    fontWeight: 800,
    color: "#1E293B",
    marginBottom: "4px",
  },
  mapelBadge: {
    display: "inline-block",
    fontSize: "10px",
    fontWeight: 700,
    textTransform: "uppercase" as const,
    letterSpacing: "0.08em",
    background: "#F0FDF4",
    color: "#16A34A",
    borderRadius: "999px",
    padding: "2px 10px",
  },
  divider: {
    border: "none",
    borderTop: "1px solid #F1F5F9",
    margin: "16px 0",
  },
  topikItem: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    fontSize: "13px",
    color: "#334155",
    padding: "7px 0",
    borderBottom: "1px solid #F8FAFC",
  },
  topikBullet: {
    width: "22px",
    height: "22px",
    background: "#EEF2FF",
    color: "#4338CA",
    borderRadius: "50%",
    fontSize: "11px",
    fontWeight: 700,
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
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
    padding: "16px",
  },
  modal: {
    background: "#fff",
    borderRadius: "14px",
    padding: "28px",
    width: "100%",
    maxWidth: "450px",
    boxShadow: "0 20px 60px rgba(0,0,0,0.18)",
    position: "relative" as const,
  },
  modalTitle: {
    fontSize: "16px",
    fontWeight: 800,
    color: "#0F172A",
    marginBottom: "4px",
  },
  modalSubtitle: {
    fontSize: "13px",
    color: "#64748B",
    marginBottom: "16px",
  },
  modalFooter: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px",
    marginTop: "20px",
  },
  btnCancel: {
    background: "#F1F5F9",
    color: "#475569",
    border: "none",
    borderRadius: "8px",
    padding: "9px 18px",
    fontSize: "13px",
    fontWeight: 700,
    cursor: "pointer",
  },
  btnSave: {
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "9px 18px",
    fontSize: "13px",
    fontWeight: 700,
    cursor: "pointer",
  },
  closeBtn: {
    position: "absolute" as const,
    top: "16px",
    right: "16px",
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "#94A3B8",
    fontSize: "18px",
    lineHeight: 1,
    padding: "2px",
  },
  // Loading skeleton
  skeleton: {
    background: "linear-gradient(90deg, #F1F5F9 25%, #E2E8F0 50%, #F1F5F9 75%)",
    backgroundSize: "200% 100%",
    animation: "shimmer 1.4s infinite",
    borderRadius: "6px",
  },
};

// ─────────────────────────────────────────────
// Loading Skeleton Sub-component
// ─────────────────────────────────────────────
function SkeletonBlock({ width = "100%", height = "16px", style = {} }: { width?: string; height?: string; style?: React.CSSProperties }) {
  return (
    <div
      style={{
        ...s.skeleton,
        width,
        height,
        ...style,
      }}
    />
  );
}

function DetailKelasSkeletonLoader() {
  return (
    <div style={s.layout}>
      <div>
        <div style={s.card}>
          <div style={s.infoGrid}>
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i}>
                <SkeletonBlock width="60%" height="11px" style={{ marginBottom: "6px" }} />
                <SkeletonBlock width="80%" height="16px" />
              </div>
            ))}
          </div>
        </div>
        <div style={s.card}>
          <div style={{ ...s.toolbar, marginBottom: "16px" }}>
            <SkeletonBlock width="120px" height="16px" />
            <SkeletonBlock width="100px" height="34px" style={{ borderRadius: "8px" }} />
          </div>
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} style={{ ...s.siswaRow, marginBottom: "8px" }}>
              <SkeletonBlock width="140px" height="14px" />
              <SkeletonBlock width="180px" height="30px" style={{ borderRadius: "7px" }} />
            </div>
          ))}
        </div>
      </div>
      <div style={s.rightCard}>
        <SkeletonBlock width="70%" height="22px" style={{ marginBottom: "10px" }} />
        <SkeletonBlock width="80px" height="18px" style={{ borderRadius: "999px", marginBottom: "16px" }} />
        <hr style={s.divider} />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "10px" }}>
            <SkeletonBlock width="22px" height="22px" style={{ borderRadius: "50%", flexShrink: 0 }} />
            <SkeletonBlock height="13px" />
          </div>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────
export default function DetailKelas({ kelasId, onNavigate }: DetailKelasProps) {
  const [kelas, setKelas] = useState<KelasResponse | null>(null);
  const [mapelObj, setMapelObj] = useState<MapelResponse | null>(null);
  const [siswaList, setSiswaList] = useState<Siswa[]>([]);
  const [siswaKelasList, setSiswaKelasList] = useState<Siswa[]>([]);
  const [loading, setLoading] = useState(true);
  const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);

  const [toasts, setToasts] = useState<Toast[]>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  const [selectedSiswaIds, setSelectedSiswaIds] = useState<string[]>([]);
  const [deleteSiswaId, setDeleteSiswaId] = useState<string | null>(null);
  const [isSavingSiswa, setIsSavingSiswa] = useState(false);
  const [isDeletingSiswa, setIsDeletingSiswa] = useState(false);

  // ✅ FIX: useRef for toastId — no shared module-level mutable state
  const toastIdRef = useRef(0);

  const { loadSiswa } = useSiswaApi();
  const { loadKelas, loadSiswaKelas } = useKelasApi();
  const { loadMapelList } = useMapelApi();
  const { submitGeneratePlan } = useLearningPlan();

  // ─────────────────────────────────────────────
  // Toast helper
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
  // ✅ FIX: Promise.allSettled — partial failures don't wipe all data
  // ─────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    Promise.allSettled([
      loadKelas(),
      loadSiswa(),
      loadSiswaKelas(kelasId),
      loadMapelList(),
    ]).then(([kelasResult, siswaResult, siswaKelasResult, mapelResult]) => {
      if (cancelled) return;

      // Kelas
      if (kelasResult.status === "fulfilled") {
        const kelasArr = Array.isArray(kelasResult.value) ? kelasResult.value : [];
        const currentKelas = kelasArr.find((k) => k.id === kelasId) ?? null;
        setKelas(currentKelas);

        // Mapel — resolve setelah kelas diketahui
        if (currentKelas?.mata_pelajaran_id && mapelResult.status === "fulfilled") {
          const mapelArr = Array.isArray(mapelResult.value) ? mapelResult.value : [];
          const found = mapelArr.find((m) => m.id === currentKelas.mata_pelajaran_id) ?? null;
          setMapelObj(found);
        }
      } else {
        showToast("Gagal memuat data kelas", "error");
      }

      // Siswa master
      if (siswaResult.status === "fulfilled") {
        const arr = Array.isArray(siswaResult.value) ? siswaResult.value : [];
        setSiswaList(arr.map(mapApiToSiswa));
      } else {
        showToast("Gagal memuat daftar siswa", "error");
      }

      // Siswa kelas
      if (siswaKelasResult.status === "fulfilled") {
        const arr = Array.isArray(siswaKelasResult.value) ? siswaKelasResult.value : [];
        setSiswaKelasList(arr.map(mapApiToSiswa));
      } else {
        showToast("Gagal memuat siswa kelas", "error");
      }

      setLoading(false);
    });

    return () => { cancelled = true; };
  }, [kelasId, loadKelas, loadSiswa, loadSiswaKelas, loadMapelList, showToast]);

  // ─────────────────────────────────────────────
  // Derived data
  // ─────────────────────────────────────────────
  const topikList = mapelObj?.topik_list?.map((t) => t.nama) ?? [];

  const availableSiswa = siswaList.filter(
    (s) => !siswaKelasList.some((ks) => ks.id === s.id)
  );

  const deleteSiswaTarget = deleteSiswaId
    ? siswaKelasList.find((s) => s.id === deleteSiswaId)
    : null;

  // ─────────────────────────────────────────────
  // Handlers
  // ─────────────────────────────────────────────
  const openAddSiswa = useCallback(() => {
    setSelectedSiswaIds([]);
    setModal("add-siswa");
  }, []);

  const closeModal = useCallback(() => {
    setModal(null);
    setDeleteSiswaId(null);
  }, []);

  const toggleSiswaSelection = useCallback((id: string, checked: boolean) => {
    setSelectedSiswaIds((prev) =>
      checked ? [...prev, id] : prev.filter((x) => x !== id)
    );
  }, []);

  // ✅ FIX: proper try/catch/finally
  const saveSiswa = useCallback(async () => {
    if (!kelasId || selectedSiswaIds.length === 0) {
      showToast("Pilih minimal 1 siswa", "error");
      return;
    }
    setIsSavingSiswa(true);
    try {
      await Promise.all(selectedSiswaIds.map((id) => addSiswaKelas(kelasId, { murid_id: id })));
      const updated = await loadSiswaKelas(kelasId);
      const updatedArr = Array.isArray(updated) ? updated : [];
      setSiswaKelasList(updatedArr.map(mapApiToSiswa));
      showToast(`${selectedSiswaIds.length} siswa berhasil ditambahkan`, "success");
      setModal(null);
      setSelectedSiswaIds([]);
    } catch {
      showToast("Gagal menambahkan beberapa siswa", "error");
    } finally {
      setIsSavingSiswa(false);
    }
  }, [kelasId, selectedSiswaIds, loadSiswaKelas, showToast]);

  // ✅ FIX: proper try/catch/finally; guard against missing target
  const confirmDeleteSiswa = useCallback(async () => {
    if (!deleteSiswaId) return;
    setIsDeletingSiswa(true);
    try {
      await deleteSiswaKelas(kelasId, deleteSiswaId);
      setSiswaKelasList((prev) => prev.filter((s) => s.id !== deleteSiswaId));
      showToast("Siswa berhasil dikeluarkan dari kelas", "success");
      setModal(null);
      setDeleteSiswaId(null);
    } catch {
      showToast("Gagal mengeluarkan siswa", "error");
    } finally {
      setIsDeletingSiswa(false);
    }
  }, [kelasId, deleteSiswaId, showToast]);

  // ✅ FIX: full try/catch/finally — isGeneratingPlan can never get stuck
  const handleGeneratePlan = useCallback(async () => {
    if (!kelas?.id) return;
    setModal(null);
    setIsGeneratingPlan(true);
    showToast("Mengoptimasi rencana belajar dengan AI...", "success");
    try {
      const result = await submitGeneratePlan(kelas.id);
      if (result) {
        showToast("Rencana studi kelas berhasil di-generate!", "success");
        onNavigate?.("planDetail", { kelas });
      } else {
        showToast("Gagal men-generate rencana studi", "error");
      }
    } catch {
      showToast("Terjadi kesalahan saat generate rencana studi", "error");
    } finally {
      setIsGeneratingPlan(false);
    }
  }, [kelas, submitGeneratePlan, onNavigate, showToast]);

  // ─────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────
  return (
    <div style={s.root}>
      {/* Shimmer keyframe — injected once */}
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <button style={s.backBtn} onClick={() => onNavigate?.("masterKelas")}>
        ← Kembali ke Master Kelas
      </button>

      <h2 style={s.pageTitle}>Detail Kelas</h2>
      <p style={s.pageSubtitle}>Informasi lengkap kelas dan daftar siswa</p>

      {/* ── Loading Skeleton ── */}
      {loading ? (
        <DetailKelasSkeletonLoader />
      ) : !kelas ? (
        <div style={s.emptyState}>Kelas tidak ditemukan.</div>
      ) : (
        <div style={s.layout}>

          {/* ── Left Panel ── */}
          <div>
            {/* Info Kelas */}
            <div style={s.card}>
              <div style={s.infoGrid}>
                <div>
                  <span style={s.infoLabel}>Nama Kelas</span>
                  <span style={s.infoValue}>Kelas {kelas.nama}</span>
                </div>
                <div>
                  <span style={s.infoLabel}>Mata Pelajaran</span>
                  <span style={s.infoValue}>{mapelObj?.nama_mata_pelajaran ?? "—"}</span>
                </div>
                <div>
                  <span style={s.infoLabel}>Hari</span>
                  <span style={s.infoValue}>{kelas.hari}</span>
                </div>
                <div>
                  <span style={s.infoLabel}>Jam</span>
                  <span style={s.infoValue}>{kelas.jam}</span>
                </div>
                <div>
                  <span style={s.infoLabel}>Jumlah Siswa</span>
                  <span style={s.infoValue}>{siswaKelasList.length} siswa</span>
                </div>
              </div>
            </div>

            {/* Daftar Siswa */}
            <div style={s.card}>
              <div style={s.toolbar}>
                <p style={s.sectionTitle}>
                  Daftar Siswa
                  <span style={s.badge}>{siswaKelasList.length}</span>
                </p>
                <button style={s.btnPrimary} onClick={openAddSiswa}>
                  <IconPlus /> Tambah Siswa
                </button>
              </div>

              {siswaKelasList.length === 0 ? (
                <div style={s.emptyState}>Belum ada siswa di kelas ini.</div>
              ) : (
                <div>
                  {siswaKelasList.map((siswa) => (
                    <div key={siswa.id} style={s.siswaRow}>
                      <div>
                        <div style={s.siswaName}>{siswa.nama}</div>
                        <div style={{ fontSize: "12px", color: "#94A3B8" }}>{siswa.education_level}</div>
                      </div>

                      <div style={s.actionGroup}>
                        {/* Buat Laporan */}
                        <button
                          type="button"
                          style={s.btnOutline}
                          onClick={() => {
                            if (!mapelObj) {
                              // mapel belum loaded, jangan navigasi
                              showToast("Data mapel belum tersedia", "error");
                              return;
                            }
                            onNavigate?.("reportEditor", {
                              siswaId: siswa.id,
                              kelasId: kelas.id,
                              siswa: siswa as unknown as SiswaResponse,
                              mapel: mapelObj,   // ← sudah dijamin non-null
                            });
                          }}
                        >
                          📝 Laporan
                        </button>

                        {/* Detail Sesi */}
                        <button
                          type="button"
                          style={s.btnOutline}
                          onClick={() =>
                            onNavigate?.("logSiswa", {
                              siswaId: siswa.id,
                              siswa,
                              mapel: mapelObj,
                              kelasId: kelas.id,
                            })
                          }
                        >
                          Detail Sesi
                        </button>

                        {/* Hapus */}
                        <button
                          type="button"
                          style={s.btnDanger}
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteSiswaId(siswa.id);
                            setModal("confirm-delete");
                          }}
                          title="Keluarkan siswa dari kelas"
                        >
                          <IconTrash />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* ── Right Panel ── */}
          {/* ✅ FIX: removed duplicate nested rightPanel div */}
          <div style={s.rightCard}>
            <div style={s.mapelName}>{mapelObj?.nama_mata_pelajaran ?? "—"}</div>
            <span style={s.mapelBadge}>Mata Pelajaran</span>

            <hr style={s.divider} />

            <p style={{ ...s.sectionTitle, fontSize: "11px", color: "#94A3B8", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "10px" }}>
              Kandungan Topik
            </p>

            {topikList.length === 0 ? (
              <div style={{ fontSize: "13px", color: "#94A3B8", fontStyle: "italic" }}>
                Belum ada topik untuk mapel ini.
              </div>
            ) : (
              topikList.map((topik, i) => (
                <div key={i} style={s.topikItem}>
                  <span style={s.topikBullet}>{i + 1}</span>
                  {topik}
                </div>
              ))
            )}

            <hr style={{ ...s.divider, marginTop: "16px" }} />

            {/* Generate Plan */}
            <button
              type="button"
              disabled={isGeneratingPlan}
              onClick={() => setModal("confirm-generate")}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "7px",
                width: "100%",
                background: isGeneratingPlan ? "#A5B4FC" : "#4F46E5",
                color: "#fff",
                border: "none",
                borderRadius: "9px",
                padding: "11px",
                fontSize: "13px",
                fontWeight: 700,
                cursor: isGeneratingPlan ? "not-allowed" : "pointer",
                marginBottom: "10px",
                transition: "background 0.2s",
              }}
            >
              {isGeneratingPlan ? (
                <>
                  <span style={{ display: "inline-block", animation: "spin 1s linear infinite" }}>⏳</span>
                  Memproses...
                </>
              ) : (
                "✦ Generate Plan Kelas"
              )}
            </button>

            {/* Lihat Jadwal */}
            <button
              type="button"
              onClick={() => onNavigate?.("planDetail", { kelas, mapelObj })}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "100%",
                background: "#F8FAFC",
                color: "#475569",
                border: "1px solid #E2E8F0",
                borderRadius: "9px",
                padding: "11px",
                fontSize: "13px",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Lihat Jadwal
            </button>
          </div>

        </div>
      )}

      {/* ────────────────────────────────────────
          MODAL: Tambah Siswa
      ──────────────────────────────────────── */}
      {modal === "add-siswa" && (
        // ✅ FIX: overlay click closes modal
        <div style={s.overlay} onClick={closeModal}>
          <div style={s.modal} onClick={(e) => e.stopPropagation()}>
            <button style={s.closeBtn} onClick={closeModal} aria-label="Tutup modal">
              <IconClose />
            </button>
            <div style={s.modalTitle}>Tambahkan Siswa ke Kelas</div>
            <div style={s.modalSubtitle}>Pilih siswa dari daftar master data</div>

            <div
              style={{
                maxHeight: "300px",
                overflowY: "auto",
                border: "1px solid #E2E8F0",
                borderRadius: "8px",
                padding: "8px",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
            >
              {availableSiswa.length === 0 ? (
                <div style={{ padding: "24px", textAlign: "center", color: "#94A3B8", fontSize: "13px" }}>
                  Semua siswa sudah masuk ke kelas ini.
                </div>
              ) : (
                availableSiswa.map((siswa) => {
                  const checked = selectedSiswaIds.includes(siswa.id);
                  return (
                    <label
                      key={siswa.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        padding: "10px 12px",
                        background: checked ? "#EEF2FF" : "#F8FAFC",
                        border: `1px solid ${checked ? "#C7D2FE" : "#E2E8F0"}`,
                        borderRadius: "7px",
                        cursor: "pointer",
                        transition: "all 0.15s",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(e) => toggleSiswaSelection(siswa.id, e.target.checked)}
                        style={{ width: "16px", height: "16px", cursor: "pointer", accentColor: "#4F46E5" }}
                      />
                      <div>
                        <div style={{ fontSize: "14px", fontWeight: 600, color: "#1E293B" }}>{siswa.nama}</div>
                        <div style={{ fontSize: "12px", color: "#64748B" }}>{siswa.education_level}</div>
                      </div>
                    </label>
                  );
                })
              )}
            </div>

            <p style={{ fontSize: "12px", color: "#64748B", marginTop: "8px", textAlign: "right" }}>
              Terpilih: <b>{selectedSiswaIds.length}</b> siswa
            </p>

            <div style={s.modalFooter}>
              <button style={s.btnCancel} onClick={closeModal}>Batal</button>
              <button
                style={{
                  ...s.btnSave,
                  opacity: selectedSiswaIds.length === 0 || isSavingSiswa ? 0.5 : 1,
                  cursor: selectedSiswaIds.length === 0 || isSavingSiswa ? "not-allowed" : "pointer",
                }}
                onClick={saveSiswa}
                disabled={selectedSiswaIds.length === 0 || isSavingSiswa}
              >
                {isSavingSiswa ? "Menyimpan..." : "Simpan ke Kelas"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────
          MODAL: Konfirmasi Hapus Siswa
      ──────────────────────────────────────── */}
      {modal === "confirm-delete" && deleteSiswaTarget && (
        // ✅ FIX: overlay click closes modal
        <div style={s.overlay} onClick={closeModal}>
          <div style={{ ...s.modal, maxWidth: "380px", textAlign: "center" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "36px", marginBottom: "12px" }}>⚠️</div>
            <div style={s.modalTitle}>Keluarkan Siswa?</div>
            <div style={s.modalSubtitle}>
              <b>{deleteSiswaTarget.nama}</b> akan dikeluarkan dari kelas ini.
              Aksi ini tidak dapat dibatalkan.
            </div>
            <div style={{ ...s.modalFooter, justifyContent: "center" }}>
              <button style={s.btnCancel} onClick={closeModal} disabled={isDeletingSiswa}>
                Batal
              </button>
              <button
                style={{
                  ...s.btnSave,
                  background: isDeletingSiswa ? "#FDA4AF" : "#E11D48",
                  cursor: isDeletingSiswa ? "not-allowed" : "pointer",
                }}
                onClick={confirmDeleteSiswa}
                disabled={isDeletingSiswa}
              >
                {isDeletingSiswa ? "Menghapus..." : "Ya, Keluarkan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────
          MODAL: Konfirmasi Generate Plan
          ✅ NEW: prevent accidental destructive action
      ──────────────────────────────────────── */}
      {modal === "confirm-generate" && (
        <div style={s.overlay} onClick={closeModal}>
          <div style={{ ...s.modal, maxWidth: "400px", textAlign: "center" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "36px", marginBottom: "12px" }}>✦</div>
            <div style={s.modalTitle}>Generate Rencana Belajar?</div>
            <div style={s.modalSubtitle}>
              Proses ini akan membuat rencana belajar baru menggunakan AI (PSO) untuk kelas{" "}
              <b>{kelas?.nama}</b>. Rencana sebelumnya akan digantikan.
            </div>
            <div style={{ ...s.modalFooter, justifyContent: "center" }}>
              <button style={s.btnCancel} onClick={closeModal}>Batal</button>
              <button
                style={{ ...s.btnSave, background: "#4F46E5" }}
                onClick={handleGeneratePlan}
              >
                Ya, Generate Sekarang
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ────────────────────────────────────────
          Toast Container
      ──────────────────────────────────────── */}
      <div
        style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          zIndex: 2000,
        }}
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            style={{
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
              animation: "fadeInUp 0.2s ease",
            }}
          >
            <span style={{ fontSize: "16px" }}>{t.type === "success" ? "✅" : "❌"}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => dismissToast(t.id)}
              style={{
                background: "none",
                border: "none",
                cursor: "pointer",
                color: "inherit",
                opacity: 0.6,
                fontSize: "14px",
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