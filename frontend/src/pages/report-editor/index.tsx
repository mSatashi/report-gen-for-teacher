import React, { useCallback, useEffect, useRef, useState } from "react";
import type { DailyLogResponse, KelasResponse, MapelResponse, SiswaResponse } from "../../service/payload";
import type { ReportSection, SubjectStat } from "./types";
import { createReportGenerator } from "../../service/reportAPI";
import { apiFetch } from "../../service/apiFetch";

// ─────────────────────────────────────────────
// Props
// ─────────────────────────────────────────────
interface ReportEditorProps {
  siswaId?: string | null;
  kelasId?: string | null;
  siswa?: SiswaResponse | null;
  mapel?: MapelResponse | null;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

// ─────────────────────────────────────────────
// Picker types
// ─────────────────────────────────────────────
interface PickerState {
  step: "kelas" | "siswa";
  kelasList: KelasResponse[];
  siswaDiKelas: SiswaResponse[];
  mapelMap: Record<string, MapelResponse>;
  selectedKelas: KelasResponse | null;
  loading: boolean;
  error: string | null;
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────
function buildSubjectStats(logs: DailyLogResponse[], mapelNama: string): SubjectStat[] {
  if (!logs.length) return [];

  const grouped: Record<string, { total: number; count: number }> = {};
  for (const log of logs) {
    const key = log.topik ?? mapelNama;
    if (!grouped[key]) grouped[key] = { total: 0, count: 0 };
    grouped[key].total += log.nilai ?? 0;
    grouped[key].count += 1;
  }

  const PALETTE = [
    { color: "#3b82f6", bgColor: "#eff6ff" },
    { color: "#22c55e", bgColor: "#f0fdf4" },
    { color: "#f43f5e", bgColor: "#fff1f2" },
    { color: "#f59e0b", bgColor: "#fffbeb" },
    { color: "#8b5cf6", bgColor: "#f5f3ff" },
  ];

  return Object.entries(grouped)
    .slice(0, 5)
    .map(([name, { total, count }], i) => ({
      name,
      sessions: count,
      progress: Math.round(total / count),
      color: PALETTE[i % PALETTE.length].color,
      bgColor: PALETTE[i % PALETTE.length].bgColor,
    }));
}

function getPeriode(logs: DailyLogResponse[]): { mulai: string; selesai: string; label: string } {
  if (!logs.length) {
    const now = new Date().toISOString().slice(0, 10);
    return { mulai: now, selesai: now, label: "—" };
  }
  const dates = logs.map((l) => l.tanggal).sort();
  const mulai = dates[0];
  const selesai = dates[dates.length - 1];
  const fmt = (d: string) =>
    new Date(d).toLocaleDateString("id-ID", { month: "long", year: "numeric" });
  return { mulai, selesai, label: `${fmt(mulai)} – ${fmt(selesai)}` };
}

function buildDefaultSections(
  siswa: SiswaResponse,
  logs: DailyLogResponse[],
  mapelNama: string,
): ReportSection[] {
  const totalSesi = logs.length;
  const totalMenit = logs.reduce((s, l) => s + (l.durasi_menit ?? 0), 0);
  const totalJam = Math.round(totalMenit / 60);
  const avgNilai = totalSesi
    ? Math.round(logs.reduce((s, l) => s + (l.nilai ?? 0), 0) / totalSesi)
    : 0;

  const perluReview = logs.filter((l) => l.tingkat_pemahaman === "Perlu Review");
  const topikLemah = [...new Set(perluReview.map((l) => l.topik).filter(Boolean))].slice(0, 3);
  const kompetensi = [...new Set(logs.map((l) => l.kompetensi_dicapai).filter(Boolean))].slice(0, 3);
  const targetNext = [...new Set(logs.map((l) => l.target_materi_berikutnya).filter(Boolean))].slice(0, 3);
  const kendala = [...new Set(logs.map((l) => l.kendala).filter(Boolean))].slice(0, 2);

  return [
    {
      id: "ringkasan",
      emoji: "📋",
      label: "Ringkasan Periode",
      accentColor: "#f59e0b",
      content: totalSesi
        ? `${siswa.nama} telah menyelesaikan ${totalSesi} sesi belajar dengan total ±${totalJam} jam pembelajaran pada mata pelajaran ${mapelNama}. Rata-rata nilai: ${avgNilai}/100.`
        : `Belum ada data log untuk siswa ini.`,
    },
    {
      id: "capaian",
      emoji: "📝",
      label: "Capaian Akademik",
      accentColor: "#3b82f6",
      content: kompetensi.length
        ? `Kompetensi yang telah dicapai selama periode ini: ${kompetensi.join("; ")}.`
        : `Data capaian akademik belum tersedia. Tambahkan kompetensi dicapai pada log belajar.`,
    },
    {
      id: "pengembangan",
      emoji: "💡",
      label: "Area Pengembangan",
      accentColor: "#f43f5e",
      content: topikLemah.length
        ? `Topik yang masih memerlukan perhatian: ${topikLemah.join(", ")}. ${kendala.length ? `Kendala yang ditemui: ${kendala.join("; ")}.` : ""}`
        : `Tidak ada area kritis yang teridentifikasi pada periode ini.`,
    },
    {
      id: "rekomendasi",
      emoji: "🎯",
      label: "Rekomendasi Plan ke Depan",
      accentColor: "#22c55e",
      content: targetNext.length
        ? `Materi yang direkomendasikan untuk periode berikutnya: ${targetNext.join("; ")}.`
        : `Rekomendasi akan tersedia setelah data target materi ditambahkan pada log belajar.`,
    },
    {
      id: "karakter",
      emoji: "🌱",
      label: "Perkembangan Karakter",
      accentColor: "#8b5cf6",
      content: `${siswa.nama} menunjukkan keterlibatan dalam proses pembelajaran. Catatan pengajar: ${
        logs
          .map((l) => l.catatan)
          .filter(Boolean)
          .slice(0, 2)
          .join(" ") || "Belum ada catatan karakter pada log belajar."
      }`,
    },
  ];
}

function parseAiKonten(konten: string, existing: ReportSection[]): ReportSection[] {
  try {
    const parsed = JSON.parse(konten);
    if (Array.isArray(parsed)) {
      return existing.map((sec) => {
        const found = parsed.find((p: { id: string; content: string }) => p.id === sec.id);
        return found ? { ...sec, content: found.content } : sec;
      });
    }
  } catch {
    // bukan JSON
  }
  return existing.map((sec) =>
    sec.id === "ringkasan" ? { ...sec, content: konten } : sec
  );
}

// ─────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────
const card: React.CSSProperties = {
  background: "#fff",
  borderRadius: 14,
  boxShadow: "0 1px 4px rgba(0,0,0,.06)",
};

const s = {
  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(15,23,42,0.45)",
    backdropFilter: "blur(2px)",
    zIndex: 100,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
  },
  skeletonBase: {
    background: "linear-gradient(90deg,#F1F5F9 25%,#E2E8F0 50%,#F1F5F9 75%)",
    backgroundSize: "200% 100%",
    animation: "shimmer 1.4s infinite",
    borderRadius: 6,
  },
};

// ─────────────────────────────────────────────
// PickerModal — ditampilkan jika akses dari sidebar
// ─────────────────────────────────────────────
interface PickerModalProps {
  onConfirm: (siswa: SiswaResponse, kelas: KelasResponse, mapel: MapelResponse | null) => void;
  onCancel: () => void;
}

const PickerModal: React.FC<PickerModalProps> = ({ onConfirm, onCancel }) => {
  const [picker, setPicker] = useState<PickerState>({
    step: "kelas",
    kelasList: [],
    siswaDiKelas: [],
    mapelMap: {},
    selectedKelas: null,
    loading: true,
    error: null,
  });

  // Load kelas + mapel saat mount
  // apiFetch prepend base URL otomatis, path mulai dari setelah /api/v1
  useEffect(() => {
    let cancelled = false;

    const fetchKelas = apiFetch("/kelas/")
      .then((res) => { if (!res.ok) throw new Error(`${res.status}`); return res.json() as Promise<KelasResponse[]>; });
    const fetchMapel = apiFetch("/mata-pelajaran")
      .then((res) => { if (!res.ok) throw new Error(`${res.status}`); return res.json() as Promise<MapelResponse[]>; });

    Promise.allSettled([fetchKelas, fetchMapel]).then(([kelasRes, mapelRes]) => {
      if (cancelled) return;

      const rawKelas = kelasRes.status === "fulfilled" ? kelasRes.value : [];
      const kelasList: KelasResponse[] = Array.isArray(rawKelas)
        ? rawKelas
        : ((rawKelas as { data?: KelasResponse[] })?.data ?? []);

      const rawMapel = mapelRes.status === "fulfilled" ? mapelRes.value : [];
      const mapelArr: MapelResponse[] = Array.isArray(rawMapel)
        ? rawMapel
        : ((rawMapel as { data?: MapelResponse[] })?.data ?? []);

      const mapelMap: Record<string, MapelResponse> = {};
      for (const m of mapelArr) mapelMap[m.id] = m;

      setPicker((p) => ({ ...p, kelasList, mapelMap, loading: false }));
    });

    return () => { cancelled = true; };
  }, []);

  const handleSelectKelas = async (kelas: KelasResponse) => {
    setPicker((p) => ({ ...p, loading: true, error: null, selectedKelas: kelas }));
    try {
      const res = await apiFetch(`/kelas/${kelas.id}/murid`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const arr: SiswaResponse[] = Array.isArray(data) ? data : (data?.data ?? []);
      setPicker((p) => ({ ...p, siswaDiKelas: arr, step: "siswa", loading: false }));
    } catch {
      setPicker((p) => ({ ...p, loading: false, error: "Gagal memuat siswa kelas. Coba lagi." }));
    }
  };

  const handleSelectSiswa = (siswa: SiswaResponse) => {
    const { selectedKelas, mapelMap } = picker;
    if (!selectedKelas) return;
    const mapel = selectedKelas.mata_pelajaran_id
      ? (mapelMap[selectedKelas.mata_pelajaran_id] ?? null)
      : null;
    onConfirm(siswa, selectedKelas, mapel);
  };

  const modalStyle: React.CSSProperties = {
    ...card,
    width: "100%",
    maxWidth: 480,
    maxHeight: "85vh",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  };

  return (
    <div style={s.overlay} onClick={onCancel}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ padding: "24px 24px 16px", borderBottom: "1px solid #f1f5f9", flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              {picker.step === "siswa" && (
                <button
                  onClick={() => setPicker((p) => ({ ...p, step: "kelas", siswaDiKelas: [], error: null }))}
                  style={{ background: "none", border: "none", cursor: "pointer", color: "#6b7280", fontSize: 18, padding: 0, lineHeight: 1 }}
                >
                  ←
                </button>
              )}
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: "#111827", margin: 0 }}>
                  {picker.step === "kelas" ? "Pilih Kelas" : `Pilih Siswa — Kelas ${picker.selectedKelas?.nama}`}
                </h3>
                <p style={{ fontSize: 12, color: "#9ca3af", margin: "2px 0 0" }}>
                  {picker.step === "kelas"
                    ? "Pilih kelas untuk melihat daftar siswa"
                    : "Pilih siswa yang akan dibuat laporannya"}
                </p>
              </div>
            </div>
            <button
              onClick={onCancel}
              style={{ background: "none", border: "none", cursor: "pointer", color: "#9ca3af", fontSize: 20, lineHeight: 1, padding: "0 2px" }}
            >
              ✕
            </button>
          </div>

          {/* Step indicator */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 14 }}>
            {(["kelas", "siswa"] as const).map((step, i) => (
              <React.Fragment key={step}>
                <div style={{
                  display: "flex", alignItems: "center", gap: 5,
                  color: picker.step === step ? "#4F46E5" : (i < ["kelas","siswa"].indexOf(picker.step) ? "#22c55e" : "#d1d5db"),
                }}>
                  <div style={{
                    width: 20, height: 20, borderRadius: "50%", fontSize: 11, fontWeight: 700,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    background: picker.step === step ? "#EEF2FF" : (i < ["kelas","siswa"].indexOf(picker.step) ? "#dcfce7" : "#f9fafb"),
                    border: `2px solid ${picker.step === step ? "#4F46E5" : (i < ["kelas","siswa"].indexOf(picker.step) ? "#22c55e" : "#e5e7eb")}`,
                    color: picker.step === step ? "#4F46E5" : (i < ["kelas","siswa"].indexOf(picker.step) ? "#22c55e" : "#9ca3af"),
                  }}>
                    {i < ["kelas","siswa"].indexOf(picker.step) ? "✓" : i + 1}
                  </div>
                  <span style={{ fontSize: 12, fontWeight: 600, textTransform: "capitalize" }}>{step}</span>
                </div>
                {i < 1 && <div style={{ flex: 1, height: 1, background: i < ["kelas","siswa"].indexOf(picker.step) ? "#22c55e" : "#e5e7eb", maxWidth: 40 }} />}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 24px 24px" }}>
          {picker.error && (
            <div style={{ background: "#fff1f2", border: "1px solid #fda4af", borderRadius: 8, padding: "10px 14px", fontSize: 12, color: "#9f1239", marginBottom: 12 }}>
              ❌ {picker.error}
            </div>
          )}

          {picker.loading ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[1,2,3].map((i) => (
                <div key={i} style={{ ...s.skeletonBase, height: 60, borderRadius: 10 }} />
              ))}
            </div>
          ) : picker.step === "kelas" ? (
            picker.kelasList.length === 0 ? (
              <div style={{ textAlign: "center", padding: "32px 0", color: "#9ca3af", fontSize: 13 }}>
                Tidak ada kelas tersedia.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {picker.kelasList.map((kelas) => {
                  const mapelNama = kelas.mata_pelajaran_id
                    ? (picker.mapelMap[kelas.mata_pelajaran_id]?.nama_mata_pelajaran ?? "—")
                    : "—";
                  return (
                    <button
                      key={kelas.id}
                      onClick={() => handleSelectKelas(kelas)}
                      style={{
                        display: "flex", alignItems: "center", justifyContent: "space-between",
                        background: "#F8FAFC", border: "1.5px solid #E2E8F0", borderRadius: 10,
                        padding: "14px 16px", cursor: "pointer", textAlign: "left", transition: "all .15s",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "#C7D2FE";
                        e.currentTarget.style.background = "#F5F3FF";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "#E2E8F0";
                        e.currentTarget.style.background = "#F8FAFC";
                      }}
                    >
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: "#111827", marginBottom: 2 }}>
                          Kelas {kelas.nama}
                        </div>
                        <div style={{ fontSize: 12, color: "#6b7280" }}>
                          {mapelNama} · {kelas.hari} {kelas.jam}
                        </div>
                      </div>
                      <span style={{ fontSize: 18, color: "#9ca3af" }}>›</span>
                    </button>
                  );
                })}
              </div>
            )
          ) : (
            picker.siswaDiKelas.length === 0 ? (
              <div style={{ textAlign: "center", padding: "32px 0", color: "#9ca3af", fontSize: 13 }}>
                Tidak ada siswa di kelas ini.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {picker.siswaDiKelas.map((siswa) => (
                  <button
                    key={siswa.id}
                    onClick={() => handleSelectSiswa(siswa)}
                    style={{
                      display: "flex", alignItems: "center", gap: 12,
                      background: "#F8FAFC", border: "1.5px solid #E2E8F0", borderRadius: 10,
                      padding: "14px 16px", cursor: "pointer", textAlign: "left", transition: "all .15s",
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = "#C7D2FE";
                      e.currentTarget.style.background = "#F5F3FF";
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = "#E2E8F0";
                      e.currentTarget.style.background = "#F8FAFC";
                    }}
                  >
                    <div style={{
                      width: 36, height: 36, borderRadius: "50%", background: "#EEF2FF",
                      color: "#4F46E5", fontWeight: 700, fontSize: 14,
                      display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                    }}>
                      {siswa.nama.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "#111827", marginBottom: 1 }}>
                        {siswa.nama}
                      </div>
                      <div style={{ fontSize: 12, color: "#6b7280" }}>{siswa.education_level}</div>
                    </div>
                  </button>
                ))}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};

// ─────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────
interface SectionCardProps {
  section: ReportSection;
  onChange: (id: string, value: string) => void;
  disabled?: boolean;
}

const SectionCard: React.FC<SectionCardProps> = ({ section: sec, onChange, disabled }) => {
  const [focused, setFocused] = useState(false);
  return (
    <div
      style={{
        ...card,
        borderLeft: `4px solid ${sec.accentColor}`,
        padding: "22px 24px",
        flex: "1 1 340px",
        minWidth: 0,
        transition: "box-shadow .15s",
        boxShadow: focused
          ? `0 0 0 2px ${sec.accentColor}33, 0 2px 8px rgba(0,0,0,.08)`
          : "0 1px 4px rgba(0,0,0,.06)",
        opacity: disabled ? 0.6 : 1,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
        <span style={{ fontSize: 18 }}>{sec.emoji}</span>
        <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: 1.2, textTransform: "uppercase", color: sec.accentColor }}>
          {sec.label}
        </span>
      </div>
      <textarea
        disabled={disabled}
        value={sec.content}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        onChange={(e) => onChange(sec.id, e.target.value)}
        rows={5}
        style={{
          width: "100%", fontSize: 13, lineHeight: 1.75, color: "#374151",
          border: focused ? `1.5px solid ${sec.accentColor}66` : "1.5px solid transparent",
          outline: "none", cursor: disabled ? "not-allowed" : "text",
          borderRadius: 6, padding: "6px 8px",
          background: focused ? `${sec.accentColor}0d` : "#FAFAFA",
          transition: "all .15s", resize: "vertical", fontFamily: "inherit",
          boxSizing: "border-box",
        }}
      />
      {focused && (
        <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 6 }}>
          ✏️ Perubahan tersimpan otomatis saat mengetik
        </div>
      )}
    </div>
  );
};

