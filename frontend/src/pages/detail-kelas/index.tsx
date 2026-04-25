import { useEffect, useState } from "react";
import type { addSiswaPayload, KelasResponse, SiswaResponse } from "../../service/payload";
import { useKelasApi } from "../master-kelas/useKelasApi";
import { styles } from "./styles";
import { IconClose, IconPlus, IconTrash } from "../../icons";
import type { Siswa, Toast } from "../../types";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import { addSiswaKelas, deleteSiswaKelas } from "../../service/kelasAPI";
// import type { Toast } from "../../types";

interface DetailKelasProps {
  kelasId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

type ModalMode = "add-siswa" | "edit-siswa" | null;

const emptyKelasSiswa = (): addSiswaPayload => ({
  murid_id: "",
});

let toastId = 0;

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

  const { loadSiswa } = useSiswaApi();
  const { errorMsg, loadKelas, loadSiswaKelas } = useKelasApi();

  const mapApiToSiswa = (data: SiswaResponse): Siswa => ({
    id: data.id,
    nama: data.nama,
    email_address: data.email_address,
    jenis_kelamin: data.jenis_kelamin,
    education_level: data.education_level,
    is_active: data.is_active,
  });

  useEffect(() => {
    
    // const fetchData = async () => {
    //   setLoading(true);
    //   try {
    //     // Load kelas list dan cari yang sesuai id
    //     const allKelas = await loadKelas();
    //     const found = allKelas.find((k) => k.id === kelasId) ?? null;
    //     setKelas(found);

    //     // Load siswa dalam kelas
    //     const siswa = await loadSiswaKelas(kelasId);
    //     setSiswaList(siswa ?? []);
    //   } finally {
    //     setLoading(false);
    //   }
    // };
    // fetchData();

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

  }, [kelasId]);

  const topikList = kelas?.mata_pelajaran_obj?.topik ?? [];

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const openAddSiswa = () => {
    setAddSiswaForm(emptyKelasSiswa());
    // setEditingKelasId(null);
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

  return (
    <div style={styles.root}>
      {/* Back button */}
      <button style={styles.backBtn} onClick={() => onNavigate?.("masterKelas")}>
        ← Kembali ke Master Kelas
      </button>

      <h2 style={styles.pageTitle}>Detail Kelas</h2>
      <p style={styles.pageSubtitle}>Informasi lengkap kelas dan daftar siswa</p>

      {loading ? (
        <div style={styles.loadingWrap}>Memuat data...</div>
      ) : !kelas ? (
        <div style={styles.loadingWrap}>Kelas tidak ditemukan.</div>
      ) : (
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
                    {kelas.mata_pelajaran_obj?.nama_mata_pelajaran ?? "-"}
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
                            style={styles.btnDetail}
                            onClick={() => onNavigate?.("logSiswa", { siswaId: siswa.id, siswa: siswa, mapel: kelas.mata_pelajaran_obj, kelasId: kelas.id })}
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
            <div style={styles.mapelName}>
              {kelas.mata_pelajaran_obj?.nama_mata_pelajaran ?? "-"}
            </div>
            <span style={styles.badge}>Mata Pelajaran</span>

            <hr style={styles.divider} />

            <p style={{ ...styles.sectionTitle, fontSize: "12px", color: "#64748B", marginBottom: "8px" }}>
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
                  {topik}
                </div>
              ))
            )}
          </div>
        </div>
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