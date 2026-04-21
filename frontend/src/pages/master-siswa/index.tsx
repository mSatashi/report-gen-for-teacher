import { useEffect, useMemo, useState } from "react";
import { styles } from "./styles";
import { IconClose, IconEdit, IconPlus, IconTrash, IconUsers } from "../../icons";
import type { ModalMode, Siswa, Toast, ToastType } from "../../types";
import { useSiswaApi } from "./useSiswaApi";
import type { SiswaResponse } from "../../service/payload";

// const uid = () => Math.random().toString(36).slice(2, 9);

const emptySiswa = (): Omit<Siswa, "id"> => ({
  username: "",
  email_address: "",
  password: undefined,
  nama: "",
  usia: "",
  level: "",
  credit_total: 0,
});

let toastId = 0;

type Props = {
  initialData?: Siswa[];
};

export default function MasterSiswa({ initialData = [] }: Props) {
  const [siswaList, setSiswaList] = useState<Siswa[]>(initialData);
  const [modal, setModal] = useState<ModalMode>(null);
  const [siswaForm, setSiswaForm] = useState(emptySiswa());
  const [, setExpanded] = useState<Record<string, boolean>>({});
  const [editingSiswaId, setEditingSiswaId] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ siswaId?: string } | null>(null);
  const [keyword, setKeyword] = useState("");
  const [toasts, setToasts] = useState<Toast[]>([]);
  // const [password, setPassword] = useState("");
  const [showPassword, ] = useState(false);
  const [, setFocused] = useState<string | null>(null);

  const { errorMsg, loadSiswa, submitCreateSiswa, submitUpdateSiswa, submitDeleteSiswa} = useSiswaApi();
  
    // const isLoading = status === "loading";

  const showToast = (message: string, type: ToastType) => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  };

  const filteredSiswa = useMemo(() => {
    const q = keyword.trim().toLowerCase();

    return siswaList.filter((s) => {
      if (!q) return true;

      return (
        s.username.toLowerCase().includes(q) ||
        s.email_address.toLowerCase().includes(q) ||
        s.nama.toLowerCase().includes(q) ||
        s.usia.toLowerCase().includes(q) ||
        s.level.toLowerCase().includes(q)
      );
    });
  }, [siswaList, keyword]);

  const totalSiswa = siswaList.length;

  const openAddSiswa = () => {
    setSiswaForm(emptySiswa());
    setEditingSiswaId(null);
    setModal("add-siswa");
  };

  const openEditSiswa = (siswa: Siswa) => {
    setSiswaForm({
      nama: siswa.nama,
      email_address: siswa.email_address,
      username: siswa.username,
      usia: siswa.usia,
      level: siswa.level,
      credit_total: siswa.credit_total,
    });
    setEditingSiswaId(siswa.id);
    setModal("edit-siswa");
  };

  const saveSiswa = async () => {
    if (!siswaForm.nama.trim()) {
      showToast("Nama siswa wajib diisi", "error");
      return;
    }

    if (editingSiswaId) {
      /** update */
      const result = await submitUpdateSiswa(editingSiswaId, siswaForm);
      if (result) {
        setSiswaList((prev) =>
          prev.map((k) =>
            k.id === editingSiswaId ? { ...k, ...mapApiToSiswa(result) } : k
          )
        );
        showToast("Siswa berhasil diperbarui ✓", "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal memperbarui siswa", "error");
      }
    } else {
      /** create */
      const result = await submitCreateSiswa(siswaForm);
      if (result) {
        const newSiswa = mapApiToSiswa(result);
        setSiswaList((prev) => [...prev, newSiswa]);
        setExpanded((prev) => ({ ...prev, [newSiswa.id]: true }));
        showToast(`Siswa ${newSiswa.nama} berhasil ditambahkan ✓`, "success");
        setModal(null);
      } else {
        showToast(errorMsg ?? "Gagal membuat siswa", "error");
      }
    }

    setModal(null);
  };

  // const deleteSiswa = async (id: string) => {
  //   const ok = await submitDeleteSiswa(id);
  //   if (ok) {
  //     setSiswaList((prev) => prev.filter((s) => s.id !== id));
  //     showToast("Siswa berhasil dihapus", "success");
  //   } else {
  //     showToast(errorMsg ?? "Gagal menghapus siswa", "error");
  //   }
  // };

  const deleteSiswa = async (id: string) => {
    const ok = await submitDeleteSiswa(id);
    if (ok) {
      setSiswaList((prev) => prev.filter((s) => s.id !== id));
      showToast("Siswa berhasil dihapus", "success");
    } else {
      showToast(errorMsg ?? "Gagal menghapus siswa", "error");
    }
    setDeleteConfirm(null);
  };

  const selectedSiswa = siswaList.find((s) => s.id === deleteConfirm);
  const isModalSiswa = modal === "add-siswa" || modal === "edit-siswa";
  
  const mapApiToSiswa = (data: SiswaResponse): Siswa => ({
    id: data.id,
    nama: data.nama,
    email_address: data.email_address,
    username: data.username,
    usia: data.usia,
    level: data.level,
    credit_total: data.credit_total,
  });

  useEffect(() => {
    loadSiswa().then((data) => {
      if (data.length) setSiswaList(data.map(mapApiToSiswa));
    });
  }, []);

  return (
    <div style={styles.root}>
      <div style={styles.header}>
        <h2 style={styles.title}>Master Siswa</h2>
        <p style={styles.subtitle}>Kelola data siswa secara mandiri</p>
      </div>

      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>
            <IconUsers />
          </div>
          <div>
            <div style={styles.statLabel}>Total Siswa</div>
            <div style={styles.statValue}>{totalSiswa}</div>
          </div>
        </div>
      </div>

      <div style={styles.toolbar}>
        <div style={{ flex: 1, minWidth: 260 }}>
          <input
            type="text"
            placeholder="Cari nama, NIS, jenis kelamin, tanggal lahir, alamat..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            style={styles.input}
          />
        </div>

        <button type="button" onClick={openAddSiswa} style={styles.btnPrimary}>
          <IconPlus />
          Tambah Siswa
        </button>
      </div>

      <div
        style={{
          background: "#fff",
          borderRadius: "14px",
          boxShadow: "0 1px 4px rgba(30,42,59,0.07)",
          overflow: "hidden",
          border: "1.5px solid #EAECF5",
        }}
      >
        <div
          style={{
            padding: "18px 22px",
            borderBottom: "1px solid #F0F2FA",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "12px",
            flexWrap: "wrap",
          }}
        >
          <div>
            <div style={{ fontSize: "16px", fontWeight: 700, color: "#1E2A3B" }}>
              Daftar Siswa
            </div>
            <div style={{ fontSize: "13px", color: "#8A9BB0", marginTop: "4px" }}>
              {filteredSiswa.length} siswa ditemukan
            </div>
          </div>
        </div>

        {filteredSiswa.length === 0 ? (
          <div style={styles.emptyState}>
            <div style={{ fontSize: "28px", marginBottom: "10px" }}>👥</div>
            Belum ada data siswa. Klik "Tambah Siswa" untuk memulai.
          </div>
        ) : (
          <div style={styles.tableWrapper}>
            <table style={styles.siswaTable}>
              <thead>
                <tr>
                  <th style={styles.th}>#</th>
                  <th style={styles.th}>Nama Siswa</th>
                  <th style={styles.th}>Email Address</th>
                  <th style={styles.th}>Usia</th>
                  <th style={styles.th}>Level</th>
                </tr>
              </thead>
              <tbody>
                {filteredSiswa.map((s, i) => (
                  <tr key={s.id}>
                    <td style={styles.td}>{i + 1}</td>
                    <td style={styles.td}>{s.nama}</td>
                    <td style={styles.td}>{s.email_address}</td>
                    <td style={styles.td}>{s.usia || "–"}</td>
                    <td style={styles.td}>{s.level || "–"}</td>
                    <td style={styles.td}>
                      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button
                          type="button"
                          onClick={() => openEditSiswa(s)}
                          style={styles.btnEdit}
                          title="Edit siswa"
                        >
                          <IconEdit />
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ siswaId: s.id }); }}
                          // onClick={() => setDeleteConfirm({ siswaId: s.id })}
                          style={styles.btnDanger}
                          title="Hapus siswa"
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

      {isModalSiswa && (
        <div style={styles.overlay} onClick={() => setModal(null)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button type="button" onClick={() => setModal(null)} style={styles.closeBtn}>
              <IconClose />
            </button>

            <div style={styles.modalTitle}>
              {modal === "add-siswa" ? "Tambah Siswa" : "Edit Data Siswa"}
            </div>
            <div style={styles.modalSubtitle}>Isi informasi siswa di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Nama Siswa *</label>
              <input
                type="text"
                value={siswaForm.nama}
                placeholder="Masukkan nama siswa"
                required
                onChange={(e) =>
                  setSiswaForm((f) => ({ ...f, nama: e.target.value }))
                }
                style={styles.input}
              />
            </div>

            <div style={styles.row2}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Email Address *</label>
                <input
                  type="text"
                  value={siswaForm.email_address}
                  placeholder="Masukkan alamat email"
                  required
                  onChange={(e) =>
                    setSiswaForm((f) => ({ ...f, email_address: e.target.value }))
                  }
                  style={styles.input}
                />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Password *</label>
                <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Masukkan password"
                    value={siswaForm.password}
                    onChange={(e) => setSiswaForm((f) => ({ ...f, password: e.target.value }))}
                    onFocus={() => setFocused("password")}
                    onBlur={() => setFocused(null)}
                    required
                    autoComplete="current-password"
                    style={styles.input}
                  />
              </div>
            </div>

            <div style={styles.row2}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Usia</label>
                <input
                  type="text"
                  value={siswaForm.usia}
                  placeholder="Masukkan usia"
                  onChange={(e) =>
                    setSiswaForm((f) => ({ ...f, usia: e.target.value }))
                  }
                  style={styles.input}
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Jenis Kelamin</label>
                <select style={styles.select} value={siswaForm.level}
                  onChange={(e) => setSiswaForm((f) => ({ ...f, level: e.target.value}))}>
                  <option value="">-- Pilih --</option>
                  <option value="SD">SD</option>
                  <option value="SMP">SMP</option>
                  <option value="SMA">SMA</option>
                </select>
              </div>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Credit Total</label>
              <input
                type="text"
                value={siswaForm.credit_total}
                placeholder="Masukkan credit total"
                onChange={(e) =>
                  setSiswaForm((f) => ({ ...f, credit_total: Number(e.target.value) }))
                }
                style={styles.input}
              />
            </div>

            <div style={styles.modalFooter}>
              <button type="button" onClick={() => setModal(null)} style={styles.btnCancel}>
                Batal
              </button>
              <button type="button" onClick={saveSiswa} style={styles.btnSave}>
                {modal === "add-siswa" ? "Tambah Siswa" : "Simpan Perubahan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {deleteConfirm && (
        <div style={styles.overlay} onClick={() => setDeleteConfirm(null)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button type="button" onClick={() => setDeleteConfirm(null)} style={styles.closeBtn}>
              <IconClose />
            </button>

            <div style={styles.modalTitle}>Konfirmasi Hapus</div>
            <div style={styles.modalSubtitle}>
              Hapus siswa "{selectedSiswa?.nama}" dari daftar?
            </div>

            <div style={styles.modalFooter}>
              <button
                type="button"
                onClick={() => setDeleteConfirm(null)}
                style={styles.btnCancel}
              >
                Batal
              </button>
              <button
                type="button"
                onClick={() => {
                  if (deleteConfirm?.siswaId)
                    deleteSiswa(deleteConfirm.siswaId);
                }}
                style={styles.btnDanger}
              >
                <IconTrash />
                Ya, Hapus
              </button>
            </div>
          </div>
        </div>
      )}

      <div
        style={{
          position: "fixed",
          right: 24,
          bottom: 24,
          display: "flex",
          flexDirection: "column",
          gap: 10,
          zIndex: 1200,
        }}
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            style={{
              minWidth: 240,
              maxWidth: 320,
              padding: "12px 14px",
              borderRadius: "12px",
              color: "#fff",
              fontSize: "13px",
              fontWeight: 600,
              boxShadow: "0 10px 30px rgba(15,22,36,0.18)",
              background: toast.type === "success" ? "#22C55E" : "#EF4444",
            }}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </div>
  );
}