const SubjectRow: React.FC<{ stat: SubjectStat }> = ({ stat: st }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 0, marginBottom: 16 }}>
    <div style={{ flex: "0 0 38%", fontSize: 13, color: "#374151", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" as const }}>
      {st.name}
    </div>
    <div style={{ flex: "0 0 15%", textAlign: "center" as const, fontSize: 13, color: "#6b7280" }}>{st.sessions}</div>
    <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, background: st.bgColor, borderRadius: 99, height: 6 }}>
        <div style={{ width: `${Math.min(st.progress, 100)}%`, background: st.color, borderRadius: 99, height: "100%", transition: "width .4s" }} />
      </div>
      <span style={{ fontSize: 12, fontWeight: 700, color: st.color, minWidth: 32, textAlign: "right" as const }}>
        {st.progress}%
      </span>
    </div>
  </div>
);

interface FinalizeModalProps {
  onConfirm: () => void;
  onCancel: () => void;
  siswaNama: string;
  periode: string;
}
const FinalizeModal: React.FC<FinalizeModalProps> = ({ onConfirm, onCancel, siswaNama, periode }) => (
  <div style={s.overlay} onClick={onCancel}>
    <div style={{ ...card, padding: "28px 32px", maxWidth: 400, width: "90%", textAlign: "center" }} onClick={(e) => e.stopPropagation()}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>📄</div>
      <h3 style={{ fontSize: 17, fontWeight: 700, color: "#111827", margin: "0 0 6px" }}>Finalisasi Laporan?</h3>
      <p style={{ fontSize: 13, color: "#6b7280", margin: "0 0 4px" }}><b>{siswaNama}</b></p>
      <p style={{ fontSize: 12, color: "#9ca3af", margin: "0 0 24px" }}>Periode: {periode}</p>
      <p style={{ fontSize: 13, color: "#6b7280", margin: "0 0 24px", lineHeight: 1.6 }}>
        Laporan akan disimpan dan dikirim. Tindakan ini tidak dapat dibatalkan.
      </p>
      <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
        <button onClick={onCancel} style={{ border: "1px solid #e5e7eb", background: "#fff", borderRadius: 8, padding: "9px 20px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}>
          Batal
        </button>
        <button onClick={onConfirm} style={{ background: "#111827", color: "#fff", border: "none", borderRadius: 8, padding: "9px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
          Ya, Finalisasi
        </button>
      </div>
    </div>
  </div>
);

interface LeaveModalProps {
  onConfirm: () => void;
  onCancel: () => void;
}
const LeaveModal: React.FC<LeaveModalProps> = ({ onConfirm, onCancel }) => (
  <div style={s.overlay} onClick={onCancel}>
    <div style={{ ...card, padding: "28px 32px", maxWidth: 380, width: "90%", textAlign: "center" }} onClick={(e) => e.stopPropagation()}>
      <div style={{ fontSize: 28, marginBottom: 12 }}>⚠️</div>
      <h3 style={{ fontSize: 16, fontWeight: 700, color: "#111827", margin: "0 0 8px" }}>Tinggalkan halaman?</h3>
      <p style={{ fontSize: 13, color: "#6b7280", margin: "0 0 24px", lineHeight: 1.6 }}>
        Perubahan yang belum difinalisasi akan hilang.
      </p>
      <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
        <button onClick={onCancel} style={{ border: "1px solid #e5e7eb", background: "#fff", borderRadius: 8, padding: "9px 20px", fontSize: 13, color: "#374151", cursor: "pointer" }}>
          Tetap di sini
        </button>
        <button onClick={onConfirm} style={{ background: "#ef4444", color: "#fff", border: "none", borderRadius: 8, padding: "9px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
          Ya, tinggalkan
        </button>
      </div>
    </div>
  </div>
);

function SectionSkeleton() {
  return (
    <div style={{ ...card, borderLeft: "4px solid #E2E8F0", padding: "22px 24px", flex: "1 1 340px", minWidth: 0 }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 14, alignItems: "center" }}>
        <div style={{ ...s.skeletonBase, width: 22, height: 22, borderRadius: "50%" }} />
        <div style={{ ...s.skeletonBase, width: 120, height: 11 }} />
      </div>
      {[100, 90, 95, 80, 70].map((w, i) => (
        <div key={i} style={{ ...s.skeletonBase, width: `${w}%`, height: 13, marginBottom: 10 }} />
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────
const ReportEditor: React.FC<ReportEditorProps> = ({ siswaId, kelasId, siswa, mapel, onNavigate }) => {
  // ── Resolved context (bisa dari props atau dari PickerModal) ─────
  const [resolvedSiswaId, setResolvedSiswaId]   = useState<string>(siswaId ?? "");
  const [resolvedKelasId, setResolvedKelasId]   = useState<string>(kelasId ?? "");
  const [resolvedSiswa, setResolvedSiswa]       = useState<SiswaResponse | null>(siswa ?? null);
  const [resolvedMapel, setResolvedMapel]       = useState<MapelResponse | null>(mapel ?? null);

  // Apakah perlu tampilkan PickerModal?
  // True jika tidak ada siswa yang diteruskan dari props
  const [showPicker, setShowPicker]             = useState<boolean>(!siswa || !siswaId);

  // ── Report state ─────────────────────────────
  const [logs, setLogs]             = useState<DailyLogResponse[]>([]);
  const [sections, setSections]     = useState<ReportSection[]>([]);
  const [stats, setStats]           = useState<SubjectStat[]>([]);
  const [periode, setPeriode]       = useState({ mulai: "", selesai: "", label: "—" });

  const [loadingLogs, setLoadingLogs]       = useState(false);
  const [loadingAi, setLoadingAi]           = useState(false);
  const [sending, setSending]               = useState(false);
  const [finalized, setFinalized]           = useState(false);
  const [hasUnsaved, setHasUnsaved]         = useState(false);
  const [showModal, setShowModal]           = useState(false);
  const [showLeaveModal, setShowLeaveModal] = useState(false);
  const [error, setError]                   = useState<string | null>(null);

  const [toasts, setToasts]         = useState<{ id: number; message: string; type: "success" | "error" }[]>([]);
  const toastIdRef = useRef(0);

  // ── Helpers ──────────────────────────────────
  const showToast = useCallback((message: string, type: "success" | "error") => {
    const id = ++toastIdRef.current;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  // ── Handler saat user selesai pilih dari PickerModal ────────────
  const handlePickerConfirm = useCallback((
    pickedSiswa: SiswaResponse,
    pickedKelas: KelasResponse,
    pickedMapel: MapelResponse | null,
  ) => {
    setResolvedSiswa(pickedSiswa);
    setResolvedSiswaId(pickedSiswa.id);
    setResolvedKelasId(pickedKelas.id);
    setResolvedMapel(pickedMapel);
    setShowPicker(false);
    // Reset state laporan karena konteks baru
    setLogs([]);
    setSections([]);
    setStats([]);
    setFinalized(false);
    setHasUnsaved(false);
    setError(null);
  }, []);

  // ── Load log siswa ──────────────────────────
  useEffect(() => {
    if (!resolvedSiswaId || resolvedSiswaId.trim() === "" || showPicker) return;

    let cancelled = false;
    setLoadingLogs(true);
    setError(null);

    (async () => {
      try {
        const res = await apiFetch(`/logs/murid/${resolvedSiswaId}`);
        if (cancelled) return;
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (cancelled) return;

        const arr: DailyLogResponse[] = Array.isArray(data) ? data : (data?.data ?? []);
        const mapelNama = resolvedMapel?.nama_mata_pelajaran ?? "—";
        setLogs(arr);
        setPeriode(getPeriode(arr));
        setStats(buildSubjectStats(arr, mapelNama));
        if (resolvedSiswa) {
          setSections(buildDefaultSections(resolvedSiswa, arr, mapelNama));
        }
      } catch (err: unknown) {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : "";
        if (msg.toLowerCase().includes("abort")) return;
        setError("Gagal memuat data log siswa. Periksa koneksi atau coba lagi.");
      } finally {
        if (!cancelled) setLoadingLogs(false);
      }
    })();

    return () => { cancelled = true; };
  }, [resolvedSiswaId, showPicker]); // intentionally exclude resolvedSiswa/Mapel untuk avoid re-fetch loop

  // ── Generate AI ──────────────────────────────
  const handleGenerateAi = useCallback(async () => {
    if (!logs.length) {
      showToast("Tidak ada data log untuk di-generate", "error");
      return;
    }
    setLoadingAi(true);
    setError(null);
    try {
      const result = await createReportGenerator({
        murid_id: resolvedSiswaId,
        kelas_id: resolvedKelasId,
        periode_mulai: periode.mulai,
        periode_selesai: periode.selesai,
        tipe_laporan: "progress",
      });
      if (result.konten) {
        setSections((prev) => parseAiKonten(result.konten, prev));
        showToast("Narasi AI berhasil di-generate!", "success");
      } else {
        showToast("AI tidak menghasilkan konten. Coba lagi.", "error");
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal generate narasi AI";
      showToast(msg, "error");
    } finally {
      setLoadingAi(false);
    }
  }, [logs, resolvedSiswaId, resolvedKelasId, periode, showToast]);

  // ── Finalisasi ────────────────────────────────
  const handleFinalize = useCallback(async () => {
    setSending(true);
    setShowModal(false);
    setError(null);
    try {
      await createReportGenerator({
        murid_id: resolvedSiswaId,
        kelas_id: resolvedKelasId,
        periode_mulai: periode.mulai,
        periode_selesai: periode.selesai,
        tipe_laporan: "final",
      });
      setFinalized(true);
      setHasUnsaved(false);
      showToast("Laporan berhasil difinalisasi dan dikirim!", "success");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal mengirim laporan";
      setError(msg);
      showToast(msg, "error");
    } finally {
      setSending(false);
    }
  }, [resolvedSiswaId, resolvedKelasId, periode, showToast]);

  // ── Handle section edit ───────────────────────
  const handleChange = useCallback((id: string, value: string) => {
    setSections((prev) => prev.map((sec) => (sec.id === id ? { ...sec, content: value } : sec)));
    setHasUnsaved(true);
  }, []);

  // ── Warn on navigate away ─────────────────────
  useEffect(() => {
    if (!hasUnsaved) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [hasUnsaved]);

  // ── Derived ───────────────────────────────────
  const totalSesi   = logs.length;
  const totalMenit  = logs.reduce((sum, l) => sum + (l.durasi_menit ?? 0), 0);
  const totalJam    = Math.round(totalMenit / 60);
  const isReadyToFinalize = sections.length > 0 &&
    sections.every((sec) => sec.content.trim().length > 20);

  // ── Nama tampilan (safe, dengan fallback) ─────
  const displayNama      = resolvedSiswa?.nama ?? "—";
  const displayLevel     = resolvedSiswa?.education_level ?? "—";
  const displayMapel     = resolvedMapel?.nama_mata_pelajaran ?? "—";
  const displayKelasId   = resolvedKelasId;

  // ─────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────
  return (
    <>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        @keyframes fadeInUp { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
      `}</style>

      {/* ── PickerModal — tampil jika akses dari sidebar (tanpa props siswa) ── */}
      {showPicker && (
        <PickerModal
          onConfirm={handlePickerConfirm}
          onCancel={() => {
            // Jika cancel dan tidak ada kelasId untuk kembali, navigasi ke dashboard atau stay
            if (displayKelasId) {
              onNavigate?.("detailKelas", { kelasId: displayKelasId });
            } else {
              onNavigate?.("home");
            }
          }}
        />
      )}

      {showModal && (
        <FinalizeModal
          onConfirm={handleFinalize}
          onCancel={() => setShowModal(false)}
          siswaNama={displayNama}
          periode={periode.label}
        />
      )}

      {showLeaveModal && (
        <LeaveModal
          onConfirm={() => {
            setShowLeaveModal(false);
            onNavigate?.("detailKelas", { kelasId: displayKelasId });
          }}
          onCancel={() => setShowLeaveModal(false)}
        />
      )}

      <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>
        <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 16 }}>

          {/* ── Header ── */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12, flexShrink: 0 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
                <span
                  style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }}
                  onClick={() => displayKelasId
                    ? onNavigate?.("detailKelas", { kelasId: displayKelasId })
                    : onNavigate?.("home")
                  }
                  onMouseEnter={(e) => (e.currentTarget.style.color = "#4F46E5")}
                  onMouseLeave={(e) => (e.currentTarget.style.color = "#9ca3af")}
                >
                  {displayKelasId ? "Detail Kelas" : "Home"}
                </span>
                <span style={{ fontSize: 13, color: "#d1d5db" }}>›</span>
                <span style={{ fontSize: 13, color: "#111827", fontWeight: 600 }}>Report Editor</span>
              </div>

              <h2 style={{ fontSize: 24, fontWeight: 800, color: "#111827", margin: "0 0 4px" }}>
                Report Editor
              </h2>
              {/* FIX: safe access dengan displayNama / displayLevel / displayMapel */}
              <p style={{ fontSize: 13, color: "#9ca3af", margin: 0 }}>
                {resolvedSiswa
                  ? `${displayNama} · ${displayLevel} · ${displayMapel} · ${periode.label}`
                  : "Pilih siswa untuk membuat laporan"}
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
              {/* Ganti Siswa — hanya tampil jika sudah ada siswa */}
              {resolvedSiswa && (
                <button
                  onClick={() => setShowPicker(true)}
                  style={{ border: "1px solid #C7D2FE", background: "#EEF2FF", borderRadius: 8, padding: "9px 16px", fontSize: 13, fontWeight: 600, color: "#4F46E5", cursor: "pointer" }}
                >
                  Ganti Siswa
                </button>
              )}

              {/* Kembali */}
              <button
                onClick={() => {
                  if (hasUnsaved) { setShowLeaveModal(true); return; }
                  displayKelasId
                    ? onNavigate?.("detailKelas", { kelasId: displayKelasId })
                    : onNavigate?.("home");
                }}
                style={{ border: "1px solid #e5e7eb", background: "#fff", borderRadius: 8, padding: "9px 16px", fontSize: 13, fontWeight: 600, color: "#374151", cursor: "pointer" }}
              >
                ← Kembali
              </button>

              {/* Generate AI */}
              <button
                disabled={loadingLogs || loadingAi || finalized || !resolvedSiswa}
                onClick={handleGenerateAi}
                style={{
                  border: "1px solid #C7D2FE",
                  background: loadingAi ? "#EEF2FF" : "#F5F3FF",
                  borderRadius: 8, padding: "9px 18px", fontSize: 13, fontWeight: 600, color: "#4F46E5",
                  cursor: (loadingLogs || loadingAi || finalized || !resolvedSiswa) ? "not-allowed" : "pointer",
                  display: "flex", alignItems: "center", gap: 6,
                  opacity: (finalized || !resolvedSiswa) ? 0.5 : 1,
                }}
              >
                {loadingAi ? (
                  <>
                    <span style={{ width: 13, height: 13, border: "2px solid #4F46E5", borderTopColor: "transparent", borderRadius: "50%", display: "inline-block", animation: "spin .7s linear infinite" }} />
                    Generating...
                  </>
                ) : "✦ Generate AI"}
              </button>

              {/* Finalisasi */}
              <button
                disabled={finalized || sending || loadingLogs || !isReadyToFinalize || !resolvedSiswa}
                title={!isReadyToFinalize ? "Isi semua seksi terlebih dahulu" : undefined}
                onClick={() => setShowModal(true)}
                style={{
                  background: finalized ? "#22c55e" : sending ? "#6b7280" : "#111827",
                  color: "#fff", border: "none", borderRadius: 8, padding: "9px 20px",
                  fontSize: 13, fontWeight: 700,
                  cursor: (finalized || sending || loadingLogs || !resolvedSiswa) ? "not-allowed" : "pointer",
                  display: "flex", alignItems: "center", gap: 8, transition: "background .3s",
                }}
              >
                {sending ? (
                  <>
                    <span style={{ width: 14, height: 14, border: "2px solid #fff", borderTopColor: "transparent", borderRadius: "50%", display: "inline-block", animation: "spin .7s linear infinite" }} />
                    Mengirim...
                  </>
                ) : finalized ? "✓ Terkirim" : "Finalisasi"}
              </button>
            </div>
          </div>

          {/* ── Error banner ── */}
          {error && (
            <div style={{ background: "#fff1f2", border: "1.5px solid #fda4af", borderRadius: 10, padding: "12px 18px", fontSize: 13, color: "#9f1239", fontWeight: 600, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span>❌ {error}</span>
              <button onClick={() => setError(null)} style={{ background: "none", border: "none", cursor: "pointer", color: "#9f1239", fontSize: 16, padding: "0 4px" }}>✕</button>
            </div>
          )}

          {/* ── Unsaved changes indicator ── */}
          {hasUnsaved && !finalized && (
            <div style={{ background: "#fffbeb", border: "1.5px dashed #f59e0b", borderRadius: 10, padding: "10px 18px", fontSize: 12, color: "#b45309", fontWeight: 600, flexShrink: 0 }}>
              ● Terdapat perubahan yang belum difinalisasi
            </div>
          )}

          {/* ── AI notice banner ── */}
          {!loadingLogs && !finalized && !hasUnsaved && resolvedSiswa && (
            <div style={{ background: "#fffbeb", border: "1.5px dashed #f59e0b", borderRadius: 10, padding: "14px 18px", fontSize: 13, color: "#b45309", fontWeight: 600, flexShrink: 0 }}>
              ✦ Draft dibangun dari <b>{totalSesi} log belajar</b> ({totalJam} jam). Klik "Generate AI" untuk narasi otomatis, atau edit langsung tiap seksi.
            </div>
          )}

          {/* ── Finalized banner ── */}
          {finalized && (
            <div style={{ background: "#f0fdf4", border: "1.5px solid #bbf7d0", borderRadius: 10, padding: "12px 18px", fontSize: 13, color: "#15803d", fontWeight: 600, flexShrink: 0 }}>
              ✓ Laporan telah berhasil difinalisasi dan dikirim untuk {displayNama}.
            </div>
          )}

          {/* ── Empty state jika belum ada siswa (picker sudah tutup) ── */}
          {!showPicker && !resolvedSiswa && (
            <div style={{ ...card, padding: "48px 24px", textAlign: "center", color: "#9ca3af" }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>📋</div>
              <p style={{ fontSize: 14, margin: "0 0 16px" }}>Belum ada siswa yang dipilih.</p>
              <button
                onClick={() => setShowPicker(true)}
                style={{ background: "#4F46E5", color: "#fff", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}
              >
                Pilih Siswa
              </button>
            </div>
          )}

          {/* ── Main content grid — hanya tampil jika ada resolvedSiswa ── */}
          {resolvedSiswa && (
            <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "flex-start", flexShrink: 0 }}>

              {/* Left: Section cards */}
              <div style={{ flex: "3 1 500px", minWidth: 0, display: "flex", flexWrap: "wrap", gap: 18, alignContent: "flex-start" }}>
                {loadingLogs
                  ? Array.from({ length: 5 }).map((_, i) => <SectionSkeleton key={i} />)
                  : sections.map((sec) => (
                    <SectionCard
                      key={sec.id}
                      section={sec}
                      onChange={handleChange}
                      disabled={finalized}
                    />
                  ))
                }
              </div>

              {/* Right: Ringkasan Statistik */}
              <div style={{ ...card, flex: "1 1 280px", minWidth: 0, padding: "22px 24px" }}>
                <h5 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: "0 0 6px" }}>
                  Ringkasan Statistik
                </h5>
                <p style={{ fontSize: 12, color: "#9ca3af", margin: "0 0 18px" }}>
                  Data dari {totalSesi} sesi log belajar
                </p>

                {/* Table header */}
                <div style={{ display: "flex", marginBottom: 12, paddingBottom: 10, borderBottom: "1px solid #f3f4f6" }}>
                  <span style={{ flex: "0 0 38%", fontSize: 10, fontWeight: 700, color: "#9ca3af", letterSpacing: 1, textTransform: "uppercase" }}>Topik</span>
                  <span style={{ flex: "0 0 15%", fontSize: 10, fontWeight: 700, color: "#9ca3af", letterSpacing: 1, textTransform: "uppercase", textAlign: "center" as const }}>Sesi</span>
                  <span style={{ flex: 1, fontSize: 10, fontWeight: 700, color: "#9ca3af", letterSpacing: 1, textTransform: "uppercase", textAlign: "center" as const }}>Avg Nilai</span>
                </div>

                {loadingLogs ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} style={{ display: "flex", gap: 8, marginBottom: 14, alignItems: "center" }}>
                      <div style={{ ...s.skeletonBase, flex: "0 0 38%", height: 12 }} />
                      <div style={{ ...s.skeletonBase, flex: "0 0 15%", height: 12 }} />
                      <div style={{ ...s.skeletonBase, flex: 1, height: 8, borderRadius: 99 }} />
                    </div>
                  ))
                ) : stats.length === 0 ? (
                  <div style={{ textAlign: "center", padding: "20px 0", color: "#9ca3af", fontSize: 13, fontStyle: "italic" }}>
                    Belum ada data statistik
                  </div>
                ) : (
                  stats.map((st) => <SubjectRow key={st.name} stat={st} />)
                )}

                {!loadingLogs && stats.length > 0 && (
                  <>
                    <div style={{ borderTop: "1px dashed #e5e7eb", margin: "16px 0" }} />
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: "#111827" }}>Total: {totalSesi} sesi</div>
                        <div style={{ fontSize: 12, color: "#9ca3af" }}>±{totalJam} jam pembelajaran</div>
                      </div>
                      <span style={{
                        background: totalSesi >= 8 ? "#dcfce7" : "#fef9c3",
                        color: totalSesi >= 8 ? "#15803d" : "#ca8a04",
                        borderRadius: 8, padding: "5px 14px", fontSize: 12, fontWeight: 700,
                      }}>
                        {totalSesi >= 8 ? "On Track" : "Perlu Perhatian"}
                      </span>
                    </div>
                  </>
                )}
              </div>

            </div>
          )}
        </div>
      </div>

      {/* ── Toast container ── */}
      <div style={{ position: "fixed", bottom: 24, right: 24, display: "flex", flexDirection: "column", gap: 10, zIndex: 2000 }}>
        {toasts.map((t) => (
          <div
            key={t.id}
            style={{
              display: "flex", alignItems: "center", gap: 10,
              background: t.type === "success" ? "#F0FDF4" : "#FFF1F2",
              border: `1.5px solid ${t.type === "success" ? "#4ADE80" : "#FDA4AF"}`,
              color: t.type === "success" ? "#15803D" : "#9F1239",
              borderRadius: 10, padding: "12px 16px", fontSize: 13, fontWeight: 600,
              boxShadow: "0 4px 16px rgba(0,0,0,0.10)", minWidth: 260, maxWidth: 360,
              animation: "fadeInUp 0.2s ease",
            }}
          >
            <span style={{ fontSize: 16 }}>{t.type === "success" ? "✅" : "❌"}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
            <button
              onClick={() => setToasts((prev) => prev.filter((x) => x.id !== t.id))}
              style={{ background: "none", border: "none", cursor: "pointer", color: "inherit", opacity: 0.6, fontSize: 14, padding: "0 2px" }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </>
  );
};

export default ReportEditor;