import React, { useState } from "react";
import { STUDENTS, STAT_ITEMS, SCHEDULE, SUBJECTS } from "./constants";
import type { Session, SubjectDetail, StatItem } from "./types";

// ─── Shared styles ────────────────────────────────────────────────────────────

const card: React.CSSProperties = {
  background: "#fff",
  borderRadius: 14,
  boxShadow: "0 1px 4px rgba(0,0,0,.06)",
};

// ─── Stat card ────────────────────────────────────────────────────────────────

const StatCard: React.FC<{ item: StatItem }> = ({ item: s }) => (
  <div
    style={{
      ...card,
      background: "#FDFAF5",
      border: s.accentColor
        ? `1px solid ${s.accentColor}40`
        : "1px solid #EDE8DF",
      borderLeft: s.accentColor ? `4px solid ${s.accentColor}` : "1px solid #EDE8DF",
      flex: "1 1 180px",
      minWidth: 0,
      padding: "20px 24px 22px",
    }}
  >
    <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, color: "#9ca3af", textTransform: "uppercase", marginBottom: 12 }}>
      {s.label}
    </div>
    <div style={{ fontSize: 42, fontWeight: 800, color: "#111827", lineHeight: 1, marginBottom: 6 }}>
      {s.value}
    </div>
    <div style={{ fontSize: 13, color: "#9ca3af", fontWeight: 500 }}>{s.sub}</div>
  </div>
);

// ─── Session card ─────────────────────────────────────────────────────────────

const SessionCard: React.FC<{ session: Session }> = ({ session: s }) => (
  <div
    style={{
      background: s.color,
      borderLeft: `4px solid ${s.borderColor}`,
      borderRadius: 8,
      padding: "10px 12px",
      cursor: "pointer",
    }}
  >
    <span style={{ fontSize: 11, color: "#6b7280", fontWeight: 600, display: "block", marginBottom: 3 }}>
      {s.time}
    </span>
    <span style={{ fontSize: 13, fontWeight: 700, color: "#111827", display: "block", marginBottom: 2 }}>
      {s.subject}
    </span>
    <span style={{ fontSize: 11, color: "#6b7280", fontStyle: "italic" }}>
      {s.note}
    </span>
  </div>
);

// ─── Subject detail card ──────────────────────────────────────────────────────

const SubjectCard: React.FC<{ subject: SubjectDetail }> = ({ subject: s }) => {
  const pct = s.sessions > 0 ? Math.round((s.completed / s.sessions) * 100) : 0;
  const label = s.completed === 0
    ? "Belum dimulai"
    : `${s.completed} dari ${s.sessions} sesi selesai`;

  return (
    <div
      style={{
        ...card,
        flex: "1 1 220px",
        minWidth: 0,
        borderTop: `3px solid ${s.color}`,
        padding: "20px 22px",
      }}
    >
      <div style={{ fontSize: 15, fontWeight: 700, color: "#111827", marginBottom: 4 }}>{s.name}</div>
      <div style={{ fontSize: 12, color: "#9ca3af", marginBottom: 16 }}>
        {s.sessions} sesi &middot; {s.hours} jam
      </div>
      {/* Progress bar */}
      <div style={{ background: `${s.color}22`, borderRadius: 99, height: 6, marginBottom: 8 }}>
        <div style={{ width: `${pct}%`, background: s.color, borderRadius: 99, height: "100%", transition: "width .4s" }} />
      </div>
      <div style={{ fontSize: 12, color: "#9ca3af" }}>{label}</div>
    </div>
  );
};

// ─── Main page ────────────────────────────────────────────────────────────────

const LearningPlan: React.FC = () => {
  const [student, setStudent] = useState(STUDENTS[0]);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 0 }}>

      {/* ── Scrollable body ── */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>

        {/* Page header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12, flexShrink: 0 }}>
          <div>
            <h2 style={{ fontSize: 26, fontWeight: 800, color: "#111827", margin: "0 0 4px" }}>Learning Plan</h2>
            <p style={{ fontSize: 13, color: "#9ca3af", margin: 0 }}>
              Plan adaptif &middot; Di-generate AI &middot; Minggu 10 – 14 Maret 2025
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
            {/* Regenerate button */}
            <button
              style={{
                background: "#f59e0b", color: "#fff", border: "none",
                borderRadius: 8, padding: "9px 20px",
                fontSize: 13, fontWeight: 700, cursor: "pointer",
                display: "flex", alignItems: "center", gap: 6,
              }}
            >
              ✦ Regenerate Plan
            </button>
          </div>
        </div>

        {/* AI notice banner */}
        <div
          style={{
            background: "#eff6ff",
            border: "1.5px dashed #93c5fd",
            borderRadius: 10,
            padding: "14px 18px",
            fontSize: 13,
            color: "#1d4ed8",
            fontWeight: 500,
            flexShrink: 0,
          }}
        >
          ✦ Plan ini digenerate oleh AI berdasarkan log tanggal 9 Maret — fokus pada penguatan aljabar dasar karena ada gap pada operasi bilangan negatif.
        </div>

        {/* Stat cards */}
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", flexShrink: 0 }}>
          {STAT_ITEMS.map((s) => <StatCard key={s.label} item={s} />)}
        </div>

        {/* Jadwal Mingguan */}
        <div style={{ ...card, padding: "22px 24px", flexShrink: 0 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
            <h4 style={{ fontSize: 16, fontWeight: 700, color: "#111827", margin: 0 }}>Jadwal Mingguan</h4>
            <span style={{ fontSize: 12, color: "#9ca3af", background: "#f3f4f6", borderRadius: 6, padding: "4px 12px", fontWeight: 500 }}>
              Klik sesi untuk detail
            </span>
          </div>

          {/* Day header row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10, marginBottom: 12 }}>
            {SCHEDULE.map((day) => (
              <div
                key={day.label}
                style={{
                  background: "#f3f4f6", borderRadius: 8,
                  textAlign: "center", padding: "10px 4px",
                  fontSize: 12, fontWeight: 700, color: "#374151",
                }}
              >
                {day.label}
              </div>
            ))}
          </div>

          {/* Session grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
            {SCHEDULE.map((day) => (
              <div key={day.label} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {day.sessions.map((session, i) => (
                  <SessionCard key={i} session={session} />
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Detail Materi per Mata Pelajaran */}
        <div style={{ ...card, padding: "22px 24px", flexShrink: 0 }}>
          <h4 style={{ fontSize: 16, fontWeight: 700, color: "#111827", margin: "0 0 18px" }}>
            Detail Materi per Mata Pelajaran
          </h4>
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
            {SUBJECTS.map((s) => <SubjectCard key={s.name} subject={s} />)}
          </div>
        </div>

      </div>
    </div>
  );
};

export default LearningPlan;