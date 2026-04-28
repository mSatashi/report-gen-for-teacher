import { useCallback, useEffect, useState } from "react";
import type { addSiswaPayload, GenerateplanResponse, KelasResponse, MapelResponse, MataPelajaranObj, SiswaResponse } from "../../service/payload";
import { useKelasApi } from "../master-kelas/useKelasApi";
import { styles } from "./styles";
import { IconClose, IconPlus, IconTrash } from "../../icons";
import type { Siswa, Toast } from "../../types";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import { addSiswaKelas, deleteSiswaKelas } from "../../service/kelasAPI";
// import { useLearningPlan } from "../learning-plan/useLearningPlan";
import { useMapelApi } from "../master-mapel/useMapelApi";
// import type { Toast } from "../../types";

interface DetailKelasProps {
  kelasId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
  mapel: MapelResponse,
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
  const [rows, ] = useState<Record<string, RowState>>({});
  const [mataPelajaranList, setMataPelajaranList] = useState<MataPelajaranObj[]>([]);

  const { loadSiswa } = useSiswaApi();
  const { errorMsg, loadKelas, loadSiswaKelas } = useKelasApi();
  // const { submitGeneratePlan } = useLearningPlan();
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
      if (data?.length) 
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
        
        showToast("Siswa berhasil ditambahkan ", "success");
        setSelectedSiswaIds([]);

        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal menambahkan siswa", "error");
        return; // stop jika salah satu gagal
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

  const handleGenerate = useCallback(async () => {
    // useCallback(async (kelas: KelasResponse) => {
    onNavigate?.('ReportEditor')
    // setRows((prev) => ({
    //   ...prev,
    //   [kelas.id]: { status: "loading", result: null, errorMsg: null },
    // }));
    
    // console.log("Generate plan untuk kelas", kelas.id);
    // const result = await submitGeneratePlan(kelas.id);
  
    //   if (result) {
    //     setRows((prev) => ({
    //       ...prev,
    //       [kelas.id]: { status: "done", result, errorMsg: null },
    //     }));
    //   } else {
    //     setRows((prev) => ({
    //       ...prev,
    //       [kelas.id]: { status: "error", result: null, errorMsg: "Gagal generate plan. Coba lagi." },
    //     }));
    //   }
    }, 
  // [submitGeneratePlan]);
  []);

