import React, { useState } from "react";
import { STUDENTS, INITIAL_SECTIONS, SUBJECT_STATS } from "./constants";
import type { ReportSection, SubjectStat } from "./types";

// ─── Shared styles ────────────────────────────────────────────────────────────

const card: React.CSSProperties = {
  background: "#fff",
  borderRadius: 14,
  boxShadow: "0 1px 4px rgba(0,0,0,.06)",
};

// ─── Editable section card ────────────────────────────────────────────────────

interface SectionCardProps {
  section: ReportSection;
  onChange: (id: string, value: string) => void;
}

const SectionCard: React.FC<SectionCardProps> = ({ section: s, onChange }) => {
  const [focused, setFocused] = useState(false);

  return (
    <div
      style={{
        ...card,
        borderLeft: `4px solid ${s.accentColor}`,
        padding: "22px 24px",
        flex: "1 1 340px",
        minWidth: 0,
        transition: "box-shadow .15s",
        boxShadow: focused ? `0 0 0 2px ${s.accentColor}33, 0 2px 8px rgba(0,0,0,.08)` : "0 1px 4px rgba(0,0,0,.06)",
      }}
    >
      {/* Section label */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
        <span style={{ fontSize: 18 }}>{s.emoji}</span>
        <span
          style={{
            fontSize: 10,
            fontWeight: 800,
            letterSpacing: 1.2,
            textTransform: "uppercase",
            color: s.accentColor,
          }}
        >
          {s.label}
        </span>
      </div>

      {/* Editable content */}
      <div
        contentEditable
        suppressContentEditableWarning
        onFocus={() => setFocused(true)}
        onBlur={(e) => {
          setFocused(false);
          onChange(s.id, e.currentTarget.innerText);
        }}
        style={{
          fontSize: 13,
          lineHeight: 1.75,
          color: "#374151",
          outline: "none",
          cursor: "text",
          borderRadius: 6,
          padding: focused ? "6px 8px" : "0",
          background: focused ? `${s.accentColor}0d` : "transparent",
          transition: "all .15s",
          minHeight: 60,
        }}
      >
        {s.content}
      </div>

      {/* Edit hint */}
      {focused && (
        <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 8 }}>
          ✏️ Klik di luar untuk menyimpan perubahan
        </div>
      )}
    </div>
  );
};

// ─── Subject stat row ─────────────────────────────────────────────────────────

const SubjectRow: React.FC<{ stat: SubjectStat }> = ({ stat: s }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 0, marginBottom: 16 }}>
    <div style={{ flex: "0 0 38%", fontSize: 13, color: "#374151", fontWeight: 500 }}>{s.name}</div>
    <div style={{ flex: "0 0 15%", textAlign: "center", fontSize: 13, color: "#6b7280" }}>{s.sessions}</div>
    <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, background: s.bgColor, borderRadius: 99, height: 6 }}>
        <div
          style={{
            width: `${s.progress}%`,
            background: s.color,
            borderRadius: 99,
            height: "100%",
            transition: "width .4s",
          }}
        />
      </div>
      <span style={{ fontSize: 12, fontWeight: 700, color: s.color, minWidth: 32, textAlign: "right" }}>
        {s.progress}%
      </span>
    </div>
  </div>
);

// ─── Finalize modal ───────────────────────────────────────────────────────────

