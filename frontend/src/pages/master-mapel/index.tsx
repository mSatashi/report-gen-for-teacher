import { useEffect, useState } from "react";
import { styles } from "./styles";
import { IconClose, IconEdit, IconPlus, IconTrash } from "../../icons";
import { useMapelApi } from "./useMapelApi";
import type { MapelPayload, MapelResponse, MapelUpdatePayload, Toast, TopikPayload } from "../../service/payload";

type ModalMode = "add-mapel" | "edit-mapel" | null;

// [FIX 1] mapelForm hanya menyimpan nama_mata_pelajaran.
// topik dikelola sepenuhnya lewat topikForm agar tidak ada konflik tipe
// antara string[] (MapelResponse) dan TopikPayload[] (MapelPayload).
const emptyMapelForm = () => ({ nama_mata_pelajaran: "" });

const emptyTopik = (): TopikPayload => ({
  id: undefined,
  nama: "",
  difficulty_index: 0.1,
  prasyarat_ids: [],
});

let toastId = 0;

// [FIX 2] label diubah ke string agar bisa dirender di <option>
const TINGKAT_KESULITAN_OPTIONS: { value: number; label: string; color: string; bg: string }[] = [
  { value: 0.1, label: "0.1", color: "#276749", bg: "#C6F6D5" },
  { value: 0.2, label: "0.2", color: "#276749", bg: "#C6F6D5" },
  { value: 0.3, label: "0.3", color: "#7B5E00", bg: "#FEFCBF" },
  { value: 0.4, label: "0.4", color: "#7B5E00", bg: "#FEFCBF" },
  { value: 0.5, label: "0.5", color: "#7B5E00", bg: "#FEFCBF" },
  { value: 0.6, label: "0.6", color: "#7B5E00", bg: "#FEFCBF" },
  { value: 0.7, label: "0.7", color: "#9B2C2C", bg: "#FED7D7" },
  { value: 0.8, label: "0.8", color: "#9B2C2C", bg: "#FED7D7" },
  { value: 0.9, label: "0.9", color: "#9B2C2C", bg: "#FED7D7" },
  { value: 1.0, label: "1.0", color: "#9B2C2C", bg: "#FED7D7" },
];

const getKesulitanInfo = (val: number) =>
  TINGKAT_KESULITAN_OPTIONS.reduce((prev, curr) =>
    Math.abs(curr.value - val) < Math.abs(prev.value - val) ? curr : prev
  );

// const parseTopikFromApi = (raw: unknown[]): TopikPayload[] => {
//   if (!raw || raw.length === 0) return [emptyTopik()];
//   return raw.map((t) => {
//     if (typeof t === "string") return { nama: t, difficulty_index: 0.1 }; // string[] → default 0.1
//     const obj = t as Partial<TopikPayload>;
//     return { nama: obj.nama ?? "", difficulty_index: obj.difficulty_index ?? 0.1 };
//   });
// };

