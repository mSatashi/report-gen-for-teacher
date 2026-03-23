import React from "react";
import type { StatCard } from "../../types";

const badgeColors: Record<string, { bg: string; text: string }> = {
  green:  { bg: "#dcfce7", text: "#16a34a" },
  blue:   { bg: "#dbeafe", text: "#1d4ed8" },
  yellow: { bg: "#fef9c3", text: "#ca8a04" },
  red:    { bg: "#fee2e2", text: "#dc2626" },
};

interface StatCardItemProps {
  card: StatCard;
}

const StatCardItem: React.FC<StatCardItemProps> = ({ card }) => {
  const bc = badgeColors[card.badge.color];

  return (
    <div
      style={{
        background: card.bg,
        borderRadius: 12,
        padding: "20px 22px",
        flex: "1 1 180px",
        minWidth: 0,
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <span style={{ fontSize: 13, color: "#6b7280", fontWeight: 500 }}>{card.label}</span>
        <span style={{ color: card.iconColor }}>{card.icon}</span>
      </div>

      <div style={{ fontSize: 36, fontWeight: 700, color: "#111827", lineHeight: 1 }}>
        {card.value}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span
          style={{
            background: bc.bg,
            color: bc.text,
            borderRadius: 6,
            padding: "2px 7px",
            fontSize: 12,
            fontWeight: 700,
          }}
        >
          {card.badge.count}
        </span>
        <span style={{ fontSize: 12, color: "#9ca3af" }}>{card.badge.text}</span>
      </div>
    </div>
  );
};

export default StatCardItem;