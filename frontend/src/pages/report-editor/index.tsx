import React, { useState } from "react";
import { INITIAL_SECTIONS } from "./constants";
import type { ReportSection } from "./types";
import * as S from "./styles";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ReportData {
  id: string;
  murid_id: string;
  kelas_id: string;
  konten: string;
  tipe_laporan: string;
  status: string;
  pdf_path: string | null;
  tanggal: string;
  tanggal_dikirim: string | null;
  is_ai_generated: boolean;
  periode_mulai: string;
  periode_selesai: string;
  nama_siswa?: string;
  nama_kelas?: string;
  nama_mapel?: string;
}

interface ReportEditorProps {
  reportData?: ReportData | null;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const formatDate = (iso: string) => {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("id-ID", {
    day: "numeric", month: "long", year: "numeric",
  });
};

// const formatPeriode = (mulai: string, selesai: string) => {
//   if (!mulai || !selesai) return "—";
//   const fmt = (s: string) =>
//     new Date(s).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
//   return `${fmt(mulai)} – ${fmt(selesai)}`;
// };

const capitalize = (s: string) =>
  s ? s.charAt(0).toUpperCase() + s.slice(1) : "—";

const isSelesai = (s: string) => ["selesai", "finalized", "sent"].includes(s);

const parseKonten = (konten: string): ReportSection[] => {
  if (!konten) return INITIAL_SECTIONS;
  return [{
    id: "konten",
    emoji: "📋",
    label: "Laporan Perkembangan",
    accentColor: "#3b82f6",
    content: konten,
  }];
};

// ─── Info card ────────────────────────────────────────────────────────────────

const StudentInfoCard: React.FC<{ r: ReportData; status: string }> = ({ r, status }) => {
  const row1 = [
    { label: "Nama Siswa",   value: r.nama_siswa ?? "—" },
    { label: "Tanggal",      value: formatDate(r.tanggal) },
    { label: "Tipe Laporan", value: capitalize(r.tipe_laporan) },
    ...(r.nama_kelas ? [{ label: "Kelas", value: r.nama_kelas }] : []),
  ];

  // const row2: { label: string; value: string }[] = [
  //   ...(r.nama_mapel ? [{ label: "Mata Pelajaran", value: r.nama_mapel }] : []),
  //   { label: "Periode", value: formatPeriode(r.periode_mulai, r.periode_selesai) },
  // ];

  return (
    <div style={S.infoCard}>
      <div style={S.infoCardHeader}>
        <span style={{ fontSize: 14 }}>🗂️</span>
        <span style={S.infoCardHeaderTitle}>Detail Peserta</span>
        <span style={S.infoCardStatusBadge}>
          {isSelesai(status) ? "✅ Selesai" : "⏳ " + capitalize(status)}
        </span>
      </div>

      <div style={S.infoCardBodyRow}>
        {row1.map((f) => (
          <div key={f.label} style={S.infoGroup}>
            <span style={S.infoLabel}>{f.label}</span>
            <span style={S.infoValue}>{f.value}</span>
          </div>
        ))}
      </div>

      <div style={S.infoCardDivider} />

      {/* <div style={S.infoCardBodyRow}>
        {row2.map((f) => (
          <div key={f.label} style={S.infoGroup}>
            <span style={S.infoLabel}>{f.label}</span>
            <span style={S.infoValue}>{f.value}</span>
          </div>
        ))}

        {r.is_ai_generated && (
          <div style={S.infoGroup}>
            <span style={S.infoLabel}>Sumber</span>
            <span style={S.badgeAI}>✦ AI Generated</span>
          </div>
        )}

        <div style={S.infoGroup}>
          <span style={S.infoLabel}>Status</span>
          <span style={S.badgeStatus(status)}>
            {isSelesai(status) ? "Selesai" : capitalize(status)}
          </span>
        </div>
      </div> */}
    </div>
  );
};

// ─── Editable section card ────────────────────────────────────────────────────

interface SectionCardProps {
  section: ReportSection;
  onChange: (id: string, value: string) => void;
  onSave: (id: string, value: string) => void;
}

const SectionCard: React.FC<SectionCardProps> = ({ section: s, onChange, onSave }) => {
  const [focused, setFocused] = useState(false);
  const [localValue, setLocalValue] = useState(s.content);

  return (
    <div style={S.sectionCard(s.accentColor, focused)}>
      <div style={S.sectionLabelRow}>
        <span style={S.sectionEmoji}>{s.emoji}</span>
        <span style={S.sectionLabel(s.accentColor)}>{s.label}</span>
      </div>

      <div
        contentEditable
        suppressContentEditableWarning
        onFocus={() => setFocused(true)}
        onBlur={(e) => {
          setFocused(false);
          const v = e.currentTarget.innerText;
          setLocalValue(v);
          onChange(s.id, v);
        }}
        onInput={(e) => setLocalValue(e.currentTarget.textContent ?? "")}
        style={S.editableContent(s.accentColor, focused)}
      >
        {s.content}
      </div>

      <div style={S.sectionFooter}>
        <button style={S.btnSave} onClick={() => onSave(s.id, localValue)}>
          💾 Simpan
        </button>
      </div>
    </div>
  );
};

// ─── Finalize modal ───────────────────────────────────────────────────────────

const FinalizeModal: React.FC<{ onConfirm: () => void; onCancel: () => void }> = ({
  onConfirm, onCancel,
}) => (
  <div style={S.modalOverlay} onClick={onCancel}>
    <div style={S.modalBox} onClick={(e) => e.stopPropagation()}>
      <div style={S.modalIcon}>📄</div>
      <h3 style={S.modalTitle}>Finalisasi Laporan?</h3>
      <p style={S.modalBody}>
        Yakin ingin memfinalisasi dan mengirim laporan ini?<br />
        Tindakan ini tidak dapat dibatalkan.
      </p>
      <div style={S.modalActions}>
        <button onClick={onCancel} style={S.btnOutline}>Batal</button>
        <button onClick={onConfirm} style={S.btnPrimary}>Ya, Finalisasi</button>
      </div>
    </div>
  </div>
);

// ─── Placeholder saat reportData null ─────────────────────────────────────────

const EMPTY_DATA: ReportData = {
  id: "", murid_id: "", kelas_id: "", konten: "",
  tipe_laporan: "", status: "draft",
  pdf_path: null, tanggal: "", tanggal_dikirim: null,
  is_ai_generated: false, periode_mulai: "", periode_selesai: "",
};

// ─── Main ─────────────────────────────────────────────────────────────────────

const ReportEditor: React.FC<ReportEditorProps> = ({ reportData }) => {
  // Selalu ada data untuk info card — gunakan reportData jika tersedia
  const activeData: ReportData = reportData ?? EMPTY_DATA;

  const [sections, setSections] = useState<ReportSection[]>(() =>
    reportData ? parseKonten(reportData.konten) : INITIAL_SECTIONS
  );
  const [showModal, setShowModal] = useState(false);
  const [status, setStatus] = useState(reportData?.status ?? "draft");
  const [sending, setSending] = useState(false);

  const done = isSelesai(status);

  const handleChange = (id: string, value: string) => {
    setSections((prev) => prev.map((s) => (s.id === id ? { ...s, content: value } : s)));
  };

  const handleSave = () => {
    // TODO: call API to persist section
  };

  const handleFinalize = () => {
    setSending(true);
    setTimeout(() => {
      setSending(false);
      setStatus("selesai");
      setShowModal(false);
    }, 1500);
  };

  return (
    <>
      {showModal && (
        <FinalizeModal onConfirm={handleFinalize} onCancel={() => setShowModal(false)} />
      )}

      <div style={S.pageWrapper}>
        <div style={S.scrollArea} className="scroll-area">

          {/* ── Header ── */}
          <div style={S.pageHeader}>
            <h2 style={S.pageTitle}>Report Editor</h2>

            <div style={S.headerActions}>
              {/* Preview PDF + Download PDF + badge — hanya jika selesai */}
              {done && (
                <>
                  <button style={S.btnOutline}>👁 Preview PDF</button>
                  <button style={S.btnOutline}>⬇ Download PDF</button>
                  <span style={S.badgeSelesaiHeader}>✅ Laporan Selesai</span>
                </>
              )}

              {/* Finalisasi — hanya jika belum selesai */}
              {!done && (
                <button
                  disabled={sending}
                  onClick={() => setShowModal(true)}
                  style={sending ? S.btnPrimarySending : S.btnPrimary}
                >
                  {sending ? <><span style={S.spinner} /> Mengirim...</> : "Finalisasi"}
                </button>
              )}
            </div>
          </div>

          {/* ── Info card — selalu tampil menggunakan activeData ── */}
          <StudentInfoCard r={activeData} status={status} />

          {/* ── Banner ── */}
          {!done && (
            <div style={S.aiBanner}>
              ✦ Draft ini digenerate AI dari log belajar siswa. Edit konten lalu klik <strong>Simpan</strong> sebelum finalisasi.
            </div>
          )}
          {done && (
            <div style={S.finalizedBanner}>
              ✓ Laporan telah berhasil difinalisasi dan dikirim.
            </div>
          )}

          {/* ── Section cards ── */}
          <div style={S.sectionGrid}>
            {sections.map((s) => (
              <SectionCard
                key={s.id}
                section={s}
                onChange={handleChange}
                onSave={handleSave}
              />
            ))}
          </div>

        </div>
      </div>

      <style>{S.globalStyles}</style>
    </>
  );
};

export default ReportEditor;