  return (
    <div style={styles.root}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20, flexShrink: 0, flexWrap: "wrap", gap: 12 }}>
        <div>
          {/* Siswa info row */}
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 2px" }}>
                Detail Kelas
              </h2>
            </div>
          </div>
          {/* Breadcrumb: Daily Log › Matematika › Aisya Putri */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <span style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }} 
            onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog"); }}
            >
              Detail Kelas
            </span>
            <span style={{ fontSize: 13, color: "#d1d5db" }}>›</span>
            <span style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }} onClick={(e) => { e.stopPropagation(); onNavigate?.("listSiswa"); }}>
              Informasi lengkap kelas dan daftar siswa
            </span>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button 
            onClick={(e) => { e.stopPropagation(); onNavigate?.("masterKelas") }}
            style={{ background: "none", border: "1px solid #e5e7eb", borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}>
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
        {doneCount > 0 && (
          <div style={{
            background: "#f0fdf4",
            border: "1.5px solid #86efac",
            borderRadius: 10,
            padding: "11px 16px",
            fontSize: 13,
            color: "#166534",
            fontWeight: 500,
            display: "flex",
            alignItems: "center",
            gap: 10,
            marginBottom: 16,   // <-- beri jarak ke card di bawahnya
          }}>
            <span>✓</span>
            <span>{doneCount} dari {totalCount} kelas sudah memiliki learning plan.</span>
            <div style={{ flex: 1, background: "#bbf7d0", borderRadius: 99, height: 5, marginLeft: 4 }}>
              <div style={{
                width: `${Math.round((doneCount / totalCount) * 100)}%`,
                background: "#16a34a",
                borderRadius: 99,
                height: "100%",
                transition: "width .4s",
              }} />
            </div>
            <span style={{ fontSize: 12, fontWeight: 700 }}>
              {Math.round((doneCount / totalCount) * 100)}%
            </span>
          </div>
        )}

        <div style={styles.layout}>
          {/* ── Left Panel ── */}
          <div style={styles.leftPanel}>
            {/* Info Kelas */}
            <div style={styles.infoCard}>
              <div style={styles.infoGrid}>
                <div style={styles.infoItem}>
                  <span style={styles.infoLabel}>Nama Kelas</span>
                  <span style={styles.infoValue}>Kelas {kelas.nama}</span>
                </div>
                <div style={styles.infoItem}>
                  <span style={styles.infoLabel}>Mata Pelajaran</span>
                  <span style={styles.infoValue}>
                    {mataPelajaranList.find((m) => m.id === kelas.mata_pelajaran_id)?.nama_mata_pelajaran ?? "-"}
                  </span>
                </div>
                <div style={styles.infoItem}>
                  <span style={styles.infoLabel}>Hari</span>
                  <span style={styles.infoValue}>{kelas.hari}</span>
                </div>
                <div style={styles.infoItem}>
                  <span style={styles.infoLabel}>Jam</span>
                  <span style={styles.infoValue}>{kelas.jam}</span>
                </div>
                <div style={styles.infoItem}>
                  <span style={styles.infoLabel}>Jumlah Siswa</span>
                  <span style={styles.infoValue}>{siswaKelasList.length} siswa</span>
                </div>
              </div>
            </div>

            {/* Daftar Siswa */}
            <div style={styles.infoCard}>
              <div style={styles.toolbar}>
                <p style={styles.sectionTitle}>
                  Daftar Siswa
                  <span style={{
                    marginLeft: "8px",
                    background: "#EEF2FF",
                    color: "#4338CA",
                    borderRadius: "999px",
                    padding: "1px 10px",
                    fontSize: "11px",
                    fontWeight: 700,
                  }}>
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
                    <div key={siswa.id} style={styles.siswaRow}>
                      <div>
                        <div style={styles.siswaName}>{siswa.nama}</div>
                      </div>

                      <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                        flexShrink: 0,
                      }}>
                        <div style={styles.kelasActions}>
                          <button
                            type="button"
                            onClick={() => handleGenerate()}
                            style={{
                              display: "inline-flex", alignItems: "center", gap: 6,
                              border: "none", borderRadius: 8,
                              padding: "8px 14px", fontSize: 12, fontWeight: 700,
                              whiteSpace: "nowrap",
                            }}
                          >
                            Generate Report
                          </button>
                          <button
                            style={styles.btnDetail}
                            onClick={() => onNavigate?.("logSiswa", { siswaId: siswa.id, siswa: siswa, mapel: mataPelajaran, kelasId: kelas.id })}
                          >
                            Detail
                          </button>
                          <button
                            style={styles.btnDanger}
                            onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ siswaId: siswa.id }); }}
                          >
                            <IconTrash />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* ── Right Panel — Mapel & Topik ── */}
          <div style={styles.rightPanel}>
            {/* Body */}
            <div style={styles.rightPanelBody}>
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
            <div style={styles.rightPanelFooter}>
              <button
                type="button"
                onClick={() => handleGenerate()}
                style={styles.btnGenerate}
              >
                Generate Plan
              </button>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); onNavigate?.("planDetail", { kelas,  mapel: mataPelajaranList.find((m) => m.id === kelas.mata_pelajaran_id) ?? "-"}); }}
                style={styles.btnDetailPlan}
              >
                Detail Plan
              </button>
            </div>
          </div>
        </div>
        </>
      )}

      {/* ── Modal Kelas ── */}
      {modal && (
        <div style={styles.overlay}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>
              {modal === "add-siswa" ? "Tambah Siswa ke kelas" : "Edit Siswa"}
            </div>
            <div style={styles.modalSubtitle}>Isi informasi siswa di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Siswa</label>
              <select
                multiple
                style={styles.select}
                // value={addSiswaForm.murid_id}
                // onChange={(e) => setAddSiswaForm((f) => ({ ...f, murid_id: e.target.value }))}
                value={selectedSiswaIds}
                onChange={(e) => {
                  const selected = Array.from(e.target.selectedOptions).map((o) => o.value);
                  setSelectedSiswaIds(selected);
                }}
                required
              >
                {/* <option value="">-- Pilih Siswa --</option>
                {siswaList.map((data) => (
                  <option key={data.id} value={data.id}>{data.nama}</option>
                ))} */}
                {availableSiswa.map((siswa) => (
                  <option key={siswa.id} value={siswa.id}>
                    {siswa.nama}
                  </option>
                ))}
                <p style={{ fontSize: 12, color: "gray" }}>
                  Tahan Ctrl / Cmd untuk pilih lebih dari satu
                </p>
              </select>
            </div>

            <div style={styles.modalFooter}>
              <button style={styles.btnCancel} onClick={() => setModal(null)}>Batal</button>
              <button style={styles.btnSave} onClick={saveSiswa}>
                {modal === "add-siswa" ? "Tambah Siswa" : "Simpan Perubahan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirm ── */}
      {deleteConfirm && (
        <div style={styles.overlay}>
          <div style={{ ...styles.modal, maxWidth: "360px" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "32px", textAlign: "center", marginBottom: "10px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center" }}>
              Hapus siswa "
              {siswaKelasList.find((k) => k.id === deleteConfirm.siswaId)?.nama}"?
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button
                style={{ ...styles.btnSave, background: "#E11D48" }}
                onClick={() => deleteSiswa(deleteConfirm.siswaId)}
              >
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}

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
}