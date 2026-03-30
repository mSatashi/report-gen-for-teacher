import React, { useState } from "react";
import type { FormState } from "../components/types";
import {
  MAPEL_OPTIONS, METODE_OPTIONS,
  PEMAHAMAN_OPTIONS, KETERLIBATAN_OPTIONS,
  inputStyle, textareaStyle, cardStyle,
} from "../components/constants";
import { styles } from "./styles";

interface DailyLogFormLogProps {
  /** Isi untuk mode edit, kosong untuk mode tambah baru */
  initialForm?: Partial<FormState>;
  lockedSiswa?: string;
  lockedMapel?: string;
  onBack: () => void;
  onSave: (form: FormState) => void;
}

const DEFAULT_FORM: FormState = {
  siswa: "Aisya Putri",
  tanggal: new Date().toISOString().split("T")[0],
  idMapel: 1,
  mapel: "Matematika",
  topik: "",
  durasi: "90",
  metode: "Penjelasan langsung",
  pemahaman: "Sangat Paham",
  keterlibatan: "Aktif",
  catatanGuru: "",
  rekTindakLanjut: "",
  targetMateri: "",
  skor: "",
  kompetensi: "",
  kendala: "",
};

const SaveButton: React.FC<{ size?: "sm" | "md"; onClick: () => void; }> = ({ size = "md", onClick }) => (
    <button
      onClick={onClick}
      style={{
        background: "#22c55e", color: "#fff", border: "none",
        borderRadius: 8,
        padding: size === "sm" ? "8px 20px" : "9px 24px",
        fontSize: 13, fontWeight: 700, cursor: "pointer",
      }}
    >
      Simpan Log
    </button>
  );

const Label: React.FC<{ text: string; optional?: boolean }> = ({ text, optional }) => (
  <div style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 }}>
    {text}
    {optional && <span style={{ fontWeight: 400, color: "#9ca3af", marginLeft: 4 }}>(opsional)</span>}
  </div>
);

