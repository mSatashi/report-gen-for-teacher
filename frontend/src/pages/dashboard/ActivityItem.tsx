import React from "react";
import type { AktivitasTerbaruResponse } from "../../service/payload";

interface ActivityItemProps {
  activity: AktivitasTerbaruResponse;
}

const ActivityItem: React.FC<ActivityItemProps> = ({ activity: a }) => (
  <div style={{ display: "flex", gap: 14, marginBottom: 20 }}>
    {/* Date + timeline dot */}
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        minWidth: 56,
      }}
    >
      <span style={{ fontSize: 11, fontWeight: 600, color: "#9ca3af", whiteSpace: "nowrap" }}>
        {a.tanggal}
      </span>
      <div
        style={{
          width: 10,
          height: 10,
          borderRadius: "50%",
          background: "#22c55e",
          margin: "4px 0",
          flexShrink: 0,
        }}
      />
      <div style={{ flex: 1, width: 2, background: "#e5e7eb" }} />
    </div>

    {/* Content */}
    <div>
      <div style={{ fontWeight: 600, fontSize: 14, color: "#111827" }}>{a.nama_mata_pelajaran}</div>
      <div style={{ fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>{a.topik}</div>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {/* {a.tags.map((t) => (
          <span
            key={t.label}
            style={{
              background: t.color,
              color: "#374151",
              borderRadius: 6,
              padding: "2px 8px",
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            {t.label}
          </span>
        ))} */}
      </div>
    </div>
  </div>
);

export default ActivityItem;