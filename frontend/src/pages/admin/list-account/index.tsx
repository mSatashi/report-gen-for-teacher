import { useState } from "react";
import { IconClose, IconEdit, IconPlus, IconTrash, IconUsers } from "../../../icons";
import { styles } from "./styles";
import type { PenggunaPayload } from "../../../service/payload";
import type { ModalMode } from "../../../types";

const emptyPengguna = (): Omit<PenggunaPayload, "id"> => ({
  email_address: "",
  username: "",
  password: "",
  tipe_pengguna: "pengajar",
  confirmPassword: "",
});

export default function ListAkun() {
  const [keyword, setKeyword] = useState("");
  const [modal, setModal] = useState<ModalMode>(null);
  const [penggunaForm, setPenggunaForm] = useState(emptyPengguna());
  const [editingPenggunaId, setEditingPenggunaId] = useState<string | null>(null);

  const filteredPengguna = [
    {
      id: "1",
      username: "ahmadfauzi",
      email_address: "ahmad.fauzi@example.com"
    },
    {
      id: "2",
      username: "sitinurhaliza",
      email_address: "siti.nurhaliza@example.com"
    }
  ];

  const openAddPengguna = () => {
    setPenggunaForm(emptyPengguna());
    setEditingPenggunaId(null);
    setModal("add-pengguna");
  };

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
              <div style={styles.statValue}>{'totalSiswa'}</div>
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
                  <th style={{ ...styles.th, width:"200px"}}>Aksi</th>
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
                          // onClick={() => openEditPengguna(p.id)}
                          style={styles.btnEdit}
                          title="Edit pengguna"
                        >
                          <IconEdit />
                          Edit
                        </button>

                        <button
                          type="button"
                          // onClick={(e) => { e.stopPropagation(); setDeleteConfirm({ penggunaId: s.id }); }}
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
                // onClick={saveSiswa} 
                style={styles.btnSave}>
                {modal === "add-pengguna" ? "Simpan" : "Simpan Perubahan"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirm ── */}
      {/* {deleteConfirm && (
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
      )} */}

      {/* ── Toast Notifications ── */}
      {/* <div style={styles.toastNotif}>
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
      </div> */}
    </div>
    </div>
  );
}