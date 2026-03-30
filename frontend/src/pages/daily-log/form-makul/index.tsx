import React, { useState } from "react";
import type { MakulEntry, MakulFormState } from "../components/types";
import { cardStyle, inputStyle, btnAddStyle } from "../components/constants";


interface DailyLogFormMakulProps {
  /** Isi untuk mode edit, kosong untuk mode tambah baru */
  initialForm?: Partial<MakulFormState>;
  data: MakulEntry[];
  onBack: () => void;
  onSave: (form: MakulFormState) => void;
  onDelete?: (id: number) => void;
}

const DEFAULT_FORM: MakulFormState = {
  nama: "",
  deskripsi: "",
};

const Label: React.FC<{ text: string; optional?: boolean }> = ({ text, optional }) => (
  <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 }}>
    {text}
    {optional && <span style={{ color: "#9ca3af", fontSize: 12 }}> (opsional)</span>}
  </label>
);

const DailyLogFormMakul: React.FC<DailyLogFormMakulProps> = ({
  initialForm,
  data,
  onBack,
  onSave,
  onDelete,
}) => {
  const [form, setForm] = useState<MakulFormState>({ ...DEFAULT_FORM, ...initialForm });
  const [editingId, setEditingId] = useState<number | null>(null);

  const set = (key: keyof MakulFormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleEdit = (item: MakulEntry) => {
    setEditingId(item.id);
    setForm({ nama: item.nama, deskripsi: item.deskripsi ?? "" });
  };

  const handleSave = () => {
    onSave(form);
    setForm(DEFAULT_FORM);
    setEditingId(null);
  };

  const handleCancel = () => {
    setForm(DEFAULT_FORM);
    setEditingId(null);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* ── Page header ── */}
      <div
        style={{
          display: "flex", justifyContent: "space-between", alignItems: "flex-start",
          marginBottom: 20, flexShrink: 0, flexWrap: "wrap", gap: 12,
        }}
      >
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 4px" }}>
            Kelola Mata Pelajaran
          </h2>
          <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
            Tambah, edit, atau hapus mata pelajaran
          </p>
        </div>
        <button
          onClick={onBack}
          style={{
            background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
            padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
          }}
        >
          ← Kembali
        </button>
      </div>

      {/* ── Scrollable body ── */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>

        {/* Form tambah / edit */}
        <div style={{ ...cardStyle }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: "0 0 20px" }}>
            {editingId ? "Edit Mata Pelajaran" : "Tambah Mata Pelajaran Baru"}
          </h3>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
            <div>
              <Label text="Nama Mata Pelajaran" />
              <input
                type="text"
                value={form.nama}
                onChange={set("nama")}
                placeholder="cth: Matematika"
                style={inputStyle}
              />
            </div>

            <div>
              <Label text="Deskripsi" optional />
              <input
                type="text"
                value={form.deskripsi}
                onChange={set("deskripsi")}
                placeholder="cth: Aljabar, Kalkulus, Statistika"
                style={inputStyle}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
            {editingId && (
              <button
                onClick={handleCancel}
                style={{
                  background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
                  padding: "8px 18px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
                }}
              >
                Batal
              </button>
            )}
            <button
              onClick={handleSave}
              disabled={!form.nama.trim()}
              style={{
                ...btnAddStyle,
                opacity: !form.nama.trim() ? 0.5 : 1,
                cursor: !form.nama.trim() ? "not-allowed" : "pointer",
              }}
            >
              {editingId ? "Simpan Perubahan" : "+ Tambah Mapel"}
            </button>
          </div>
        </div>

        {/* Daftar mata pelajaran */}
        <div style={{ ...cardStyle }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: "0 0 20px" }}>
            Daftar Mata Pelajaran ({data.length})
          </h3>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "rgba(228,230,239,0.85)" }}>
                {[
                  { label: "No",                  width: 50    },
                  { label: "Nama Mata Pelajaran",  width: "auto" },
                  { label: "Deskripsi",            width: "auto" },
                  { label: "Actions",              width: 140   },
                ].map((h) => (
                  <th
                    key={h.label}
                    style={{
                      padding: "10px 14px",
                      textAlign: "left",
                      fontWeight: 600,
                      color: "#374151",
                      width: h.width,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {h.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((item, idx) => (
                <tr
                  key={item.id}
                  style={{
                    borderBottom: "1px solid #f3f4f6",
                    background: editingId === item.id ? "#eff6ff" : "transparent",
                  }}
                >
                  <td style={{ padding: "12px 14px", color: "#6b7280" }}>{idx + 1}</td>
                  <td style={{ padding: "12px 14px", fontWeight: 500, color: "#111827" }}>{item.nama}</td>
                  <td style={{ padding: "12px 14px", color: "#6b7280" }}>{item.deskripsi ?? "—"}</td>
                  <td style={{ padding: "12px 14px" }}>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button
                        onClick={() => handleEdit(item)}
                        style={{
                          background: "#f59e0b", color: "#fff", border: "none",
                          borderRadius: 6, padding: "5px 12px",
                          fontSize: 12, fontWeight: 600, cursor: "pointer",
                        }}
                      >
                        Edit
                      </button>
                      {onDelete && (
                        <button
                          onClick={() => onDelete(item.id)}
                          style={{
                            background: "#f43f5e", color: "#fff", border: "none",
                            borderRadius: 6, padding: "5px 12px",
                            fontSize: 12, fontWeight: 600, cursor: "pointer",
                          }}
                        >
                          Hapus
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {data.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ padding: "40px 14px", textAlign: "center", color: "#9ca3af", fontSize: 13 }}>
                    Belum ada mata pelajaran.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DailyLogFormMakul;