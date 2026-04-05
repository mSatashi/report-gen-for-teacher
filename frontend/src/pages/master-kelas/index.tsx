import { useEffect, useState } from "react";
import { styles } from "./styles";
import { IconChevron, IconClose, IconEdit, IconPlus, IconTrash, IconUsers } from "../../icons";
import type { Kelas, Siswa } from "../../types";
import { useKelasApi } from "./useKelasApi";
import type { KelasResponse, Toast } from "../../service/payload";

type ModalMode = "add-kelas" | "edit-kelas" | "add-siswa" | "edit-siswa" | null;

const jkBadge = (jk: string): React.CSSProperties => ({
  display: "inline-block",
  background: jk === "P" ? "#FDF2F8" : "#EFF8FF",
  color: jk === "P" ? "#D53F8C" : "#3182CE",
  borderRadius: "6px",
  padding: "2px 10px",
  fontSize: "11px",
  fontWeight: 700,
});

const uid = () => Math.random().toString(36).slice(2, 9);

const emptyKelas = (): Omit<Kelas, "id" | "siswa"> => ({
  nama: "", mata_pelajaran: "", pengajar_id: "", kredit: "", jadwal: "",
});

let toastId = 0;

export default function MasterKelas() {
  const [kelasList, setKelasList] = useState<Kelas[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [modal, setModal] = useState<ModalMode>(null);
  const [kelasForm, setKelasForm] = useState(emptyKelas());
  const [siswaForm, setSiswaForm] = useState(emptySiswa());
  const [editingKelasId, setEditingKelasId] = useState<string | null>(null);
  const [editingSiswaId, setEditingSiswaId] = useState<string | null>(null);
  const [targetKelasId, setTargetKelasId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ type: "kelas" | "siswa"; kelasId: string; siswaId?: string } | null>(null);

  const { status, errorMsg, loadKelas, submitCreateKelas, submitUpdateKelas, submitDeleteKelas} = useKelasApi();

  const isLoading = status === "loading";

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const toggleExpand = (id: string) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  // ── Kelas CRUD ──
  const openAddKelas = () => {
    setKelasForm(emptyKelas());
    setEditingKelasId(null);
    setModal("add-kelas");
  };

  // ── Siswa CRUD ──
  const openAddSiswa = (kelasId: string) => {
    setSiswaForm(emptySiswa());
    setEditingSiswaId(null);
    setTargetKelasId(kelasId);
    setModal("add-siswa");
  };

  const openEditSiswa = (kelasId: string, s: Siswa) => {
    setSiswaForm({ nama: s.nama, nis: s.nis, jenisKelamin: s.jenisKelamin, tanggalLahir: s.tanggalLahir, alamat: s.alamat });
    setEditingSiswaId(s.id);
    setTargetKelasId(kelasId);
    setModal("edit-siswa");
  };

  const saveSiswa = () => {
    if (!siswaForm.nama.trim() || !targetKelasId) return;
    setKelasList((prev) =>
      prev.map((k) => {
        if (k.id !== targetKelasId) return k;
        if (editingSiswaId) {
          return { ...k, siswa: k.siswa.map((s) => s.id === editingSiswaId ? { ...s, ...siswaForm } : s) };
        }
        return { ...k, siswa: [...k.siswa, { id: uid(), ...siswaForm }] };
      })
    );
    setModal(null);
  };

  const deleteSiswa = (kelasId: string, siswaId: string) => {
    setKelasList((prev) =>
      prev.map((k) =>
        k.id === kelasId ? { ...k, siswa: k.siswa.filter((s) => s.id !== siswaId) } : k
      )
    );
    setDeleteConfirm(null);
  };

  const isModalKelas = modal === "add-kelas" || modal === "edit-kelas";

  const mapApiToKelas = (data: KelasResponse): Kelas => ({
    id: data.id,
    nama: data.nama,
    mata_pelajaran: data.mata_pelajaran,
    pengajar_id: data.pengajar_id,
    kredit: data.kredit,
    jadwal: data.jadwal,
    created_at: data.created_at,
    siswa: [],
  });

  useEffect(() => {
    loadKelas().then((data) => {
      if (data.length) setKelasList(data.map(mapApiToKelas));
    });
  }, []);

  const totalSiswa = kelasList.reduce((a, k) => a + k.siswa.length, 0);

  const openEditKelas = (k: Kelas) => {
    setKelasForm({ 
      nama: k.nama, 
      mata_pelajaran: k.mata_pelajaran, 
      pengajar_id: k.pengajar_id, 
      kredit: k.kredit, 
      jadwal: k.jadwal, 
      created_at: k.created_at 
    });
    setEditingKelasId(k.id);
    setModal("edit-kelas");
  };

  const saveKelas = async () => {
    if (!kelasForm.nama.trim()) return;
    if (editingKelasId) {
      /** update */
      const result = await submitUpdateKelas(editingKelasId, kelasForm);
      if (result) {
        setKelasList((prev) =>
          prev.map((k) =>
            k.id === editingKelasId ? { ...k, ...mapApiToKelas(result), siswa: k.siswa } : k
          )
        );
        showToast("Kelas berhasil diperbarui ✓", "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal memperbarui kelas", "error");
      }
    } else {
      /** create */
      const result = await submitCreateKelas(kelasForm);
      if (result) {
        const newKelas = mapApiToKelas(result);
        setKelasList((prev) => [...prev, newKelas]);
        setExpanded((prev) => ({ ...prev, [newKelas.id]: true }));
        showToast(`Kelas ${newKelas.nama} berhasil ditambahkan ✓`, "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal membuat kelas", "error");
      }
    }
    setModal(null);
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
        <h2 style={styles.title}>Master Kelas &amp; Siswa</h2>
        <p style={styles.subtitle}>Kelola data kelas dan daftar siswa per kelas</p>
      </div>

      {/* ── Stats ── */}
      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>🏫</div>
          <div>
            <div style={styles.statLabel}>Total Kelas</div>
            <div style={styles.statValue}>{kelasList.length}</div>
          </div>
        </div>
        <div style={styles.statCard}>
          <div style={{ ...styles.statIcon, background: "#F0FFF4", color: "#38A169" }}>👥</div>
          <div>
            <div style={styles.statLabel}>Total Siswa</div>
            <div style={styles.statValue}>{totalSiswa}</div>
          </div>
        </div>
      </div>

      {/* ── Toolbar ── */}
      <div style={styles.toolbar}>
        <span style={{ fontSize: "14px", fontWeight: 600, color: "#6B7FA3" }}>
          {kelasList.length} kelas ditemukan
        </span>
        <button style={styles.btnPrimary} onClick={openAddKelas}>
          <IconPlus /> Tambah Kelas
        </button>
      </div>

      {/* ── Kelas List ── */}
      {kelasList.length === 0 && (
        <div style={{ ...styles.kelasCard, ...styles.emptyState }}>
          <div style={{ fontSize: "32px", marginBottom: "8px" }}>🏫</div>
          Belum ada kelas. Klik "Tambah Kelas" untuk memulai.
        </div>
      )}

      {kelasList.map((kelas) => {
        const isOpen = !!expanded[kelas.id];
        return (
          <div key={kelas.id} style={styles.kelasCard}>
            {/* Header */}
            <div style={styles.kelasHeader} onClick={() => toggleExpand(kelas.id)}>
              <div style={styles.kelasTitle}>
                <div style={styles.kelasBadge}>Kelas {kelas.nama}</div>
                <div style={styles.kelasMeta}>
                  <span style={styles.metaItem}>
                    Mata Pelajaran&nbsp;<span style={styles.metaLabel}>{kelas.mata_pelajaran || "–"}</span>
                  </span>
                  <span style={styles.metaItem}>
                    Kredit&nbsp;<span style={styles.metaLabel}>{kelas.kredit || "–"}</span>
                  </span>
                  <span style={styles.metaItem}>
                    Jadwal&nbsp;<span style={styles.metaLabel}>{kelas.jadwal}</span>
                  </span>
                  <span style={styles.siswaCount}>
                    <IconUsers /> {kelas.siswa.length} siswa
                  </span>
                </div>
              </div>
              <div style={styles.kelasActions}>
                <button style={styles.btnEdit} onClick={(e) => { e.stopPropagation(); openEditKelas(kelas); }}>
                  <IconEdit /> Edit
                </button>
                <button style={styles.btnDanger} onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ type: "kelas", kelasId: kelas.id }); }}>
                  <IconTrash /> Hapus
                </button>
                <IconChevron open={isOpen} />
              </div>
            </div>

            {/* Siswa Table */}
            {isOpen && (
              <>
                <div style={styles.tableWrapper}>
                  {kelas.siswa.length === 0 ? (
                    <div style={styles.emptyState}>Belum ada siswa di kelas ini.</div>
                  ) : (
                    <table style={styles.siswaTable}>
                      <thead>
                        <tr>
                          <th style={styles.th}>#</th>
                          <th style={styles.th}>NIS</th>
                          <th style={styles.th}>Nama Siswa</th>
                          <th style={styles.th}>JK</th>
                          <th style={styles.th}>Tgl Lahir</th>
                          <th style={styles.th}>Alamat</th>
                          <th style={styles.th}>Aksi</th>
                        </tr>
                      </thead>
                      <tbody>
                        {kelas.siswa.map((s, i) => (
                          <tr key={s.id}>
                            <td style={{ ...styles.td, color: "#8A9BB0", fontWeight: 600 }}>{i + 1}</td>
                            <td style={{ ...styles.td, fontFamily: "monospace", fontSize: "12px" }}>{s.nis}</td>
                            <td style={{ ...styles.td, fontWeight: 600 }}>{s.nama}</td>
                            <td style={styles.td}><span style={jkBadge(s.jenisKelamin)}>{s.jenisKelamin === "P" ? "Perempuan" : "Laki-laki"}</span></td>
                            <td style={styles.td}>{s.tanggalLahir || "–"}</td>
                            <td style={{ ...styles.td, color: "#6B7FA3", maxWidth: "180px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{s.alamat || "–"}</td>
                            <td style={styles.td}>
                              <div style={{ display: "flex", gap: "6px" }}>
                                <button style={styles.btnEdit} onClick={() => openEditSiswa(kelas.id, s)}><IconEdit /></button>
                                <button style={styles.btnDanger} onClick={() => setDeleteConfirm({ type: "siswa", kelasId: kelas.id, siswaId: s.id })}><IconTrash /></button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
                <div style={styles.addSiswaRow}>
                  <button style={styles.btnSecondary} onClick={() => openAddSiswa(kelas.id)}>
                    <IconPlus /> Tambah Siswa
                  </button>
                </div>
              </>
            )}
          </div>
        );
      })}

      {/* ── Modal Kelas ── */}
      {isModalKelas && (
        <div style={styles.overlay} onClick={() => setModal(null)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>{modal === "add-kelas" ? "Tambah Kelas Baru" : "Edit Kelas"}</div>
            <div style={styles.modalSubtitle}>Isi informasi kelas di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Nama Kelas *</label>
              <input style={styles.input} placeholder="Masukkan nama kelas" value={kelasForm.nama}
                onChange={(e) => setKelasForm((f) => ({ ...f, nama: e.target.value }))} />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Mata Pelajaran *</label>
              <input style={styles.input} placeholder="Masukkan nama mata pelajaran" value={kelasForm.mata_pelajaran}
                onChange={(e) => setKelasForm((f) => ({ ...f, mata_pelajaran: e.target.value }))} />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Kredit *</label>
              <input style={styles.input} placeholder="Masukkan jumlah sesi/kredit" value={kelasForm.kredit}
                onChange={(e) => setKelasForm((f) => ({ ...f, kredit: e.target.value }))} />
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Jadwal</label>
              <input style={styles.input} placeholder="Masukkan jadwal" value={kelasForm.jadwal}
                onChange={(e) => setKelasForm((f) => ({ ...f, jadwal: e.target.value }))} />
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

      {/* ── Modal Siswa ── */}
      {isModalSiswa && (
        <div style={styles.overlay} onClick={() => setModal(null)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button style={styles.closeBtn} onClick={() => setModal(null)}><IconClose /></button>
            <div style={styles.modalTitle}>{modal === "add-siswa" ? "Tambah Siswa" : "Edit Data Siswa"}</div>
            <div style={styles.modalSubtitle}>
              Kelas: <b>{kelasList.find((k) => k.id === targetKelasId)?.nama}</b>
            </div>

            <div style={styles.row2}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Nama Siswa *</label>
                <input style={styles.input} placeholder="Nama lengkap" value={siswaForm.nama}
                  onChange={(e) => setSiswaForm((f) => ({ ...f, nama: e.target.value }))} />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>NIS</label>
                <input style={styles.input} placeholder="Nomor induk siswa" value={siswaForm.nis}
                  onChange={(e) => setSiswaForm((f) => ({ ...f, nis: e.target.value }))} />
              </div>
            </div>
            <div style={styles.row2}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Jenis Kelamin</label>
                <select style={styles.select} value={siswaForm.jenisKelamin}
                  onChange={(e) => setSiswaForm((f) => ({ ...f, jenisKelamin: e.target.value as "L" | "P" }))}>
                  <option value="L">Laki-laki</option>
                  <option value="P">Perempuan</option>
                </select>
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Tanggal Lahir</label>
                <input type="date" style={styles.input} value={siswaForm.tanggalLahir}
                  onChange={(e) => setSiswaForm((f) => ({ ...f, tanggalLahir: e.target.value }))} />
              </div>
            </div>
            <div style={styles.formGroup}>
              <label style={styles.label}>Alamat</label>
              <input style={styles.input} placeholder="Alamat lengkap" value={siswaForm.alamat}
                onChange={(e) => setSiswaForm((f) => ({ ...f, alamat: e.target.value }))} />
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
        <div style={styles.overlay} onClick={() => setDeleteConfirm(null)}>
          <div style={{ ...styles.modal, maxWidth: "380px" }} onClick={(e) => e.stopPropagation()}>
            <div style={{ fontSize: "36px", textAlign: "center", marginBottom: "12px" }}>⚠️</div>
            <div style={{ ...styles.modalTitle, textAlign: "center" }}>Konfirmasi Hapus</div>
            <div style={{ ...styles.modalSubtitle, textAlign: "center", marginBottom: "0" }}>
              {deleteConfirm.type === "kelas"
                ? `Hapus kelas "${kelasList.find((k) => k.id === deleteConfirm.kelasId)?.nama}"? Semua siswa dalam kelas ini akan ikut terhapus.`
                : `Hapus siswa "${kelasList.find((k) => k.id === deleteConfirm.kelasId)?.siswa.find((s) => s.id === deleteConfirm.siswaId)?.nama}"?`}
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button style={{ ...styles.btnSave, background: "linear-gradient(135deg, #E53E3E, #C53030)" }}
                onClick={() => {
                  if (deleteConfirm.type === "kelas") deleteKelas(deleteConfirm.kelasId);
                  else deleteSiswa(deleteConfirm.kelasId, deleteConfirm.siswaId!);
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