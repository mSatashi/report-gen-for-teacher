import { useEffect, useState } from "react";
import { IconClose, IconEdit, IconPlus, IconTrash } from "../../icons";
import { useKelasApi } from "./useKelasApi";
import type { KelasPayload, KelasResponse, MataPelajaranObj, Toast } from "../../service/payload";
import { useMapelApi } from "../master-mapel/useMapelApi";

type ModalMode = "add-kelas" | "edit-kelas" | null;

const HARI_MAP: Record<string, string> = {
  "Senin": "Senin", "Selasa": "Selasa", "Rabu": "Rabu", "Kamis": "Kamis",
  "Jumat": "Jumat", "Sabtu": "Sabtu", "Minggu": "Minggu",
};

const HARI_ORDER = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"];

const HARI_COLORS: Record<string, { bg: string; border: string; label: string }> = {
  Senin:  { bg: "#EEF2FF", border: "#818CF8", label: "#4338CA" },
  Selasa: { bg: "#F0FDF4", border: "#4ADE80", label: "#15803D" },
  Rabu:   { bg: "#FEF3C7", border: "#FCD34D", label: "#92400E" },
  Kamis:  { bg: "#FDF2F8", border: "#F0ABFC", label: "#86198F" },
  Jumat:  { bg: "#FFF7ED", border: "#FDBA74", label: "#9A3412" },
  Sabtu:  { bg: "#F0F9FF", border: "#38BDF8", label: "#075985" },
  Minggu: { bg: "#FFF1F2", border: "#FDA4AF", label: "#9F1239" },
};

const emptyKelasForm = () => ({
  nama: "",
  mata_pelajaran_id: "",
  hari: "",
  jam: "",
});

let toastId = 0;