const FinalizeModal: React.FC<{ onConfirm: () => void; onCancel: () => void }> = ({ onConfirm, onCancel }) => (
  <div
    style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
      zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center",
    }}
    onClick={onCancel}
  >
    <div
      style={{ ...card, padding: "28px 32px", maxWidth: 400, width: "90%", textAlign: "center" }}
      onClick={(e) => e.stopPropagation()}
    >
      <div style={{ fontSize: 32, marginBottom: 12 }}>📄</div>
      <h3 style={{ fontSize: 17, fontWeight: 700, color: "#111827", margin: "0 0 8px" }}>
        Finalisasi Laporan?
      </h3>
      <p style={{ fontSize: 13, color: "#6b7280", margin: "0 0 24px", lineHeight: 1.6 }}>
        Yakin ingin memfinalisasi dan mengirim laporan ini? Tindakan ini tidak dapat dibatalkan.
      </p>
      <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
        <button
          onClick={onCancel}
          style={{ border: "1px solid #e5e7eb", background: "#fff", borderRadius: 8, padding: "9px 20px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}
        >
          Batal
        </button>
        <button
          onClick={onConfirm}
          style={{ background: "#111827", color: "#fff", border: "none", borderRadius: 8, padding: "9px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}
        >
          Ya, Finalisasi
        </button>
      </div>
    </div>
  </div>
);

// ─── Main page ────────────────────────────────────────────────────────────────

const ReportEditor: React.FC = () => {
  const [student,    setStudent]    = useState(STUDENTS[0]);
  const [sections,   setSections]   = useState<ReportSection[]>(INITIAL_SECTIONS);
  const [showModal,  setShowModal]  = useState(false);
  const [finalized,  setFinalized]  = useState(false);
  const [sending,    setSending]    = useState(false);

  const handleChange = (id: string, value: string) => {
    setSections((prev) => prev.map((s) => (s.id === id ? { ...s, content: value } : s)));
  };

  const handleFinalize = () => {
    setSending(true);
    setTimeout(() => {
      setSending(false);
      setFinalized(true);
      setShowModal(false);
    }, 1500);
  };

  // Split into left (5 editable) and right (stats)
  const editableSections = sections; // all 5

  return (
    <>
      {showModal && (
        <FinalizeModal onConfirm={handleFinalize} onCancel={() => setShowModal(false)} />
      )}

      <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>
        <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>

          {/* ── Page header ── */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12, flexShrink: 0 }}>
            <div>
              <h2 style={{ fontSize: 26, fontWeight: 800, color: "#111827", margin: "0 0 4px" }}>Report Editor</h2>
              <p style={{ fontSize: 13, color: "#9ca3af", margin: 0 }}>
                Draft laporan &middot; {student} &middot; Februari – Maret 2025
              </p>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              {/* Student selector */}
              <div style={{ position: "relative" }}>
                <select
                  value={student}
                  onChange={(e) => setStudent(e.target.value)}
                  style={{
                    padding: "9px 36px 9px 14px",
                    border: "1px solid #e5e7eb",
                    borderRadius: 8,
                    fontSize: 13,
                    fontWeight: 600,
                    color: "#374151",
                    background: "#fff",
                    appearance: "none",
                    cursor: "pointer",
                    fontFamily: "inherit",
                    outline: "none",
                    minWidth: 150,
                  }}
                >
                  {STUDENTS.map((s) => <option key={s}>{s}</option>)}
                </select>
                <span style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", color: "#6b7280", fontSize: 12 }}>▾</span>
              </div>

              {/* Preview PDF */}
              <button
                style={{
                  border: "1px solid #e5e7eb",
                  background: "#fff",
                  borderRadius: 8,
                  padding: "9px 18px",
                  fontSize: 13,
                  fontWeight: 600,
                  color: "#374151",
                  cursor: "pointer",
                }}
              >
                Preview PDF
              </button>

              {/* Finalisasi */}
              <button
                disabled={finalized || sending}
                onClick={() => setShowModal(true)}
                style={{
                  background: finalized ? "#22c55e" : "#111827",
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  padding: "9px 20px",
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: finalized || sending ? "not-allowed" : "pointer",
                  opacity: sending ? 0.7 : 1,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  transition: "background .3s",
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

          {/* ── AI notice banner ── */}
          <div
            style={{
              background: "#fffbeb",
              border: "1.5px dashed #f59e0b",
              borderRadius: 10,
              padding: "14px 18px",
              fontSize: 13,
              color: "#b45309",
              fontWeight: 600,
              flexShrink: 0,
            }}
          >
            ✦ Draft ini digenerate AI dari 24 log belajar. Klik teks berwarna untuk mengedit sebelum finalisasi.
          </div>

          {/* ── Finalized banner ── */}
          {finalized && (
            <div style={{ background: "#f0fdf4", border: "1.5px solid #bbf7d0", borderRadius: 10, padding: "12px 18px", fontSize: 13, color: "#15803d", fontWeight: 600, flexShrink: 0 }}>
              ✓ Laporan telah berhasil difinalisasi dan dikirim.
            </div>
          )}

          {/* ── Main report grid ── */}
          <div style={{ display: "flex", gap: 18, flexWrap: "wrap", alignItems: "flex-start", flexShrink: 0 }}>

            {/* Left: 5 editable section cards in 2-col grid */}
            <div style={{ flex: "3 1 500px", minWidth: 0, display: "flex", flexWrap: "wrap", gap: 18, alignContent: "flex-start" }}>
              {editableSections.map((s) => (
                <SectionCard key={s.id} section={s} onChange={handleChange} />
              ))}
            </div>

            {/* Right: Ringkasan Statistik */}
            <div style={{ ...card, flex: "1 1 280px", minWidth: 0, padding: "22px 24px" }}>
              <h5 style={{ fontSize: 15, fontWeight: 700, color: "#111827", margin: "0 0 18px" }}>
                Ringkasan Statistik
              </h5>

              {/* Table header */}
              <div style={{ display: "flex", marginBottom: 12, paddingBottom: 10, borderBottom: "1px solid #f3f4f6" }}>
                <span style={{ flex: "0 0 38%", fontSize: 10, fontWeight: 700, color: "#9ca3af", letterSpacing: 1, textTransform: "uppercase" }}>Mapel</span>
                <span style={{ flex: "0 0 15%", fontSize: 10, fontWeight: 700, color: "#9ca3af", letterSpacing: 1, textTransform: "uppercase", textAlign: "center" }}>Sesi</span>
                <span style={{ flex: 1, fontSize: 10, fontWeight: 700, color: "#9ca3af", letterSpacing: 1, textTransform: "uppercase", textAlign: "center" }}>Progres</span>
              </div>

              {/* Rows */}
              {SUBJECT_STATS.map((s) => <SubjectRow key={s.name} stat={s} />)}

              {/* Divider */}
              <div style={{ borderTop: "1px dashed #e5e7eb", margin: "16px 0" }} />

              {/* Total */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#111827" }}>Total: 24 sesi</div>
                  <div style={{ fontSize: 12, color: "#9ca3af" }}>48 jam pembelajaran</div>
                </div>
                <span style={{ background: "#dcfce7", color: "#15803d", borderRadius: 8, padding: "5px 14px", fontSize: 12, fontWeight: 700 }}>
                  On Track
                </span>
              </div>
            </div>

          </div>

        </div>
      </div>

      {/* Spinner animation */}
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </>
  );
};

export default ReportEditor;