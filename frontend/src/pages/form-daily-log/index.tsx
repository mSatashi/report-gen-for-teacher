import { useEffect, useState } from "react";
import type { DailyLogPayload, DailyLogResponse, MapelResponse, SiswaResponse } from "../../service/payload";
import { inputStyle, KETERLIBATAN_OPTIONS, METODE_OPTIONS, PEMAHAMAN_OPTIONS, textareaStyle } from "../daily-log/components/constants";
import { styles, toggleBtnStyle, toastItemStyle } from "./styles";
import { useDailyLog } from "./useDailyLog";
import type { Toast } from "../../types";
import { fonts } from "../../components/fontstyle";

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
      style={{ ...styles.btnSimpanLog, 
        padding: size === "sm" ? "8px 20px" : "9px 24px" }}
    >
      Simpan Log
    </button>
  );

const Label: React.FC<{ text: string; optional?: boolean }> = ({ text, optional }) => (
  <div style={styles.label}>
    {text}
    {optional && <span style={styles.optional}>(opsional)</span>}
  </div>
);

let toastId = 0;

export default function DailyLogFormLog({ 
  onNavigate, namaSiswa, mapel, kelasId, siswa, dataLog 
}: DailyLogFormLogProps) {

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
  
    if (dataLog?.id) {
      if (!dataLog?.id) return;

      const result = await submitUpdateLog(dataLog?.id, payload);
      if (result) {
        setLogResult((prev) => [...prev, result]);
        onNavigate?.("logSiswa", { siswaId: siswa.id, kelasId, mapel, siswa })
        showToast("Daily log berhasil diperbarui", "success");
      } else {
        showToast("Gagal memperbarui daily log", "error");
      }  
    } else {  
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


  useEffect(() => {
    if (selectedSiswaId === null) return;
    loadLogSiswa(selectedSiswaId).then((data) => {
      setLogResult(data);
    });
  }, [selectedSiswaId]);

  return (
    <div style={styles.ctnMain}>

      {/* ── Page header ── */}
      <div
        style={styles.header}
      >
        <div>
          <h2 style={fonts.h2}>
            Daily Log
          </h2>
          <p style={styles.tagP}>
            Catat aktivitas belajar siswa hari ini
          </p>
        </div>
        <div style={styles.buttonRightWrapper}>
          <button
            onClick={(e) => { e.stopPropagation(); 
              onNavigate?.("logSiswa", { 
                siswaId: siswa.id, 
                kelasId, mapel, siswa 
              }) }}
            style={styles.btnKembali}
          >
            ← Kembali
          </button>
          <SaveButton onClick={() => onSave(logForm)} size="sm" />
        </div>
      </div>

      {/* ── Scrollable body ── */}
      <div style={styles.ctnScroll}>

        {/* Row 1: Informasi Sesi + Evaluasi */}
        <div style={styles.row}>

          {/* Informasi Sesi Belajar */}
          <div style={styles.cardStyle}>
            <h3 style={fonts.h3}>
              Informasi Sesi Belajar
            </h3>
            <div style={styles.cardContent}>
              <div>
                <Label text="Siswa" />
                <div style={styles.cardInitialWrapper}>
                  <div
                    style={styles.filedInitialStyle}
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
                <div style={styles.inputWrapper}>
                  <div style={styles.lockedFieldStyle}>{mapel?.nama_mata_pelajaran ?? "Mata Pelajaran"}</div>
                </div>
              </div>
              <div>
                <Label text="Topik / Materi" />
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
          <div style={styles.cardStyle}>
            <h3 style={fonts.h3}>
              Evaluasi &amp; Catatan
            </h3>

            <Label text="Tingkat Pemahaman Siswa" />
            <div style={styles.inputTingkatPemahamanWrapper}>
              {PEMAHAMAN_OPTIONS.map((opt) => {
                const active = logForm.tingkat_pemahaman === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => setLogForm((f) => ({ ...f, tingkat_pemahaman: opt.value }))}
                    style={toggleBtnStyle(active, opt.activeBg)}
                  >
                    {opt.emoji} {opt.value}
                  </button>
                );
              })}
            </div>

            <Label text="Tingkat Keterlibatan" />
            <div style={styles.inputTingkatPemahamanWrapper}>
              {KETERLIBATAN_OPTIONS.map((opt) => {
                const active = logForm.tingkat_keterlibatan === opt.value;
                return (
                  <button
                    key={opt.value}
                    onClick={() => setLogForm((f) => ({ ...f, tingkat_keterlibatan: opt.value }))}
                    style={toggleBtnStyle(active, opt.activeBg)}
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
        <div style={{ ...styles.capaianCard }}>
          <div style={styles.capaianHeader}>
            <h3 style={styles.capaianTitle}>Capaian &amp; Kompetensi</h3>
            <span style={styles.capaianBadge}>📋 Sesuai kurikulum</span>
          </div>

          <div style={styles.capaianGrid}>

            <div>
              <Label text="Target Materi Berikutnya" />
              <select value={logForm.target_materi_berikutnya} 
                onChange={(e) => setLogForm((f) => ({ 
                  ...f, target_materi_berikutnya: e.target.value 
                }))} 
                style={inputStyle}>
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
        <div style={styles.bottomBar}>
          <button
            onClick={(e) => { e.stopPropagation(); onNavigate?.("logSiswa", { siswaId: siswa.id, kelasId, mapel, siswa }) }}
            style={styles.btnBatal}
          >
            Batal
          </button>
          {/* <SaveButton onClick={() => onSave(form)} size="sm" /> */}
        </div>

        {/* ── Toast Notifications ── */}
        <div style={styles.toastContainer}>
          {toasts.map((t) => (
            <div key={t.id} style={{ ...toastItemStyle(t.type), color: t.type === "success" ? "#15803D" : "#9F1239" }}>
              <span style={{ fontSize: "16px" }}>
                {t.type === "success" ? "✅" : "❌"}
              </span>
              <span style={{ flex: 1 }}>{t.message}</span>
              <button
                onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
                style={styles.toastCloseBtn}
              >✕</button>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};