const DailyLogFormLog: React.FC<DailyLogFormLogProps> = ({ initialForm, lockedSiswa, lockedMapel, onBack, onSave }) => {
  const [form, setForm] = useState<FormState>({ 
    ...DEFAULT_FORM, 
    ...initialForm, 
    ...(lockedSiswa ? { siswa: lockedSiswa } : {}),...(lockedMapel ? { mapel: lockedMapel } : {}), });

  const set = (key: keyof FormState) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value }));

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
            {initialForm ? "Edit Daily Log" : "Input Daily Log"}
          </h2>
          <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
            Catat aktivitas belajar siswa hari ini
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <button
            onClick={onBack}
            style={{
              background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
              padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
            }}
          >
            ← Kembali
          </button>
          <SaveButton onClick={() => onSave(form)} size="sm" />
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>

        {/* Row 1: Informasi Sesi + Evaluasi */}
        <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "flex-start" }}>

          {/* Informasi Sesi Belajar */}
          <div style={{ ...cardStyle, flex: "1 1 340px", minWidth: 0 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: "0 0 20px" }}>
              Informasi Sesi Belajar
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

              {/* <div>
                <Label text="Siswa" />
                <select value={form.siswa} onChange={set("siswa")} style={inputStyle}>
                  {SISWA_OPTIONS.map((s) => <option key={s}>{s}</option>)}
                </select>
              </div> */}

              <div>
                <Label text="Siswa" />
                {lockedSiswa ? (
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div
                      style={{
                        width: 28, height: 28, borderRadius: "50%",
                        background: "#eff6ff", color: "#3b82f6",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 11, fontWeight: 700, flexShrink: 0,
                      }}
                    >
                      {lockedSiswa.split(" ").map((w) => w[0]).slice(0, 2).join("")}
                    </div>
                    <div style={styles.lockedFieldStyle}>{lockedSiswa}</div>
                  </div>
                ) : (
                  <input
                    type="text"
                    value={form.siswa}
                    onChange={set("siswa")}
                    placeholder="Nama siswa"
                    style={inputStyle}
                  />
                )}
              </div>

              <div>
                <Label text="Tanggal" />
                <input type="date" value={form.tanggal} onChange={set("tanggal")} style={inputStyle} />
              </div>

              {/* <div>
                <Label text="Mata Pelajaran" />
                <select value={form.mapel} onChange={set("mapel")} style={inputStyle}>
                  {MAPEL_OPTIONS.map((m) => <option key={m}>{m}</option>)}
                </select>
              </div> */}
              <div>
                <Label text="Mata Pelajaran" />
                {lockedMapel ? (
                  <div style={styles.lockedFieldStyle}>{lockedMapel}</div>
                ) : (
                  <select value={form.mapel} onChange={set("mapel")} style={inputStyle}>
                    {MAPEL_OPTIONS.map((m) => <option key={m}>{m}</option>)}
                  </select>
                )}
              </div>

              <div>
                <Label text="Topik / Materi" />
                <input
                  type="text" value={form.topik} onChange={set("topik")}
                  placeholder="cth: Aljabar — persamaan linear"
                  style={inputStyle}
                />
              </div>

              <div>
                <Label text="Durasi (menit)" />
                <input type="number" value={form.durasi} onChange={set("durasi")} style={inputStyle} min={0} />
              </div>

              <div>
                <Label text="Metode Belajar" />
                <select value={form.metode} onChange={set("metode")} style={inputStyle}>
                  {METODE_OPTIONS.map((m) => <option key={m}>{m}</option>)}
                </select>
              </div>

            </div>
          </div>

          {/* Evaluasi & Catatan */}
          <div style={{ ...cardStyle, flex: "1 1 300px", minWidth: 0 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: "0 0 20px" }}>
              Evaluasi &amp; Catatan
            </h3>

            <Label text="Tingkat Pemahaman Siswa" />
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 18 }}>
              {PEMAHAMAN_OPTIONS.map((opt) => {
                const active = form.pemahaman === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => setForm((f) => ({ ...f, pemahaman: opt.value }))}
                    style={{
                      border: active ? "none" : "1px solid #e5e7eb",
                      borderRadius: 8, padding: "7px 14px", fontSize: 13, fontWeight: 600,
                      cursor: "pointer",
                      background: active ? opt.activeBg : "#fff",
                      color: active ? "#fff" : "#374151",
                      transition: "all .15s",
                    }}
                  >
                    {opt.emoji} {opt.value}
                  </button>
                );
              })}
            </div>

            <Label text="Tingkat Keterlibatan" />
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 18 }}>
              {KETERLIBATAN_OPTIONS.map((opt) => {
                const active = form.keterlibatan === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => setForm((f) => ({ ...f, keterlibatan: opt.value }))}
                    style={{
                      border: active ? "none" : "1px solid #e5e7eb",
                      borderRadius: 8, padding: "7px 14px", fontSize: 13, fontWeight: 600,
                      cursor: "pointer",
                      background: active ? opt.activeBg : "#fff",
                      color: active ? "#fff" : "#374151",
                      transition: "all .15s",
                    }}
                  >
                    {opt.emoji} {opt.value}
                  </button>
                );
              })}
            </div>

            <Label text="Catatan Guru" />
            <textarea
              value={form.catatanGuru} onChange={set("catatanGuru")}
              placeholder="cth: Siswa mampu memahami konsep dengan baik..."
              style={{ ...textareaStyle, marginBottom: 16 }}
            />

            <Label text="Rekomendasi Tindak Lanjut" />
            <input
              type="text" value={form.rekTindakLanjut} onChange={set("rekTindakLanjut")}
              placeholder="cth: Review konsep sebelum lanjut ke materi berikutnya"
              style={inputStyle}
            />
          </div>
        </div>

        {/* Row 2: Capaian & Kompetensi */}
        <div style={{ ...cardStyle, flexShrink: 0 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: 0 }}>
              Capaian &amp; Kompetensi
            </h3>
            <span style={{ fontSize: 12, color: "#3b82f6", fontWeight: 600, background: "#eff6ff", borderRadius: 6, padding: "4px 10px" }}>
              📋 Sesuai kurikulum
            </span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

            <div>
              <Label text="Target Materi Berikutnya" />
              <input type="text" value={form.targetMateri} onChange={set("targetMateri")} placeholder="cth: Persamaan kuadrat" style={inputStyle} />
            </div>

            <div>
              <Label text="Skor / Penilaian" optional />
              <input type="text" value={form.skor} onChange={set("skor")} placeholder="cth: 85" style={inputStyle} />
            </div>

            <div>
              <Label text="Kompetensi Dicapai" />
              <textarea
                value={form.kompetensi} onChange={set("kompetensi")}
                placeholder="cth: Siswa mampu menyelesaikan persamaan linear satu variabel"
                style={textareaStyle}
              />
            </div>

            <div>
              <Label text="Kendala / Hambatan" optional />
              <textarea
                value={form.kendala} onChange={set("kendala")}
                placeholder="cth: Kesulitan pada operasi bilangan negatif"
                style={textareaStyle}
              />
            </div>

          </div>
        </div>

        {/* Bottom action bar */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, padding: "4px 0 8px", flexShrink: 0 }}>
          <button
            onClick={onBack}
            style={{
              background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
              padding: "9px 20px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
            }}
          >
            Batal
          </button>
          <SaveButton onClick={() => onSave(form)} size="sm" />
        </div>

      </div>
    </div>
  );
};

export default DailyLogFormLog;