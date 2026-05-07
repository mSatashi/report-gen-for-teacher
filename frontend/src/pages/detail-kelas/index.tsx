import { useCallback, useEffect, useState } from "react";
import type { addSiswaPayload, GenerateplanResponse, KelasResponse, MataPelajaranObj, ReportGeneratorPayload, SiswaResponse } from "../../service/payload";
import { useKelasApi } from "../master-kelas/useKelasApi";
import { styles } from "./styles";
import { IconClose, IconPlus, IconTrash } from "../../icons";
import type { Siswa, Toast } from "../../types";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import { addSiswaKelas, deleteSiswaKelas } from "../../service/kelasAPI";
import { useLearningPlan } from "../learning-plan/useLearningPlan";
import { useMapelApi } from "../master-mapel/useMapelApi";
import { useReport } from "../report-editor/useReport";
import { fetchLogSiswa } from "../../service/dailyLogAPI";

interface DetailKelasProps {
  kelasId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

type ModalMode = "add-siswa" | "edit-siswa" | null;

const emptyKelasSiswa = (): addSiswaPayload => ({
  murid_id: "",
});

let toastId = 0;

type RowStatus = "idle" | "loading" | "done" | "error";
interface RowState {
  status: RowStatus;
  result: GenerateplanResponse | null;
  errorMsg: string | null;
}

const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({ width: window.innerWidth });
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

// Helper: merge base style + optional overrides
const m = (...objs: (object | undefined | false)[]) =>
  Object.assign({}, ...objs.filter(Boolean));

export default function DetailKelas({ kelasId, onNavigate }: DetailKelasProps) {
  const [kelas, setKelas] = useState<KelasResponse | null>(null);
  const [siswaList, setSiswaList] = useState<SiswaResponse[]>([]);
  const [siswaKelasList, setSiswaKelasList] = useState<SiswaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [, setAddSiswaForm] = useState<addSiswaPayload>(emptyKelasSiswa());
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  const [selectedSiswaIds, setSelectedSiswaIds] = useState<string[]>([]);
  const [deleteConfirm, setDeleteConfirm] = useState<{ siswaId: string } | null>(null);
  const [rows, setRows] = useState<Record<string, RowState>>({});
  const [mataPelajaranList, setMataPelajaranList] = useState<MataPelajaranObj[]>([]);
  const [loadingReportId, setLoadingReportId] = useState<string | null>(null);
  
  const { width } = useWindowSize();
  const isMobile = width < 768;
  const isSmall = width < 480;

  const { loadSiswa } = useSiswaApi();
  const { errorMsg, loadKelas, loadSiswaKelas } = useKelasApi();
  const { submitGeneratePlan } = useLearningPlan();
  const { submitReportGenerator } = useReport();
  const { loadMapelList } = useMapelApi();

  const mapApiToSiswa = (data: SiswaResponse): Siswa => ({
    id: data.id,
    nama: data.nama,
    email_address: data.email_address,
    jenis_kelamin: data.jenis_kelamin,
    education_level: data.education_level,
    is_active: data.is_active,
  });

  useEffect(() => {
    loadKelas().then((data) => {
      setLoading(true);
      if (data?.length) {
        const found = data.find((k) => k.id === kelasId) ?? null;
        setKelas(found);
      }
      setLoading(false);
    });
    
    loadSiswa().then((data) => {
      if (data?.length) setSiswaList(data.map(mapApiToSiswa));
    });

    loadSiswaKelas(kelasId).then((data) => {
      if (data?.length) setSiswaKelasList(data.map(mapApiToSiswa));
    });

    loadMapelList().then((data) => {
      if (data?.length) setMataPelajaranList(data);
    });
  }, [kelasId]);

  const topikList = mataPelajaranList.find((m) => m.id === kelas?.mata_pelajaran_id)?.topik_list ?? [];
  const mataPelajaran = mataPelajaranList.find((m) => m.id === kelas?.mata_pelajaran_id) ?? null;

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const openAddSiswa = () => {
    setAddSiswaForm(emptyKelasSiswa());
    setModal("add-siswa");
  };

  const availableSiswa = siswaList.filter(
    (s) => !siswaKelasList.some((ks) => ks.id === s.id)
  );

  const saveSiswa = async () => {
    if (!kelasId) {
      showToast("Kelas belum dipilih", "error");
      return;
    }
    
    for (const siswaId of selectedSiswaIds) {
      const payload = { murid_id: siswaId };
      const result = await addSiswaKelas(kelasId, payload);

      if (result) {
        const updated = await loadSiswaKelas(kelasId);
        if (updated?.length) setSiswaKelasList(updated.map(mapApiToSiswa));
        showToast("Siswa berhasil ditambahkan", "success");
        setSelectedSiswaIds([]);
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal menambahkan siswa", "error");
        return;
      }
    }
  };

  const deleteSiswa = async (siswaId: string) => {
    try {
      await deleteSiswaKelas(kelasId, siswaId);
      setSiswaKelasList((prev) => prev.filter((k) => k.id !== siswaId));
      showToast("Siswa berhasil dihapus", "success");
    } catch {
      showToast(errorMsg ?? "Gagal menghapus siswa", "error");
    } finally {
      setDeleteConfirm(null);
    }
  };

  const doneCount = Object.values(rows).filter((r) => r.status === "done").length;
  const totalCount = mataPelajaranList.find((m) => m.id === kelas?.mata_pelajaran_id)?.topik_list?.length ?? 0;

  const handleGenerate = useCallback(async (kelas: KelasResponse) => {
    setRows((prev) => ({
      ...prev,
      [kelas.id]: { status: "loading", result: null, errorMsg: null },
    }));
    
    const result = await submitGeneratePlan(kelas.id);

    if (result) {
      setRows((prev) => ({
        ...prev,
        [kelas.id]: { status: "done", result, errorMsg: null },
      }));
    } else {
      setRows((prev) => ({
        ...prev,
        [kelas.id]: { status: "error", result: null, errorMsg: "Gagal generate plan. Coba lagi." },
      }));
    }
  }, [submitGeneratePlan]);

  const handleGenerateReport = useCallback(async (siswaId: string) => {
    setLoadingReportId(siswaId);
    try {
      const logSiswa = await fetchLogSiswa(siswaId);
      const logTerbaru = logSiswa.length > 10
        ? [...logSiswa]
            .sort((a, b) => b.created_at.localeCompare(a.created_at))
            .slice(0, 10)
        : logSiswa;

      const createdAtPertama = logTerbaru.reduce((min, item) =>
        item.created_at < min ? item.created_at : min, logTerbaru[0]?.created_at
      );

      const createdAtTerakhir = logTerbaru.reduce((max, item) =>
        item.created_at > max ? item.created_at : max, logTerbaru[0]?.created_at
      );

      const today = new Date().toISOString().split("T")[0];
      
      const payload: ReportGeneratorPayload = {
        murid_id: siswaId!,
        kelas_id: kelasId!,
        periode_mulai: createdAtPertama.split("T")[0] ?? today,
        periode_selesai: createdAtTerakhir.split("T")[0] ?? today,
        tipe_laporan: "Perkembangan",
      };
      
      const result = await submitReportGenerator(payload);

      if (result) {
        showToast(`Report berhasil digenerate`, "success");
        onNavigate?.('reportEditor', { reportData: result });
      } else {
        showToast(errorMsg ?? "Gagal membuat report", "error");
      }
    } finally {
      setLoadingReportId(null);
    }
  }, [submitReportGenerator, onNavigate]);

  return (
    <div style={m(styles.root, isMobile && styles.rootMobile)}>

      {/* ── Header ── */}
      <div style={m(styles.headerRow, isMobile && styles.headerRowMobile)}>
        <div style={styles.titleSection}>
          <h2 style={m(styles.pageTitle, isMobile && styles.pageTitleMobile)}>
            Detail Kelas
          </h2>
          <div style={styles.breadcrumb}>
            <span
              style={m(styles.breadcrumbText, isMobile && styles.breadcrumbTextMobile)}
              onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog"); }}
            >
              Detail Kelas
            </span>
            <span style={styles.breadcrumbSeparator}>›</span>
            <span
              style={m(styles.breadcrumbText, isMobile && styles.breadcrumbTextMobile)}
              onClick={(e) => { e.stopPropagation(); onNavigate?.("listSiswa"); }}
            >
              Informasi lengkap kelas dan daftar siswa
            </span>
          </div>
        </div>

        <div style={m(styles.backButtonWrapper, isMobile && styles.backButtonWrapperMobile)}>
          <button
            onClick={(e) => { e.stopPropagation(); onNavigate?.("masterKelas"); }}
            style={m(styles.backButton, isMobile && styles.backButtonMobile)}
          >
            ← Kembali
          </button>
        </div>
      </div>

      {loading ? (
        <div style={styles.loadingWrap}>Memuat data...</div>
      ) : !kelas ? (
        <div style={styles.loadingWrap}>Kelas tidak ditemukan.</div>
      ) : (
        <>
          {/* ── Progress Bar ── */}
          {doneCount > 0 && (
            <div style={m(styles.progressBar, isMobile && styles.progressBarMobile)}>
              <span>✓</span>
              <span>{doneCount} dari {totalCount} kelas sudah memiliki learning plan.</span>
              <div style={styles.progressBarInner}>
                <div style={{
                  width: `${Math.round((doneCount / totalCount) * 100)}%`,
                  background: "#16a34a",
                  borderRadius: 99,
                  height: "100%",
                  transition: "width .4s",
                }} />
              </div>
              <span style={styles.progressBarText}>
                {Math.round((doneCount / totalCount) * 100)}%
              </span>
            </div>
          )}

          {/* ── Main Layout ── */}
          <div style={m(styles.layout, isMobile && styles.layoutMobile)}>

            {/* ── Left Panel ── */}
            <div style={styles.leftPanel}>

              {/* Info Kelas */}
              <div style={m(styles.infoCard, isMobile && styles.infoCardMobile)}>
                <div style={m(
                  styles.infoGrid,
                  isMobile && styles.infoGridMobile,
                  isSmall && styles.infoGridSmall,
                )}>
                  <div style={styles.infoItem}>
                    <span style={styles.infoLabel}>Nama Kelas</span>
                    <span style={m(styles.infoValue, isMobile && styles.infoValueMobile)}>
                      Kelas {kelas.nama}
                    </span>
                  </div>
                  <div style={styles.infoItem}>
                    <span style={styles.infoLabel}>Mata Pelajaran</span>
                    <span style={m(styles.infoValue, isMobile && styles.infoValueMobile)}>
                      {mataPelajaranList.find((m) => m.id === kelas.mata_pelajaran_id)?.nama_mata_pelajaran ?? "-"}
                    </span>
                  </div>
                  <div style={styles.infoItem}>
                    <span style={styles.infoLabel}>Hari</span>
                    <span style={m(styles.infoValue, isMobile && styles.infoValueMobile)}>
                      {kelas.hari}
                    </span>
                  </div>
                  <div style={styles.infoItem}>
                    <span style={styles.infoLabel}>Jam</span>
                    <span style={m(styles.infoValue, isMobile && styles.infoValueMobile)}>
                      {kelas.jam}
                    </span>
                  </div>
                  <div style={styles.infoItem}>
                    <span style={styles.infoLabel}>Jumlah Siswa</span>
                    <span style={m(styles.infoValue, isMobile && styles.infoValueMobile)}>
                      {siswaKelasList.length} siswa
                    </span>
                  </div>
                </div>
              </div>

              {/* Daftar Siswa */}
              <div style={m(styles.infoCard, isMobile && styles.infoCardMobile)}>
                <div style={m(styles.toolbar, isMobile && styles.toolbarMobile)}>
                  <p style={styles.sectionTitle}>
                    Daftar Siswa
                    <span style={styles.siswaCountBadge}>
                      {siswaKelasList.length}
                    </span>
                  </p>
                  <button style={styles.btnPrimary} onClick={openAddSiswa}>
                    <IconPlus /> Tambah Siswa
                  </button>
                </div>

                {siswaKelasList.length === 0 ? (
                  <div style={styles.emptyState}>Belum ada siswa di kelas ini</div>
                ) : (
                  <div style={styles.siswaList}>
                    {siswaKelasList.map((siswa) => (
                      <div
                        key={siswa.id}
                        style={m(styles.siswaRow, isMobile && styles.siswaRowMobile)}
                      >
                        <div style={styles.siswaName}>{siswa.nama}</div>

                        <div style={m(styles.siswaActions, isMobile && styles.siswaActionsMobile)}>
                          {/* Generate Report */}
                          <button
                            type="button"
                            onClick={() => handleGenerateReport(siswa.id)}
                            style={styles.generateButton}
                          >
                            {loadingReportId === siswa.id ? (
                              <>
                                <span style={{
                                  width: 12, height: 12,
                                  border: "2px solid rgba(255,255,255,0.6)",
                                  borderTopColor: "transparent",
                                  borderRadius: "50%",
                                  display: "inline-block",
                                  animation: "spin 0.7s linear infinite",
                                }} />
                                Generating...
                              </>
                            ) : (
                              "Generate Report"
                            )}
                          </button>

                          {/* Detail */}
                          <button
                            style={styles.btnDetail}
                            onClick={() => onNavigate?.("logSiswa", {
                              siswaId: siswa.id,
                              siswa: siswa,
                              mapel: mataPelajaran,
                              kelasId: kelas.id,
                            })}
                          >
                            Detail
                          </button>

                          {/* Hapus */}
                          <button
                            style={styles.btnDanger}
                            onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ siswaId: siswa.id }); }}
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

            {/* ── Right Panel — Mapel & Topik ── */}
            <div style={m(styles.rightPanel, isMobile && styles.rightPanelMobile)}>
              <div style={m(styles.rightPanelBody, isMobile && styles.rightPanelBodyMobile)}>
                <div style={styles.mapelName}>
                  {mataPelajaranList.find((m) => m.id === kelas.mata_pelajaran_id)?.nama_mata_pelajaran ?? "-"}
                </div>
                <span style={styles.badge}>Mata Pelajaran</span>

                <hr style={styles.divider} />

                <p style={{ fontSize: "11px", color: "#64748B", marginBottom: "10px", letterSpacing: "0.04em", fontWeight: 600 }}>
                  LIST TOPIK
                </p>

                {topikList.length === 0 ? (
                  <div style={{ fontSize: "12px", color: "#CBD5E1" }}>Belum ada topik</div>
                ) : (
                  topikList.map((topik, i) => (
                    <div key={i} style={styles.topikItem}>
                      <span style={{
                        width: "20px",
                        height: "20px",
                        background: "#EEF2FF",
                        color: "#4338CA",
                        borderRadius: "50%",
                        fontSize: "10px",
                        fontWeight: 700,
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                      }}>
                        {i + 1}
                      </span>
                      {topik.nama}
                    </div>
                  ))
                )}
              </div>

              {/* Footer tombol */}
              <div style={m(styles.rightPanelFooter, isMobile && styles.rightPanelFooterMobile)}>
                <button
                  type="button"
                  onClick={() => handleGenerate(kelas)}
                  style={styles.btnGenerate}
                >
                  Generate Plan
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onNavigate?.("planDetail", {
                      kelas,
                      mapel: mataPelajaranList.find((m) => m.id === kelas.mata_pelajaran_id) ?? "-",
                    });
                  }}
                  style={styles.btnDetailPlan}
                >
                  Detail Plan
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ── Modal Tambah Siswa ── */}
      {modal && (
        <div style={styles.overlay}>
          <div
            style={m(styles.modal, isMobile && styles.modalMobile)}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              style={m(styles.closeBtn, isMobile && styles.closeBtnMobile)}
              onClick={() => setModal(null)}
            >
              <IconClose />
            </button>
            <div style={m(styles.modalTitle, isMobile && styles.modalTitleMobile)}>
              {modal === "add-siswa" ? "Tambah Siswa ke Kelas" : "Edit Siswa"}
            </div>
            <div style={m(styles.modalSubtitle, isMobile && styles.modalSubtitleMobile)}>
              Isi informasi siswa di bawah ini
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Siswa</label>
              <select
                multiple
                style={styles.select}
                value={selectedSiswaIds}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions).map((o) => o.value);
                  setSelectedSiswaIds(selected);
                }}
                required
              >
                {availableSiswa.map((siswa) => (
                  <option key={siswa.id} value={siswa.id}>
                    {siswa.nama}
                  </option>
                ))}
              </select>
              <p style={{ fontSize: 12, color: "#94A3B8", marginTop: 6 }}>
                Tahan Ctrl / Cmd untuk pilih lebih dari satu
              </p>
            </div>

            <div style={m(styles.modalFooter, isMobile && styles.modalFooterMobile)}>
              <button
                style={m(styles.btnCancel, isMobile && styles.btnCancelMobile)}
                onClick={() => setModal(null)}
              >
                Batal
              </button>
              <button
                style={m(styles.btnSave, isMobile && styles.btnSaveMobile)}
                onClick={saveSiswa}
              >
                {modal === "add-siswa" ? "Tambah Siswa" : "Simpan Perubahan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirm ── */}
      {deleteConfirm && (
        <div style={styles.overlay}>
          <div
            style={m(styles.modal, isMobile && styles.modalMobile, { maxWidth: "360px" })}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: "32px", textAlign: "center", marginBottom: "10px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center" }}>
              Hapus siswa "{siswaKelasList.find((k) => k.id === deleteConfirm.siswaId)?.nama}"?
            </div>
            <div style={m(styles.modalFooter, { justifyContent: "center" }, isMobile && styles.modalFooterMobile)}>
              <button
                style={m(styles.btnCancel, isMobile && styles.btnCancelMobile)}
                onClick={() => setDeleteConfirm(null)}
              >
                Batal
              </button>
              <button
                style={m(styles.btnSave, isMobile && styles.btnSaveMobile, { background: "#E11D48" })}
                onClick={() => deleteSiswa(deleteConfirm.siswaId)}
              >
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Toast Notifications ── */}
      <div style={m(styles.toastContainer, isMobile && styles.toastContainerMobile)}>
        {toasts.map((t) => (
          <div
            key={t.id}
            style={m(
              styles.toast,
              isMobile && styles.toastMobile,
              t.type === "success" ? styles.toastSuccess : styles.toastError,
            )}
          >
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
}