const styles = {
  root: {
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
    background: "#F8FAFF",
    minHeight: "100vh",
    padding: "32px 28px",
    color: "#1E293B",
  } as React.CSSProperties,

  header: {
    marginBottom: "24px",
  } as React.CSSProperties,

  title: {
    fontSize: "22px",
    fontWeight: 700,
    color: "#0F172A",
    margin: 0,
  } as React.CSSProperties,

  subtitle: {
    fontSize: "13px",
    color: "#64748B",
    margin: "4px 0 0",
  } as React.CSSProperties,

  statsRow: {
    display: "flex",
    gap: "12px",
    marginBottom: "20px",
    flexWrap: "wrap" as const,
  } as React.CSSProperties,

  statBadge: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: "10px",
    padding: "10px 18px",
    fontSize: "13px",
    fontWeight: 600,
    color: "#334155",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
  } as React.CSSProperties,

  toolbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px",
  } as React.CSSProperties,

  btnPrimary: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "9px 16px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
  } as React.CSSProperties,

  scheduleGrid: {
    display: "flex",
    gap: "14px",
    overflowX: "auto" as const,
    paddingBottom: "12px",
    alignItems: "flex-start",
  } as React.CSSProperties,

  dayColumn: {
    minWidth: "160px",
    flex: "1 1 160px",
  } as React.CSSProperties,

  dayHeader: {
    textAlign: "center" as const,
    fontWeight: 700,
    fontSize: "12px",
    letterSpacing: "0.08em",
    textTransform: "uppercase" as const,
    padding: "8px 0 10px",
    color: "#475569",
  } as React.CSSProperties,

  kelasCard: (hari: string) => ({
    background: HARI_COLORS[hari]?.bg ?? "#F8FAFF",
    border: `1.5px solid ${HARI_COLORS[hari]?.border ?? "#CBD5E1"}`,
    borderRadius: "10px",
    padding: "12px 13px",
    marginBottom: "10px",
    cursor: "pointer",
    transition: "box-shadow 0.15s, transform 0.15s",
    position: "relative" as const,
  } as React.CSSProperties),

  kelasNama: {
    fontWeight: 700,
    fontSize: "13px",
    color: "#0F172A",
    marginBottom: "3px",
  } as React.CSSProperties,

  kelasMaPel: {
    fontSize: "12px",
    color: "#334155",
    fontWeight: 500,
    marginBottom: "3px",
  } as React.CSSProperties,

  kelasJam: {
    fontSize: "11px",
    color: "#64748B",
  } as React.CSSProperties,

  kelasActions: {
    display: "flex",
    gap: "4px",
    marginTop: "8px",
  } as React.CSSProperties,

  btnEdit: {
    display: "flex",
    alignItems: "center",
    gap: "3px",
    background: "#EFF6FF",
    color: "#2563EB",
    border: "1px solid #BFDBFE",
    borderRadius: "5px",
    padding: "3px 8px",
    fontSize: "11px",
    fontWeight: 600,
    cursor: "pointer",
  } as React.CSSProperties,

  btnDanger: {
    display: "flex",
    alignItems: "center",
    gap: "3px",
    background: "#FFF1F2",
    color: "#E11D48",
    border: "1px solid #FECDD3",
    borderRadius: "5px",
    padding: "3px 8px",
    fontSize: "11px",
    fontWeight: 600,
    cursor: "pointer",
  } as React.CSSProperties,

  emptyDay: {
    textAlign: "center" as const,
    color: "#CBD5E1",
    fontSize: "12px",
    padding: "20px 0",
    border: "1.5px dashed #E2E8F0",
    borderRadius: "10px",
  } as React.CSSProperties,

  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(15,23,42,0.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  } as React.CSSProperties,

  modal: {
    background: "#fff",
    borderRadius: "16px",
    padding: "28px 28px 24px",
    width: "100%",
    maxWidth: "420px",
    boxShadow: "0 20px 60px rgba(0,0,0,0.18)",
    position: "relative" as const,
  } as React.CSSProperties,

  modalTitle: {
    fontSize: "17px",
    fontWeight: 700,
    color: "#0F172A",
    marginBottom: "4px",
  } as React.CSSProperties,

  modalSubtitle: {
    fontSize: "13px",
    color: "#64748B",
    marginBottom: "20px",
  } as React.CSSProperties,

  formGroup: { marginBottom: "14px" } as React.CSSProperties,
  label: { fontSize: "12px", fontWeight: 600, color: "#475569", display: "block", marginBottom: "5px" } as React.CSSProperties,
  input: {
    width: "100%",
    border: "1.5px solid #E2E8F0",
    borderRadius: "8px",
    padding: "9px 12px",
    fontSize: "13px",
    outline: "none",
    boxSizing: "border-box" as const,
    color: "#0F172A",
  } as React.CSSProperties,

  modalFooter: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "8px",
    marginTop: "20px",
  } as React.CSSProperties,

  btnCancel: {
    background: "#F1F5F9",
    color: "#475569",
    border: "none",
    borderRadius: "8px",
    padding: "9px 16px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
  } as React.CSSProperties,

  btnSave: {
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "9px 18px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
  } as React.CSSProperties,

  closeBtn: {
    position: "absolute" as const,
    top: "14px",
    right: "14px",
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "#94A3B8",
    padding: "4px",
  } as React.CSSProperties,

  select: {
    width: "100%",
    border: "1.5px solid #E2E8F0",
    borderRadius: "8px",
    padding: "9px 12px",
    fontSize: "13px",
    outline: "none",
    boxSizing: "border-box" as const,
    background: "#fff",
    cursor: "pointer",
    color: "#0F172A",
    appearance: "auto" as const,
  } as React.CSSProperties,
  
  btnDetail: {
    display: "flex",
    alignItems: "center",
    gap: "3px",
    background: "#F5F3FF",
    color: "#7C3AED",
    border: "1px solid #DDD6FE",
    borderRadius: "5px",
    padding: "3px 8px",
    fontSize: "11px",
    fontWeight: 600,
    cursor: "pointer",
  } as React.CSSProperties,
};

