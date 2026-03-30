import React from "react";
import type { Student } from "../types";

interface ProgressBarProps {
  pct: number;
  color: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ pct, color }) => (
  <div style={{ background: "#e5e7eb", borderRadius: 99, height: 6, width: "100%" }}>
    <div
      style={{
        width: `${pct}%`,
        background: color,
        borderRadius: 99,
        height: "100%",
        transition: "width .5s",
      }}
    />
  </div>
);

interface StudentRowProps {
  student: Student;
}

const StudentRow: React.FC<StudentRowProps> = ({ student: s }) => {
  const isWarning = s.status === "Perlu Perhatian";
  const barColor   = isWarning ? "#f59e0b" : "#22c55e";
  const badgeBg    = isWarning ? "#fef3c7" : "#dcfce7";
  const badgeText  = isWarning ? "#b45309" : "#15803d";

  const initials = s.name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2);

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "14px 0",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      {/* Avatar */}
      <div
        style={{
          width: 38,
          height: 38,
          borderRadius: 8,
          background: s.avatarColor,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 13,
          fontWeight: 700,
          color: "#374151",
          flexShrink: 0,
        }}
      >
        {initials}
      </div>

      {/* Info + progress */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 14, color: "#111827" }}>{s.name}</div>
        <div style={{ fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
          {s.subject} · {s.subtopic}
        </div>
        <ProgressBar pct={s.progress} color={barColor} />
        <div style={{ fontSize: 11, color: isWarning ? "#f59e0b" : "#9ca3af", marginTop: 4 }}>
          {s.note}
        </div>
      </div>

      {/* Status badge */}
      <span
        style={{
          background: badgeBg,
          color: badgeText,
          borderRadius: 8,
          padding: "4px 10px",
          fontSize: 12,
          fontWeight: 600,
          flexShrink: 0,
          whiteSpace: "nowrap",
        }}
      >
        {s.status}
      </span>
    </div>
  );
};

export default StudentRow;