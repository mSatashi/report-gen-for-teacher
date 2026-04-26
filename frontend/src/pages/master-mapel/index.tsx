import { useEffect, useState } from "react";
import { styles } from "./styles";
import { IconClose, IconEdit, IconPlus, IconTrash } from "../../icons";
import { useMapelApi } from "./useMapelApi";
import { createTopik, updateTopik, deleteTopikApi, addPrasyaratApi } from "../../service/topikAPI";
import type { MapelResponse, Toast, TopikFormItem } from "../../service/payload";

type ModalMode = "add-mapel" | "edit-mapel" | null;

let toastId = 0;

export default function MasterMapel() {
  const[mapelList, setMapelList] = useState<MapelResponse[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [modal, setModal] = useState<ModalMode>(null);
  
  const [namaMapel, setNamaMapel] = useState("");
  const[topikForm, setTopikForm] = useState<TopikFormItem[]>([]);
  
  const[editingMapelId, setEditingMapelId] = useState<string | null>(null);
  const[deleteConfirm, setDeleteConfirm] = useState<{ mapelId: string } | null>(null);

  const { errorMsg, loadMapelList, submitCreateMapel, submitUpdateMapel, submitDeleteMapel } = useMapelApi();

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) =>[...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  useEffect(() => {
    loadMapelList().then((data) => { if (data.length) setMapelList(data); });
  },[]); // eslint-disable-line react-hooks/exhaustive-deps

  const openAddMapel = () => {
    setNamaMapel("");
    setTopikForm([{ id: `temp-${Date.now()}`, nama: "", prasyarat_ids: [] }]);
    setEditingMapelId(null);
    setModal("add-mapel");
  };

  const openEditMapel = (k: MapelResponse) => {
    setNamaMapel(k.nama_mata_pelajaran);
    setTopikForm(
      k.topik_list ? k.topik_list.map((t) => ({
        id: t.id,
        nama: t.nama,
        prasyarat_ids: t.prasyarat ? t.prasyarat.map(p => p.id) :[],
      })) :[]
    );
    setEditingMapelId(k.id);
    setModal("edit-mapel");
  };

  const saveMapel = async () => {
    if (!namaMapel.trim()) {
      showToast("Nama Mapel wajib diisi", "error");
      return;
    }

    try {
      let mapelId = editingMapelId;

      // 1. SIMPAN MATA PELAJARAN DULU
      if (editingMapelId) {
        await submitUpdateMapel({ nama_mata_pelajaran: namaMapel }, editingMapelId);
      } else {
        const resMapel = await submitCreateMapel({ nama_mata_pelajaran: namaMapel });
        if (!resMapel) throw new Error("Gagal membuat mapel");
        mapelId = resMapel.id;
      }

      if (!mapelId) return;

      // 2. SIMPAN TOPIK
      const idMapper = new Map<string, string>(); 

      // Tahap 2A: Create/Update/Delete Topik
      for (const t of topikForm) {
        if (t.isDeleted) {
          if (!t.id.startsWith("temp-")) await deleteTopikApi(t.id);
          continue;
        }

        if (t.nama.trim() === "") continue;

        if (t.id.startsWith("temp-")) {
          const newTopik = await createTopik({
            mata_pelajaran_id: mapelId,
            nama: t.nama,
            difficulty_index: 0.5,
          });
          idMapper.set(t.id, newTopik.id);
        } else {
          await updateTopik(t.id, t.nama);
          idMapper.set(t.id, t.id);
        }
      }

      // Tahap 2B: Sambungkan Relasi Prasyarat
      for (const t of topikForm) {
        if (t.isDeleted || t.nama.trim() === "") continue;
        const realTopikId = idMapper.get(t.id);
        if (!realTopikId) continue;

        for (const prasyaratTempId of t.prasyarat_ids) {
          const realPrasyaratId = idMapper.get(prasyaratTempId);
          if (realPrasyaratId) {
             await addPrasyaratApi(realTopikId, realPrasyaratId).catch(() => {});
          }
        }
      }

      const refreshedData = await loadMapelList();
      setMapelList(refreshedData);
      
      showToast("Berhasil menyimpan Mata Pelajaran & Topik", "success");
      setModal(null);
    } catch (err) {
      showToast("Terjadi kesalahan saat menyimpan", "error");
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

  // --- HELPER UNTUK TOGGLE PRASYARAT ---
  const togglePrasyarat = (topikId: string, targetPrasyaratId: string) => {
    setTopikForm(prev => prev.map(t => {
      if (t.id === topikId) {
        const isSelected = t.prasyarat_ids.includes(targetPrasyaratId);
        return {
          ...t,
          prasyarat_ids: isSelected 
            ? t.prasyarat_ids.filter(id => id !== targetPrasyaratId) // Hapus jika sudah ada
            :[...t.prasyarat_ids, targetPrasyaratId] // Tambah jika belum ada
        };
      }
      return t;
    }));
  };

  const isModalMapel = modal === "add-mapel" || modal === "edit-mapel";
  const visibleTopiks = topikForm.filter(t => !t.isDeleted);

  return (
    <div style={styles.root}>
      {/* ── Header ── */}
      <div style={styles.header}>
        <h2 style={styles.title}>Master Mata Pelajaran</h2>
        <p style={styles.subtitle}>Kelola data mata pelajaran dan topik pembelajarannya</p>
      </div>

      {/* ── Toolbar ── */}
      <div style={styles.toolbar}>
        <span style={{ fontSize: "14px", fontWeight: 600, color: "#6B7FA3" }}>
          {mapelList.length} mata pelajaran ditemukan
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
                  <th style={styles.th}>Jumlah Topik</th>
                  <th style={styles.th}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {mapelList.map((s, i) => (
                  <tr key={s.id}>
                    <td style={styles.td}>{i + 1}</td>
                    <td style={styles.td}>{s.nama_mata_pelajaran}</td>
                    <td style={styles.td}>
                      <span style={{ background: "#EEF2FF", color: "#4338CA", padding: "4px 8px", borderRadius: "6px", fontSize: "12px", fontWeight: 600 }}>
                        {s.topik_list ? s.topik_list.length : 0} Topik
                      </span>
                    </td>
                    <td style={styles.td}>
                      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button
                          type="button"
                          onClick={() => openEditMapel(s)}
                          style={styles.btnEdit}
                          title="Edit mata pelajaran"
                        >
                          <IconEdit /> Edit
                        </button>

                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ mapelId: s.id }); }}
                          style={styles.btnDanger}
                          title="Hapus mata pelajaran"
                        >
                          <IconTrash /> Hapus
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

      {/* ── Modal Mata Pelajaran & Topik ── */}
      {isModalMapel && (
        <div style={styles.overlay}>
          <div style={{ ...styles.modal, maxWidth: "650px", maxHeight: "90vh", display: "flex", flexDirection: "column" }} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>{modal === "add-mapel" ? "Tambah Mata Pelajaran" : "Edit Mata Pelajaran"}</div>
            
            <div style={{ overflowY: "auto", paddingRight: "8px", marginTop: "16px" }}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Nama Mata Pelajaran *</label>
                <input style={styles.input} value={namaMapel} onChange={(e) => setNamaMapel(e.target.value)} placeholder="Contoh: Matematika" />
              </div>

              <div style={styles.formGroup}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px", alignItems: "center" }}>
                  <label style={{...styles.label, marginBottom: 0}}>Manajemen Topik & Prasyarat</label>
                  <button
                    type="button"
                    onClick={() => setTopikForm([...topikForm, { id: `temp-${Date.now()}`, nama: "", prasyarat_ids: [] }])}
                    style={{ background: "#EEF2FF", border: "1px solid #C7D2FE", color: "#4F46E5", borderRadius: "6px", fontSize: "12px", fontWeight: 600, cursor: "pointer", padding: "6px 12px", transition: "all 0.2s" }}
                  >
                    + Tambah Topik
                  </button>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  {visibleTopiks.map((t, idx) => {
                    // Filter topik untuk UI Prasyarat
                    const otherTopiks = visibleTopiks.filter(other => other.id !== t.id && other.nama.trim() !== "");
                    const selectedPrereqs = otherTopiks.filter(other => t.prasyarat_ids.includes(other.id));
                    const availablePrereqs = otherTopiks.filter(other => !t.prasyarat_ids.includes(other.id));

                    return (
                      <div key={t.id} style={{ display: "flex", gap: "12px", alignItems: "flex-start", background: "#F8FAFC", padding: "16px", borderRadius: "10px", border: "1px solid #E2E8F0" }}>
                        
                        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 12 }}>
                          <input
                            style={{ ...styles.input, padding: "8px 12px", fontWeight: 500 }}
                            placeholder={`Ketik nama topik ke-${idx + 1}`}
                            value={t.nama}
                            onChange={(e) => {
                              const updated = [...topikForm];
                              const index = updated.findIndex(item => item.id === t.id);
                              updated[index].nama = e.target.value;
                              setTopikForm(updated);
                            }}
                          />
                          
                          {/* AREA PILLS / CHIPS UNTUK PRASYARAT */}
                          {t.nama.trim() !== "" && otherTopiks.length > 0 && (
                            <div style={{ background: "#fff", padding: "12px", borderRadius: "8px", border: "1px solid #F1F5F9" }}>
                              <span style={{ fontSize: 11, color: "#64748b", fontWeight: 600, display: "block", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                                Prasyarat Topik Ini
                              </span>
                              
                              {/* Pill yang SUDAH dipilih */}
                              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: availablePrereqs.length > 0 ? "12px" : "0" }}>
                                {selectedPrereqs.length === 0 ? (
                                  <span style={{ fontSize: 12, color: "#94A3B8", fontStyle: "italic" }}>Belum ada prasyarat terpilih</span>
                                ) : (
                                  selectedPrereqs.map(p => (
                                    <button
                                      key={`selected-${p.id}`}
                                      type="button"
                                      onClick={() => togglePrasyarat(t.id, p.id)}
                                      style={{
                                        background: "#4F46E5", color: "#fff", border: "none",
                                        borderRadius: "20px", padding: "4px 12px", fontSize: "12px", fontWeight: 500,
                                        cursor: "pointer", display: "flex", alignItems: "center", gap: "6px"
                                      }}
                                      title="Klik untuk menghapus prasyarat"
                                    >
                                      {p.nama} <span style={{fontSize: "14px", fontWeight: 700}}>×</span>
                                    </button>
                                  ))
                                )}
                              </div>

                              {/* Pill opsi yang TERSEDIA */}
                              {availablePrereqs.length > 0 && (
                                <>
                                  <div style={{ height: "1px", background: "#F1F5F9", margin: "0 -12px 10px" }} />
                                  <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                                    {availablePrereqs.map(p => (
                                      <button
                                        key={`avail-${p.id}`}
                                        type="button"
                                        onClick={() => togglePrasyarat(t.id, p.id)}
                                        style={{
                                          background: "#F1F5F9", color: "#475569", border: "1px dashed #CBD5E1",
                                          borderRadius: "20px", padding: "4px 12px", fontSize: "12px", fontWeight: 500,
                                          cursor: "pointer", transition: "all 0.2s"
                                        }}
                                        onMouseEnter={(e) => {
                                          e.currentTarget.style.background = "#E2E8F0";
                                          e.currentTarget.style.borderColor = "#94A3B8";
                                        }}
                                        onMouseLeave={(e) => {
                                          e.currentTarget.style.background = "#F1F5F9";
                                          e.currentTarget.style.borderColor = "#CBD5E1";
                                        }}
                                        title="Klik untuk menambahkan sebagai prasyarat"
                                      >
                                        + {p.nama}
                                      </button>
                                    ))}
                                  </div>
                                </>
                              )}
                            </div>
                          )}

                        </div>

                        <button
                          type="button"
                          onClick={() => {
                            const updated = [...topikForm];
                            const index = updated.findIndex(item => item.id === t.id);
                            updated[index].isDeleted = true; // Soft delete
                            setTopikForm(updated);
                          }}
                          style={{ 
                            background: "#FEF2F2", border: "1px solid #FECACA", borderRadius: "8px", 
                            color: "#EF4444", cursor: "pointer", padding: "8px", marginTop: "2px", transition: "all 0.2s" 
                          }}
                          title="Hapus topik ini"
                          onMouseEnter={(e) => e.currentTarget.style.background = "#FEE2E2"}
                          onMouseLeave={(e) => e.currentTarget.style.background = "#FEF2F2"}
                        >
                          <IconTrash />
                        </button>
                      </div>
                    );
                  })}
                  {visibleTopiks.length === 0 && (
                    <div style={{ textAlign: "center", fontSize: "14px", color: "#94a3b8", padding: "30px 0", border: "1.5px dashed #CBD5E1", borderRadius: "10px" }}>
                      Belum ada topik. Klik "+ Tambah Topik" di atas.
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div style={{...styles.modalFooter, marginTop: "24px", paddingTop: "16px", borderTop: "1px solid #E2E8F0"}}>
              <button style={styles.btnCancel} onClick={() => setModal(null)}>Batal</button>
              <button style={styles.btnSave} onClick={saveMapel}>Simpan Mata Pelajaran</button>
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
              Hapus mata pelajaran "{mapelList.find((k) => k.id === deleteConfirm.mapelId)?.nama_mata_pelajaran}"? Seluruh Topik di dalamnya akan ikut terhapus.
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center", marginTop: "20px" }}>
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

      {/* ── Toast Notifications ── */}
      <div style={{ position: "fixed", bottom: "24px", right: "24px", display: "flex", flexDirection: "column", gap: "10px", zIndex: 2000 }}>
        {toasts.map((t) => (
          <div key={t.id} style={{ display: "flex", alignItems: "center", gap: "10px", background: t.type === "success" ? "#F0FDF4" : "#FFF1F2", border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`, color: t.type === "success" ? "#15803D" : "#9F1239", borderRadius: "10px", padding: "12px 16px", fontSize: "13px", fontWeight: 600, boxShadow: "0 4px 16px rgba(0,0,0,0.10)", minWidth: "260px", maxWidth: "360px" }}>
            <span style={{ fontSize: "16px" }}>{t.type === "success" ? "✅" : "❌"}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))} style={{ background: "none", border: "none", cursor: "pointer", color: "inherit", opacity: 0.6, fontSize: "14px", padding: "0 2px" }}>✕</button>
          </div>
        ))}
      </div>
    </div>
  );
}