import { useEffect, useState } from "react";
import { IconClose, IconEdit, IconPlus, IconTrash } from "../../icons";
import { useKelasApi } from "./useKelasApi";
import type { KelasPayload, KelasResponse, MataPelajaranObj, Toast } from "../../service/payload";
import { useMapelApi } from "../master-mapel/useMapelApi";
import { styles } from "./styles";

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

const stylesCard = {
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

  const kelasByHari = HARI_ORDER.reduce<Record<string, KelasResponse[]>>((acc, hariStr) => {
    acc[hariStr] = kelasList.filter((k) => k.hari=== hariStr);
    return acc;
  }, {});

  const displayDays = HARI_ORDER;

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
                    <div key={kelas.id} style={stylesCard.kelasCard(hari)}>
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
      <div style={styles.toastNotif}>
        {toasts.map((t) => (
          <div key={t.id} style={{
            background: t.type === "success" ? "#F0FDF4" : "#FFF1F2",
            border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`,
            color: t.type === "success" ? "#15803D" : "#9F1239",
            ...styles.bodyToastNotif
          }}>
            <span style={{ fontSize: "16px" }}>
              {t.type === "success" ? "✅" : "❌"}
            </span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
              style={styles.btnToast}
            >✕</button>
          </div>
        ))}
      </div>
    </div>
  );
}