export default function MasterMapel() {
  const [mapelList, setMapelList] = useState<MapelResponse[]>([]);
  const [, setToasts] = useState<Toast[]>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  const [mapelForm, setMapelForm] = useState<{ nama_mata_pelajaran: string }>(emptyMapelForm());
  const [topikForm, setTopikForm] = useState<TopikPayload[]>([emptyTopik()]);
  const [editingMapelId, setEditingMapelId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ mapelId: string } | null>(null);

  const { errorMsg, loadMapelList, submitCreateMapel, submitUpdateMapel, submitDeleteMapel } =
    useMapelApi();

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const updateTopik = (idx: number, patch: Partial<TopikPayload>) => {
    setTopikForm((prev) => prev.map((t, i) => (i === idx ? { ...t, ...patch } : t)));
  };

  const addTopik = () => setTopikForm((prev) => [...prev, emptyTopik()]);

  const removeTopik = (idx: number) =>
    setTopikForm((prev) => prev.filter((_, i) => i !== idx));

  // ── Mata Pelajaran CRUD ──
    const openAddMapel = () => {
      setMapelForm(emptyMapelForm());
      setTopikForm([emptyTopik()]);
      setEditingMapelId(null);
      setModal("add-mapel");
    };

  const isModalMapel = modal === "add-mapel" || modal === "edit-mapel";

  const mapApiMapel = (data: MapelResponse) => ({
    id: data.id,
    nama_mata_pelajaran: data.nama_mata_pelajaran,
    topik_list: data.topik_list,
    created_at: data.created_at,
    updated_at: data.updated_at,
  });

  useEffect(() => {
    loadMapelList().then((data) => {
      if (data.length) setMapelList(data.map(mapApiMapel));
    });
  }, []);

  const openEditMapel = (k: MapelResponse) => {
    setMapelForm({ nama_mata_pelajaran: k.nama_mata_pelajaran });

    type TopikFromApi = {
      id?: string | null;
      nama?: string;
      difficulty_index?: number;
      prasyarat_ids?: string[];
    };

    const parsed: TopikPayload[] =
      !k.topik_list || k.topik_list.length === 0
        ? [emptyTopik()]
        : (k.topik_list as unknown as TopikFromApi[]).map((t) => {
            if (typeof t === "string") {
              return { id: undefined, nama: t, difficulty_index: 0.1, prasyarat_ids: [] }; // ← di sini
            }
            return {
              id: t.id ?? undefined,   // ← dan di sini
              nama: t.nama ?? "",
              difficulty_index: t.difficulty_index ?? 0.1,
              prasyarat_ids: t.prasyarat_ids ?? [],
            };
          });

    setTopikForm(parsed);
    setEditingMapelId(k.id);
    setModal("edit-mapel");
  };

  // const openEditMapel = (k: MapelResponse) => {
  // setMapelForm({ nama_mata_pelajaran: k.nama_mata_pelajaran });

//   type TopikFromApi = {
//     id?: string | null;
//     nama?: string;
//     difficulty_index?: number;
//     prasyarat_ids?: string[];
//   };
  

//   const parsed: TopikPayload[] =
//     !k.topik_list || k.topik_list.length === 0
//       ? [emptyTopik()]
//       : (k.topik_list as unknown as TopikFromApi[]).map((t) => {
//           if (typeof t === "string") {
//             return { id: null, nama: t as string, difficulty_index: 0.1, prasyarat_ids: [] };
//           }
//           return {
//             id: t.id ?? null,
//             nama: t.nama ?? "",
//             difficulty_index: t.difficulty_index ?? 0.1,
//             prasyarat_ids: t.prasyarat_ids ?? [],
//           };
//         });

//   setTopikForm(parsed);
//   setEditingMapelId(k.id);
//   setModal("edit-mapel");
// };


  const saveMapel = async () => {
    if (!mapelForm.nama_mata_pelajaran.trim()) return;

    const filteredTopik = topikForm.filter((t) => t.nama.trim());
    console.log(filteredTopik)

    if (editingMapelId) {
      const updatePayload: MapelUpdatePayload = {
        nama_mata_pelajaran: mapelForm.nama_mata_pelajaran,
        topik_list: filteredTopik.map((t) => ({
          id: t.id ?? null,  
          nama: t.nama,
          difficulty_index: t.difficulty_index,
          prasyarat_ids: t.prasyarat_ids ?? [],
        })),
      };

      const result = await submitUpdateMapel(updatePayload, editingMapelId);
      if (result) {
        setMapelList((prev) =>
          prev.map((k) => (k.id === editingMapelId ? { ...k, ...mapApiMapel(result) } : k))
        );
        showToast("Mata Pelajaran berhasil diperbarui", "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal memperbarui mata pelajaran", "error");
      }
    } else {
      const payload: Omit<MapelPayload, "id"> = {
        nama_mata_pelajaran: mapelForm.nama_mata_pelajaran,
        topik_awal: topikForm.filter((t) => t.nama.trim()),
      };
      
      const result = await submitCreateMapel(payload);
      if (result) {
        const newMapel = mapApiMapel(result);
        setMapelList((prev) => [...prev, newMapel]);
        showToast(`Mata Pelajaran ${newMapel.nama_mata_pelajaran} 
          berhasil ditambahkan`, "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal membuat mata pelajaran", "error");
      }
    }
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
        <span style={{ fontSize: "14px", fontWeight: 600, color: "#6B7FA3" }} />
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
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirm({ mapelId: s.id });
                          }}
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
      {/* [FIX 8] Modal duplikat & nested dihapus — sekarang hanya ada satu blok modal */}
      {isModalMapel && (
        <div style={styles.overlay}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}>
              <IconClose />
            </button>
            <div style={styles.modalTitle}>
              {modal === "add-mapel" ? "Tambah Mata Pelajaran Baru" : "Edit Mata Pelajaran"}
            </div>
            <div style={styles.modalSubtitle}>Isi informasi mata pelajaran di bawah ini</div>

            {/* Nama Mata Pelajaran */}
            <div style={styles.formGroup}>
              <label style={styles.label}>Nama Mata Pelajaran *</label>
              <input
                style={styles.input}
                placeholder="Masukkan nama mata pelajaran"
                value={mapelForm.nama_mata_pelajaran}
                onChange={(e) =>
                  setMapelForm((f) => ({ ...f, nama_mata_pelajaran: e.target.value }))
                }
              />
            </div>

            {/* Topik */}
            <div style={styles.formGroup}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "8px",
                }}
              >
                <label style={styles.label}>Topik *</label>
                <button
                  type="button"
                  onClick={addTopik}
                  style={{
                    background: "none",
                    border: "none",
                    color: "#534AB7",
                    fontSize: "13px",
                    fontWeight: 600,
                    cursor: "pointer",
                    padding: "2px 4px",
                  }}
                >
                  + Tambah Topik
                </button>
              </div>

              {/* Header kolom */}
              {topikForm.length > 0 && (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 140px 34px",
                    gap: "8px",
                    marginBottom: "4px",
                    paddingLeft: "2px",
                  }}
                >
                  <span style={{ fontSize: "11px", color: "#8A94A8", fontWeight: 600 }}>
                    Nama Topik
                  </span>
                  <span style={{ fontSize: "11px", color: "#8A94A8", fontWeight: 600 }}>
                    Tingkat Kesulitan
                  </span>
                  <span />
                </div>
              )}

              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {topikForm.map((topik, idx) => {
                  // [FIX 9] Ganti .find() dengan getKesulitanInfo() agar tidak undefined/crash
                  const kesulitanInfo = getKesulitanInfo(topik.difficulty_index);
                  return (
                    <div
                      key={idx}
                      style={{
                        display: "grid",
                        gridTemplateColumns: "1fr 140px 34px",
                        gap: "8px",
                        alignItems: "center",
                      }}
                    >
                      {/* Input nama topik */}
                      <input
                        style={{ ...styles.input, margin: 0 }}
                        placeholder="Nama topik"
                        value={topik.nama}
                        onChange={(e) => updateTopik(idx, { nama: e.target.value })}
                      />

                      {/* Select tingkat kesulitan */}
                      <div style={{ position: "relative" }}>
                        <select
                          value={topik.difficulty_index}
                          onChange={(e) =>
                            updateTopik(idx, { difficulty_index: parseFloat(e.target.value) })
                          }
                          style={{
                            width: "100%",
                            height: "38px",
                            border: `1.5px solid ${kesulitanInfo.color}40`,
                            borderRadius: "8px",
                            padding: "0 24px 0 10px",
                            fontSize: "13px",
                            fontWeight: 600,
                            color: kesulitanInfo.color,
                            background: kesulitanInfo.bg,
                            appearance: "none",
                            cursor: "pointer",
                            outline: "none",
                          }}
                        >
                          {TINGKAT_KESULITAN_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                              {opt.label}
                            </option>
                          ))}
                        </select>
                        <span
                          style={{
                            position: "absolute",
                            right: "8px",
                            top: "50%",
                            transform: "translateY(-50%)",
                            pointerEvents: "none",
                            fontSize: "10px",
                            color: kesulitanInfo.color,
                          }}
                        >
                          ▾
                        </span>
                      </div>

                      {/* Tombol hapus topik */}
                      {topikForm.length > 1 ? (
                        <button
                          type="button"
                          onClick={() => removeTopik(idx)}
                          style={{
                            background: "none",
                            border: "1px solid #E2E8F0",
                            borderRadius: "6px",
                            color: "#A0AEC0",
                            cursor: "pointer",
                            width: "34px",
                            height: "34px",
                            fontSize: "14px",
                            flexShrink: 0,
                          }}
                          title="Hapus topik"
                        >
                          ✕
                        </button>
                      ) : (
                        <span style={{ width: "34px" }} />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <div style={styles.modalFooter}>
              <button style={styles.btnCancel} onClick={() => setModal(null)}>
                Batal
              </button>
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
          <div
            style={{ ...styles.modal, maxWidth: "380px" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: "36px", textAlign: "center", marginBottom: "12px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            {/* [FIX 10] Hapus backtick liar di akhir string */}
            <div style={{ ...styles.modalSubtitle, textAlign: "center", marginBottom: "0" }}>
              Hapus mata pelajaran "
              {mapelList.find((k) => k.id === deleteConfirm.mapelId)?.nama_mata_pelajaran}"?
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>
                Batal
              </button>
              <button
                style={{
                  ...styles.btnSave,
                  background: "linear-gradient(135deg, #E53E3E, #C53030)",
                }}
                onClick={() => deleteMapel(deleteConfirm.mapelId)}
              >
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}