export default function MasterKelas({ onNavigate }: { onNavigate?: (route: string, params?: Record<string, string>) => void }) {
  const [kelasList, setKelasList] = useState<KelasResponse[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  const [kelasForm, setKelasForm] = useState<KelasPayload>(emptyKelasForm());
  const [editingKelasId, setEditingKelasId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ kelasId: string } | null>(null);
  const [mataPelajaranList, setMataPelajaranList] = useState<MataPelajaranObj[]>([]);

  const { errorMsg, loadKelas, submitCreateKelas, submitUpdateKelas, submitDeleteKelas } = useKelasApi();
    const { loadMapelList } = useMapelApi();

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  useEffect(() => {
    loadKelas().then((data) => {
      if (data?.length) setKelasList(data);
    });
    loadMapelList().then((data) => {
      if (data?.length) setMataPelajaranList(data);
    });
  }, []);

  // Group kelas by hari (convert number → string via HARI_MAP)
  const kelasByHari = HARI_ORDER.reduce<Record<string, KelasResponse[]>>((acc, hariStr) => {
    acc[hariStr] = kelasList.filter((k) => k.hari=== hariStr);
    return acc;
  }, {});

  const displayDays = HARI_ORDER;

  // const totalSiswa = 0;

  // ── Kelas CRUD ──
  const openAddKelas = () => {
    setKelasForm(emptyKelasForm());
    setEditingKelasId(null);
    setModal("add-kelas");
  };

  const openEditKelas = (k: KelasResponse) => {
    setKelasForm({
      nama: k.nama,
      mata_pelajaran_id: k.mata_pelajaran_id ?? "",
      hari: k.hari,
      jam: k.jam,
    });
    setEditingKelasId(k.id);
    setModal("edit-kelas");
  };

  const saveKelas = async () => {
    if (!kelasForm.nama.trim()) return;
    if (editingKelasId) {
      const result = await submitUpdateKelas(editingKelasId, kelasForm);
      if (result) {
        setKelasList((prev) =>
          prev.map((k) => k.id === editingKelasId ? result : k)
        );
        showToast("Kelas berhasil diperbarui", "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal memperbarui kelas", "error");
      }
    } else {
      const result = await submitCreateKelas(kelasForm);
      console.log(result);
      if (result) {
        setKelasList((prev) => [...prev, result]);
        showToast(`Kelas ${result.nama} berhasil ditambahkan`, "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal membuat kelas", "error");
      }
    }
  };

  const deleteKelas = async (id: string) => {
    const ok = await submitDeleteKelas(id);
    if (ok) {
      setKelasList((prev) => prev.filter((k) => k.id !== id));
      showToast("Kelas berhasil dihapus", "success");
    } else {
      showToast(errorMsg ?? "Gagal menghapus kelas", "error");
    }
    setDeleteConfirm(null);
  };

  return (
    <div style={styles.root}>
      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>Master Kelas</h2>
        <p style={styles.subtitle}>Jadwal kelas berdasarkan hari</p>
      </div>

      {/* ── Stats ── */}
      <div style={styles.statsRow}>
        <div style={styles.statBadge}>
          🏫 Total Kelas: <span style={{ color: "#4F46E5" }}>{kelasList.length}</span>
        </div>
        {/* <div style={styles.statBadge}>
          👥 Total Siswa: <span style={{ color: "#059669" }}>{totalSiswa}</span>
        </div> */}
      </div>

      {/* ── Toolbar ── */}
      <div style={styles.toolbar}>
        <span style={{ fontSize: "13px", color: "#94A3B8" }}>
          {kelasList.length} kelas ditemukan
        </span>
        <button style={styles.btnPrimary} onClick={openAddKelas}>
          <IconPlus /> Tambah Kelas
        </button>
      </div>

      {/* ── Schedule Grid ── */}
      <div style={styles.scheduleGrid}>
        {displayDays.map((hari) => {
          const kelasHariIni = kelasByHari[hari];
          const color = HARI_COLORS[hari] ?? { label: "#475569" };
          return (
            <div key={hari} style={styles.dayColumn}>
              {/* Day Header */}
              <div style={{ ...styles.dayHeader, color: color.label }}>
                {hari}
              </div>

              {/* Kelas Cards */}
              {kelasHariIni.length === 0 ? (
                <div style={styles.emptyDay}>–</div>
              ) : (
                kelasHariIni
                  .sort((a, b) => a.jam.localeCompare(b.jam))
                  .map((kelas) => (
                    <div key={kelas.id} style={styles.kelasCard(hari)}>
                      <div style={styles.kelasNama}>Kelas {kelas.nama}</div>
                      <div style={styles.kelasMaPel}>
                        <div style={styles.kelasMaPel}>
                          {mataPelajaranList.find((m) => m.id === kelas.mata_pelajaran_id)?.nama_mata_pelajaran ?? "-"}
                      </div>
                      </div>
                      <div style={styles.kelasJam}>⏰ {kelas.jam}</div>

                      <div style={styles.kelasActions}>
                        <button
                          style={styles.btnDetail}
                          onClick={(e) => { e.stopPropagation(); 
                            onNavigate?.("detailKelas", { kelasId: kelas.id }); }}
                        >
                          Detail
                        </button>
                        <button
                          style={styles.btnEdit}
                          onClick={(e) => { e.stopPropagation(); openEditKelas(kelas); }}
                        >
                          <IconEdit /> Edit
                        </button>
                        <button
                          style={styles.btnDanger}
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ kelasId: kelas.id }); }}
                        >
                          <IconTrash />
                        </button>
                      </div>
                    </div>
                  ))
              )}
            </div>
          );
        })}
      </div>

      {/* ── Modal Kelas ── */}
      {modal && (
        <div style={styles.overlay}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>
              {modal === "add-kelas" ? "Tambah Kelas Baru" : "Edit Kelas"}
            </div>
            <div style={styles.modalSubtitle}>Isi informasi kelas di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Nama Kelas *</label>
              <input
                style={styles.input}
                placeholder="Contoh: A, B, atau VII-A"
                value={kelasForm.nama}
                onChange={(e) => setKelasForm((f) => ({ ...f, nama: e.target.value }))}
                required
                autoComplete="nama"
              />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Mata Pelajaran *</label>
              <select
                style={styles.select}
                value={kelasForm.mata_pelajaran_id}
                onChange={(e) => {
                  const selected = mataPelajaranList.find((m) => m.id === e.target.value);
                  setKelasForm((f) => ({
                    ...f,
                    mata_pelajaran_id: selected?.id ?? "",
                  }));
                }}
                required
              >
                <option value="">
                  -- Pilih Mata Pelajaran --
                </option>
                {mataPelajaranList.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.nama_mata_pelajaran}
                  </option>
                ))}
              </select>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Hari</label>
              <select
                style={styles.select}
                value={kelasForm.hari}
                onChange={(e) => setKelasForm((f) => ({ ...f, hari: e.target.value }))}
                required
              >
                <option value="">-- Pilih Hari --</option>
                {Object.entries(HARI_MAP).map(([nama]) => (
                  <option key={nama} value={nama}>{nama}</option>
                ))}
              </select>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Jam Mulai</label>
              <input
                style={styles.input}
                placeholder="Contoh: 10:00"
                value={kelasForm.jam}
                onChange={(e) => setKelasForm((f) => ({ ...f, jam: e.target.value }))}
                required
                autoComplete="jam" 
              />
            </div>

            <div style={styles.modalFooter}>
              <button style={styles.btnCancel} onClick={() => setModal(null)}>Batal</button>
              <button style={styles.btnSave} onClick={saveKelas}>
                {modal === "add-kelas" ? "Tambah Kelas" : "Simpan Perubahan"}
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
              Hapus kelas "
              {kelasList.find((k) => k.id === deleteConfirm.kelasId)?.nama}"?
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button
                style={{ ...styles.btnSave, background: "#E11D48" }}
                onClick={() => deleteKelas(deleteConfirm.kelasId)}
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
}