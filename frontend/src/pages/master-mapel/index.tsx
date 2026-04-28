import { useEffect, useState } from "react";
import { styles } from "./styles";
import { IconClose, IconEdit, IconPlus, IconTrash } from "../../icons";
import { useMapelApi } from "./useMapelApi";
import type { MapelPayload, MapelResponse, Toast } from "../../service/payload";

type ModalMode = "add-mapel" | "edit-mapel" | null;

const emptyKelas = (): Omit<MapelPayload, "id"> => ({
  nama_mata_pelajaran: "", topik: [],
});

let toastId = 0;

export default function MasterMapel() {
  const [mapelList, setMapelList] = useState<MapelResponse[]>([]);
  const [, setToasts] = useState<Toast[]>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  const [mapelForm, setMapelForm] = useState(emptyKelas());
  const [editingMapelId, setEditingMapelId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ mapelId: string; } | null>(null);

  const { errorMsg, loadMapelList, submitCreateMapel, submitUpdateMapel, submitDeleteMapel } = useMapelApi();

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  // ── Mata Pelajaran CRUD ──
  const openAddMapel = () => {
    setMapelForm(emptyKelas());
    setEditingMapelId(null);
    setModal("add-mapel");
  };

  const isModalMapel = modal === "add-mapel" || modal === "edit-mapel";

  const mapApiMapel = (data: MapelResponse) => ({
    id: data.id,
    nama_mata_pelajaran: data.nama_mata_pelajaran,
    topik: data.topik,
    created_at: data.created_at,
    updated_at: data.updated_at,
  });

  useEffect(() => {
    loadMapelList().then((data) => {
      if (data.length) setMapelList(data.map(mapApiMapel));
    });
  }, []);

  const openEditMapel = (k: MapelResponse) => {
    setMapelForm({ 
      nama_mata_pelajaran: k.nama_mata_pelajaran,
      topik: k.topik,
    });
    setEditingMapelId(k.id);
    setModal("edit-mapel");
  };

  const saveMapel = async () => {
    if (!mapelForm.nama_mata_pelajaran.trim()) return;
    if (editingMapelId) {
      /** update */
      const result = await submitUpdateMapel(mapelForm, editingMapelId);
      if (result) {
        setMapelList((prev) =>
          prev.map((k) =>
            k.id === editingMapelId ? { ...k, ...mapApiMapel(result)} : k
          )
        );
        showToast("Mata Pelajaran berhasil diperbarui", "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal memperbarui mata pelajaran", "error");
      }
    } else {
      /** create */
      const result = await submitCreateMapel(mapelForm);
      if (result) {
        const newMapel = mapApiMapel(result);
        setMapelList((prev) => [...prev, newMapel]);
        showToast(`Mata Pelajaran ${newMapel.nama_mata_pelajaran} berhasil ditambahkan`, "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal membuat mata pelajaran", "error");
      }
    }
    setModal(null);
  };

  const deleteMapel = async (id: string) => {
    const ok = await submitDeleteMapel(id);
    if (ok) {
      setMapelList((prev) => prev.filter((k) => k.id !== id));
      showToast("Mata Pelajaran berhasil dihapus", "success");
    } else {
      showToast(errorMsg ?? "Gagal menghapus mata pelajaran", "error");
    }
    setDeleteConfirm(null);
  };

  return (
    <div style={styles.root}>
      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>Master Mata Pelajaran</h2>
        <p style={styles.subtitle}>Kelola data mata pelajaran</p>
      </div>

      {/* ── Toolbar ── */}
      <div style={styles.toolbar}>
        <span style={{ fontSize: "14px", fontWeight: 600, color: "#6B7FA3" }}>
          {/* {mapelList.length} kelas ditemukan */}
        </span>
        <button style={styles.btnPrimary} onClick={openAddMapel}>
          <IconPlus /> Tambah Mata Pelajaran
        </button>
      </div>

      {/* ── Mata Pelajaran List ── */}
      <div
        style={{
          background: "#fff",
          borderRadius: "14px",
          boxShadow: "0 1px 4px rgba(30,42,59,0.07)",
          overflow: "hidden",
          border: "1.5px solid #EAECF5",
        }}
      >
      {mapelList.length === 0 ? (
        <div style={{ ...styles.kelasCard, ...styles.emptyState }}>
          <div style={{ fontSize: "32px", marginBottom: "8px" }}>🏫</div>
          Belum ada mata pelajaran. Klik "Tambah Mata Pelajaran" untuk memulai.
        </div>
      ) : (
        <div style={styles.tableWrapper}>
          <table style={styles.siswaTable}>
            <thead>
              <tr>
                <th style={styles.th}>#</th>
                <th style={styles.th}>Nama Mata Pelajaran</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {mapelList.map((s, i) => (
                <tr key={s.id}>
                  <td style={styles.td}>{i + 1}</td>
                  <td style={styles.td}>{s.nama_mata_pelajaran}</td>
                  <td style={styles.td}>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                      <button
                        type="button"
                        onClick={() => openEditMapel(s)}
                        style={styles.btnEdit}
                        title="Edit mata pelajaran"
                      >
                        <IconEdit />
                        Edit
                      </button>

                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ mapelId: s.id }); }}
                        // onClick={() => setDeleteConfirm({ siswaId: s.id })}
                        style={styles.btnDanger}
                        title="Hapus mata pelajaran"
                      >
                        <IconTrash />
                        Hapus
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      </div>

      {/* ── Modal Mata Pelajaran ── */}
      {/* {isModalMapel && (
        <div style={styles.overlay} onClick={() => setModal(null)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>{modal === "add-mapel" ? "Tambah Mata Pelajaran Baru" : "Edit Mata Pelajaran"}</div>
            <div style={styles.modalSubtitle}>Isi informasi mata pelajaran di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Nama Mata Pelajaran *</label>
              <input style={styles.input} placeholder="Masukkan nama mata pelajaran" value={mapelForm.nama_mata_pelajaran}
                onChange={(e) => setMapelForm((f) => ({ ...f, nama_mata_pelajaran: e.target.value }))} />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Topik *</label>
              <input style={styles.input} placeholder="Masukkan nama topik" value={mapelForm.topik.join(", ")}
                onChange={(e) => setMapelForm((f) => ({ ...f, topik: e.target.value.split(", ").map((v) => v.trim()).filter((v) => v) }))} />
            </div>

            <div style={styles.modalFooter}>
              <button style={styles.btnCancel} onClick={() => setModal(null)}>Batal</button>
              <button style={styles.btnSave} onClick={saveMapel}>
                {modal === "add-mapel" ? "Tambah Mata Pelajaran" : "Simpan Perubahan"}
              </button>
            </div>
          </div>
        </div>
      )} */}
      {isModalMapel && (
        <div style={styles.overlay}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>{modal === "add-mapel" ? "Tambah Mata Pelajaran Baru" : "Edit Mata Pelajaran"}</div>
            <div style={styles.modalSubtitle}>Isi informasi mata pelajaran di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Nama Mata Pelajaran *</label>
              <input style={styles.input} placeholder="Masukkan nama mata pelajaran" value={mapelForm.nama_mata_pelajaran}
                onChange={(e) => setMapelForm((f) => ({ ...f, nama_mata_pelajaran: e.target.value }))} />
            </div>
            <div style={styles.formGroup}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "6px" }}>
                <label style={styles.label}>Topik *</label>
                <button
                  type="button"
                  onClick={() => setMapelForm((f) => ({ ...f, topik: [...f.topik, ""] }))}
                  style={{ background: "none", border: "none", color: "#534AB7", fontSize: "13px", fontWeight: 600, cursor: "pointer", padding: "2px 4px" }}
                >
                  + Tambah Topik
                </button>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {(mapelForm.topik.length === 0 ? [""] : mapelForm.topik).map((topik, idx) => (
                  <div key={idx} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <input
                      style={{ ...styles.input, margin: 0, flex: 1 }}
                      placeholder="Masukkan nama topik"
                      value={topik}
                      onChange={(e) => {
                        const updated = [...mapelForm.topik];
                        if (mapelForm.topik.length === 0) {
                          setMapelForm((f) => ({ ...f, topik: [e.target.value] }));
                        } else {
                          updated[idx] = e.target.value;
                          setMapelForm((f) => ({ ...f, topik: updated }));
                        }
                      }}
                    />
                    {mapelForm.topik.length > 1 && (
                      <button
                        type="button"
                        onClick={() => setMapelForm((f) => ({ ...f, topik: f.topik.filter((_, i) => i !== idx) }))}
                        style={{ background: "none", border: "1px solid #E2E8F0", borderRadius: "6px", color: "#A0AEC0", cursor: "pointer", width: "34px", height: "34px", fontSize: "14px", flexShrink: 0 }}
                        title="Hapus topik"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div style={styles.modalFooter}>
              <button style={styles.btnCancel} onClick={() => setModal(null)}>Batal</button>
              <button style={styles.btnSave} onClick={saveMapel}>
                {modal === "add-mapel" ? "Tambah Mata Pelajaran" : "Simpan Perubahan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirm ── */}
      {deleteConfirm && (
        <div style={styles.overlay}>
          <div style={{ ...styles.modal, maxWidth: "380px" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "36px", textAlign: "center", marginBottom: "12px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center", marginBottom: "0" }}>
              Hapus mata pelajaran "{mapelList.find((k) => k.id === deleteConfirm.mapelId)?.nama_mata_pelajaran}"?`
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button style={{ ...styles.btnSave, background: "linear-gradient(135deg, #E53E3E, #C53030)" }}
                onClick={() => {
                  deleteMapel(deleteConfirm.mapelId);
                }}>
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}