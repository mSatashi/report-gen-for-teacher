import React from "react";
import type { ProgressDashboardResponse } from "../../service/payload";

interface ProgressBarProps {
  pct: number;
  color: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ pct, color }) => (
  <div style={{ background: "#e5e7eb", borderRadius: 99, height: 6, width: "100%" }}>
    <div
      style={{
        width: `${Math.min(pct, 100)}%`,
        background: color,
        borderRadius: 99,
        height: "100%",
        transition: "width .5s",
      }}
    />
  </div>
);

interface StudentRowProps {
  student: ProgressDashboardResponse;
}

const avatarColors = ["#dbeafe", "#dcfce7", "#fef9c3", "#fee2e2", "#ede9fe"];

const StudentRow: React.FC<StudentRowProps> = ({ student: s }) => {
  const isWarning = s.status === "Perlu Perhatian";
  const barColor  = isWarning ? "#f59e0b" : "#22c55e";
  const badgeBg   = isWarning ? "#fef3c7" : "#dcfce7";
  const badgeText = isWarning ? "#b45309" : "#15803d";

  const initials = s.nama
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  // Warna avatar berdasarkan karakter pertama nama
  const avatarBg = avatarColors[s.nama.charCodeAt(0) % avatarColors.length];

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
          background: avatarBg,
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
        <div style={{ fontWeight: 600, fontSize: 14, color: "#111827" }}>{s.nama}</div>
        <div style={{ fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
          {s.total_sesi} sesi · rata-rata {s.avg_nilai}
        </div>
        <ProgressBar pct={s.avg_nilai} color={barColor} />
        <div style={{ fontSize: 11, color: isWarning ? "#f59e0b" : "#9ca3af", marginTop: 4 }}>
          Nilai: {s.avg_nilai}
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