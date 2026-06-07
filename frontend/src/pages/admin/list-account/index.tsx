import { useEffect, useMemo, useState } from "react";
import { IconClose, IconPlus, IconTrash, IconUsers } from "../../../icons";
import { styles } from "./styles";
import type { PenggunaPayload, PenggunaResponse } from "../../../service/payload";
import type { ModalMode, Toast, ToastType } from "../../../types";
import { usePenggunaApi } from "./usePenggunaApi";

const emptyPengguna = (): PenggunaPayload => ({
  email_address: "",
  username: "",
  password: "",
  tipe_pengguna: "pengajar",
  confirmPassword: "",
});

let toastId = 0;

type Props = {
  initialData?: PenggunaResponse[];
};

export default function ListAkun({ initialData = [] }: Props) {
  const [keyword, setKeyword] = useState("");
  const [modal, setModal] = useState<ModalMode>(null);
  const [penggunaForm, setPenggunaForm] = useState(emptyPengguna());
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [penggunaList, setPenggunaList] = useState<PenggunaResponse[]>(initialData);
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string } | null>(null);

  const { errorMsg, loadPengguna, submitPengguna, sumbitDeletePengguna } = usePenggunaApi();

  const showToast = (message: string, type: ToastType) => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3500);
  };

  const openAddPengguna = () => {
    setPenggunaForm(emptyPengguna());
    setModal("add-pengguna");
  };

  const savePengguna = async () => {
    if (!penggunaForm.username.trim()) {
      showToast("Username wajib diisi", "error");
      return;
    }

    if (!penggunaForm.email_address.trim()) {
      showToast("Email wajib diisi", "error");
      return;
    }

    if (!penggunaForm.password.trim()) {
      showToast("Password wajib diisi", "error");
      return;
    }

    if (penggunaForm.password !== penggunaForm.confirmPassword) {
      showToast("Password dan konfirmasi password tidak cocok", "error");
      return;
    }

    /** create */
    const result = await submitPengguna(penggunaForm);
    if (result) {
      const freshData = await loadPengguna();
      if (freshData?.length) setPenggunaList(freshData);
      
      showToast(`Pengguna berhasil ditambahkan ✓`, "success");
      setModal(null);
    } else {
      showToast(errorMsg ?? "Gagal membuat pengguna", "error");
    }
  };

  const deleteAkun = async (id: string) => {
    const ok = await sumbitDeletePengguna(id);
    if (ok) {
      setPenggunaList((prev) => prev.filter((k) => k.id !== id));
      showToast("Pengguna berhasil dihapus", "success");
    } else {
      showToast(errorMsg ?? "Gagal menghapus pengguna", "error");
    }
    setDeleteConfirm(null);
  };

  useEffect(() => {
    loadPengguna().then((data) => {
      if (data?.length) setPenggunaList(data);
    });
  }, []);

  const filteredPengguna = useMemo(() => {
    const q = keyword.trim().toLowerCase();

    return penggunaList.filter((p) => {
      if (!q) return true;

      return (
        p.email_address.toLowerCase().includes(q) ||
        p.username.toLowerCase().includes(q)
      );
    });
  }, [penggunaList, keyword]);

  return (
      <div style={styles.root}>
        <div style={styles.header}>
          <h2 style={styles.title}>Data  Pengguna</h2>
          <p style={styles.subtitle}>Kelola data pengguna</p>
        </div>
  
        <div style={styles.statsRow}>
          <div style={styles.statCard}>
            <div style={styles.statIcon}>
              <IconUsers />
            </div>
            <div>
              <div style={styles.statLabel}>Total Pengajar</div>
              <div style={styles.statValue}>{penggunaList.length}</div>
            </div>
          </div>
        </div>
  
        <div style={styles.toolbar}>
          <div style={{ flex: 1, minWidth: 260 }}>
            <input
              type="text"
              placeholder="Cari username, email ..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              style={styles.input}
            />
          </div>
  
          <button type="button" onClick={openAddPengguna} style={styles.btnPrimary}>
            <IconPlus />
            Tambah Pengguna
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
                Daftar Pengguna
              </div>
              <div style={{ fontSize: "13px", color: "#8A9BB0", marginTop: "4px" }}>
                {filteredPengguna.length} pengguna ditemukan
              </div>
            </div>
          </div>

        {filteredPengguna.length === 0 ? (
          <div style={styles.emptyState}>
            <div style={{ fontSize: "28px", marginBottom: "10px" }}>👥</div>
            Belum ada data pengguna. Klik "Tambah Pengguna" untuk memulai.
          </div>
        ) : (
          <div style={styles.tableWrapper}>
            <table style={styles.dataTable}>
              <thead>
                <tr>
                  <th style={{ ...styles.th, width:"50px"}}>#</th>
                  <th style={{ ...styles.th, width:"200px"}}>Nama Pengguna</th>
                  <th style={{ ...styles.th, width:"300px"}}>Email Address</th>
                  <th style={{ ...styles.th, width:"50px"}}>Aksi</th>
                </tr>
              </thead>
              <tbody>
                {filteredPengguna.map((p, i) => (
                  <tr key={p.id}>
                    <td style={styles.td}>{i + 1}</td>
                    <td style={styles.td}>{p.username}</td>
                    <td style={styles.td}>{p.email_address}</td>
                    <td style={styles.td}>
                      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ id: p.id }); }}
                          style={styles.btnDanger}
                          title="Hapus pengguna"
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

      {/* ── Modal Kelas ── */}
      {modal && (
        <div style={styles.overlay}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <button type="button" onClick={() => setModal(null)} style={styles.closeBtn}>
              <IconClose />
            </button>

            <div style={styles.modalTitle}>
              {modal === "add-pengguna" ? "Tambah Pengguna" : "Edit Data Pengguna"}
            </div>
            <div style={styles.modalSubtitle}>Isi informasi pengguna di bawah ini</div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Username *</label>
              <input
                type="text"
                value={penggunaForm.username}
                placeholder="Masukkan username"
                required
                onChange={(e) => 
                  setPenggunaForm((f) => ({ ...f, username: e.target.value }))
                }
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Email Address *</label>
              <input
                type="text"
                value={penggunaForm.email_address}
                placeholder="Masukkan alamat email"
                required
                onChange={(e) =>
                  setPenggunaForm((f) => ({ ...f, email_address: e.target.value }))
                }
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Password *</label>
              <input
                type="password"
                value={penggunaForm.password}
                placeholder="Masukkan password"
                required
                onChange={(e) =>
                  setPenggunaForm((f) => ({ ...f, password: e.target.value }))
                }
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Konfirmasi Password *</label>
              <input
                type="password"
                value={penggunaForm.confirmPassword}
                placeholder="Masukkan password"
                required
                onChange={(e) =>
                  setPenggunaForm((f) => ({ ...f, confirmPassword: e.target.value }))
                }
                style={styles.input}
              />
            </div>

            <div style={styles.modalFooter}>
              <button type="button" onClick={() => setModal(null)} style={styles.btnCancel}>
                Batal
              </button>
              <button type="button" 
                onClick={savePengguna} 
                style={styles.btnSave}>
                {modal === "add-pengguna" ? "Simpan" : "Simpan Perubahan"}
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
              Hapus pengguna "
              {penggunaList.find((p) => p.id === deleteConfirm.id)?.username}"?
            </div>
            <div style={{ ...styles.modalFooter, justifyContent: "center" }}>
              <button style={styles.btnCancel} onClick={() => setDeleteConfirm(null)}>Batal</button>
              <button
                style={{ ...styles.btnSave, background: "#E11D48" }}
                onClick={() => deleteAkun(deleteConfirm.id)}
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