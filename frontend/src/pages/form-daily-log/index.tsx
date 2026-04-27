import { useEffect, useState } from "react";
import type { DailyLogPayload, DailyLogResponse, MapelResponse, SiswaResponse } from "../../service/payload";
import { cardStyle, inputStyle, KETERLIBATAN_OPTIONS, METODE_OPTIONS, PEMAHAMAN_OPTIONS, textareaStyle } from "../daily-log/components/constants";
import { styles } from "./styles";
import { useDailyLog } from "./useDailyLog";
import type { Toast } from "../../types";

interface DailyLogFormLogProps {
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
  namaSiswa?: string | null;
  mapel: MapelResponse;
  kelasId?: string;
  siswa: SiswaResponse;
  dataLog?: DailyLogResponse | null;
}

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

let toastId = 0;

export default function DailyLogFormLog({ onNavigate, namaSiswa, mapel, kelasId, siswa, dataLog }: DailyLogFormLogProps) {
  const [logForm, setLogForm] = useState<DailyLogPayload>({
    kelas_id: dataLog?.kelas_id || kelasId || "",
    murid_id: dataLog?.murid_id || siswa.id || "",
    mata_pelajaran_id: dataLog?.mata_pelajaran_id || mapel.id || "",
    tanggal: dataLog?.tanggal || "",
    topik: dataLog?.topik || "",
    nilai: dataLog?.nilai || 0,
    tingkat_pemahaman: dataLog?.tingkat_pemahaman || "",
    tingkat_keterlibatan: dataLog?.tingkat_keterlibatan || "",
    kompetensi_dicapai: dataLog?.kompetensi_dicapai  || "",
    target_materi_berikutnya: dataLog?.target_materi_berikutnya || "",
    kendala: dataLog?.kendala || "",
    catatan: dataLog?.catatan || "",
    durasi_menit: dataLog?.durasi_menit || 0,
    metode_belajar: dataLog?.metode_belajar || "",
  });
  const [, setLogResult] = useState<DailyLogResponse[]>([]);
  const [selectedSiswaId, ] = useState<string | null>(null);
  const [toasts, setToasts] = useState<Toast[]>([]);


  const { loadLogSiswa, submitCreateLog, submitUpdateLog } = useDailyLog();

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const onSave = async (form: DailyLogPayload) => {
    if (!siswa.id || !kelasId) return;
    
      if (dataLog?.id) {
        if (!dataLog?.id) return;
        
        const payload: DailyLogPayload = {
          kelas_id: kelasId!,
          murid_id: siswa.id,
          mata_pelajaran_id: mapel.id,
          tanggal: form.tanggal,
          topik: form.topik ?? "",
          nilai: form.nilai,
          tingkat_pemahaman: form.tingkat_pemahaman,
          tingkat_keterlibatan: form.tingkat_keterlibatan,
          kompetensi_dicapai: form.kompetensi_dicapai,
          target_materi_berikutnya: form.target_materi_berikutnya,
          kendala: form.kendala ?? "",
          catatan: form.catatan ?? "",
          durasi_menit: form.durasi_menit,
          metode_belajar: form.metode_belajar,
        };
        const result = await submitUpdateLog(dataLog?.id, payload);
        if (result) {
          setLogResult((prev) => [...prev, result]);
          onNavigate?.("logSiswa", { siswaId: siswa.id, kelasId, mapel, siswa })
          showToast("Daily log berhasil diperbarui", "success");
        } else {
          showToast("Gagal memperbarui daily log", "error");
        }  
      } else {
        const payload: DailyLogPayload = {
          kelas_id: kelasId!,
          murid_id: siswa.id,
          mata_pelajaran_id: mapel.id,
          tanggal: form.tanggal,
          topik: form.topik ?? "",
          nilai: form.nilai,
          tingkat_pemahaman: form.tingkat_pemahaman,
          tingkat_keterlibatan: form.tingkat_keterlibatan,
          kompetensi_dicapai: form.kompetensi_dicapai,
          target_materi_berikutnya: form.target_materi_berikutnya,
          kendala: form.kendala ?? "",
          catatan: form.catatan ?? "",
          durasi_menit: form.durasi_menit,
          metode_belajar: form.metode_belajar,
        };
  
        const result = await submitCreateLog(payload);
        if (result) {
          setLogResult((prev) => [...prev, result]);
          onNavigate?.("logSiswa", { siswaId: siswa.id, kelasId, mapel, siswa })
          showToast("Daily log berhasil ditambahkan", "success");
        } else {
          showToast("Gagal menambahkan daily log", "error");
        }
      }
    };

  // const set = (key: keyof FormState) =>
  //   (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
  //     setForm((f) => ({ ...f, [key]: e.target.value }));

  useEffect(() => {
    if (selectedSiswaId === null) return;
    loadLogSiswa(selectedSiswaId).then((data) => {
      setLogResult(data);
    });
  }, [selectedSiswaId]);

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
            {/* {initialForm ? "Edit Daily Log" : "Input Daily Log"} */}
          </h2>
          <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
            Catat aktivitas belajar siswa hari ini
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <button
            onClick={(e) => { e.stopPropagation(); onNavigate?.("logSiswa", { siswaId: siswa.id, kelasId, mapel, siswa }) }}
            style={{
              background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
              padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
            }}
          >
            ← Kembali
          </button>
          <SaveButton onClick={() => onSave(logForm)} size="sm" />
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
              <div>
                <Label text="Siswa" />
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div
                    style={{
                      width: 28, height: 28, borderRadius: "50%",
                      background: "#eff6ff", color: "#3b82f6",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 11, fontWeight: 700, flexShrink: 0,
                    }}
                  >
                    {namaSiswa?.split(" ").map((w) => w[0]).slice(0, 2).join("")}
                  </div>
                  <div style={styles.lockedFieldStyle}>{namaSiswa}</div>
                </div>
              </div>

              <div>
                <Label text="Tanggal" />
                <input type="date" 
                  value={logForm.tanggal} 
                  onChange={(e) => setLogForm((f) => ({ ...f, tanggal: e.target.value }))} 
                  style={inputStyle} />
              </div>

              <div>
                <Label text="Mata Pelajaran" />
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={styles.lockedFieldStyle}>{mapel?.nama_mata_pelajaran ?? "Mata Pelajaran"}</div>
                </div>
              </div>
              <div>
                <Label text="Topik / Materi" />
                {/* {lockedMapel ? (
                  <div style={styles.lockedFieldStyle}>{lockedMapel}</div>
                ) : (
                  
                )} */}
                <select value={logForm.topik} onChange={(e) => setLogForm((f) => ({ ...f, topik: e.target.value }))} style={inputStyle}>
                  <option value="">-- Pilih --</option>
                  {mapel?.topik_list?.map((data) => <option key={data.nama}>{data.nama}</option>)}
                </select>
              </div>

              <div>
                <Label text="Durasi (menit)" />
                <input type="number" value={logForm.durasi_menit} onChange={(e) => setLogForm((f) => ({ ...f, durasi_menit: Number(e.target.value) }))} style={inputStyle} min={0} />
              </div>

              <div>
                <Label text="Metode Belajar" />
                <select value={logForm.metode_belajar} onChange={(e) => setLogForm((f) => ({ ...f, metode_belajar: e.target.value }))} style={inputStyle}>
                  <option value="">-- Pilih --</option>
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
                const active = logForm.tingkat_pemahaman === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => setLogForm((f) => ({ ...f, tingkat_pemahaman: opt.value }))}
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
                const active = logForm.tingkat_keterlibatan === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => setLogForm((f) => ({ ...f, tingkat_keterlibatan: opt.value }))}
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
              value={logForm.catatan} onChange={(e) => setLogForm((f) => ({ ...f, catatan: e.target.value }))}
              placeholder="cth: Siswa mampu memahami konsep dengan baik..."
              style={{ ...textareaStyle, marginBottom: 16 }}
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
              <select value={logForm.topik} onChange={(e) => setLogForm((f) => ({ ...f, topik: e.target.value }))} style={inputStyle}>
                  <option value="">-- Pilih --</option>
                  {mapel?.topik_list?.map((data) => <option key={data.nama}>{data.nama}</option>)}
                </select>
            </div>

            <div>
              <Label text="Skor / Penilaian" optional />
              <input type="text" value={logForm.nilai} onChange={(e) => setLogForm((f) => ({ ...f, nilai: Number(e.target.value) }))} placeholder="cth: 85" style={inputStyle} />
            </div>

            <div>
              <Label text="Kompetensi Dicapai" />
              <textarea
                value={logForm.kompetensi_dicapai} onChange={(e) => setLogForm((f) => ({ ...f, kompetensi_dicapai: e.target.value }))}
                placeholder="cth: Siswa mampu menyelesaikan persamaan linear satu variabel"
                style={textareaStyle}
              />
            </div>

            <div>
              <Label text="Kendala / Hambatan" optional />
              <textarea
                value={logForm.kendala} onChange={(e) => setLogForm((f) => ({ ...f, kendala: e.target.value }))}
                placeholder="cth: Kesulitan pada operasi bilangan negatif"
                style={textareaStyle}
              />
            </div>

          </div>
        </div>

        {/* Bottom action bar */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, padding: "4px 0 8px", flexShrink: 0 }}>
          <button
            onClick={(e) => { e.stopPropagation(); onNavigate?.("logSiswa", { siswaId: siswa.id, kelasId, mapel, siswa }) }}
            style={{
              background: "none", border: "1px solid #e5e7eb", borderRadius: 8,
              padding: "9px 20px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer",
            }}
          >
            Batal
          </button>
          {/* <SaveButton onClick={() => onSave(form)} size="sm" /> */}
        </div>

        {/* ── Toast Notifications ── */}
        <div style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          zIndex: 2000,
        }}>
          {toasts.map((t) => (
            <div key={t.id} style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              background: t.type === "success" ? "#F0FDF4" : "#FFF1F2",
              border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`,
              color: t.type === "success" ? "#15803D" : "#9F1239",
              borderRadius: "10px",
              padding: "12px 16px",
              fontSize: "13px",
              fontWeight: 600,
              boxShadow: "0 4px 16px rgba(0,0,0,0.10)",
              minWidth: "260px",
              maxWidth: "360px",
              animation: "slideIn 0.2s ease",
            }}>
              <span style={{ fontSize: "16px" }}>
                {t.type === "success" ? "✅" : "❌"}
              </span>
              <span style={{ flex: 1 }}>{t.message}</span>
              <button
                onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                  opacity: 0.6,
                  fontSize: "14px",
                  padding: "0 2px",
                }}
              >✕</button>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};