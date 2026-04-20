import React from "react";
import type { GeneratedPlan, SubjectMeta } from "../types";

interface Props {
  plan: GeneratedPlan;
  subject: SubjectMeta;
  onClose: () => void;
}

const overlay: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.45)",
  zIndex: 50,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "20px",
};

const modal: React.CSSProperties = {
  background: "#fff",
  borderRadius: 16,
  boxShadow: "0 8px 40px rgba(0,0,0,0.18)",
  width: "100%",
  maxWidth: 600,
  maxHeight: "85vh",
  overflowY: "auto",
  display: "flex",
  flexDirection: "column",
};

export const PlanDetailData: React.FC<Props> = ({ plan, subject, onClose }) => {
  return (
    <div style={overlay} onClick={onClose}>
      <div style={modal} onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div
          style={{
            padding: "22px 26px 18px",
            borderBottom: "1px solid #f3f4f6",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 12,
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
              <div
                style={{
                  width: 36, height: 36, borderRadius: 10,
                  background: subject.bgColor,
                  border: `1.5px solid ${subject.borderColor}33`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 18,
                }}
              >
                {subject.icon}
              </div>
              <div>
                <h3 style={{ fontSize: 17, fontWeight: 800, color: "#111827", margin: 0 }}>
                  Rencana Belajar — {subject.name}
                </h3>
                <p style={{ fontSize: 11, color: "#9ca3af", margin: 0, marginTop: 2 }}>
                  Digenerate {new Date(plan.generatedAt).toLocaleString("id-ID", {
                    day: "numeric", month: "long", year: "numeric",
                    hour: "2-digit", minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "#f3f4f6", border: "none", borderRadius: 8,
              width: 32, height: 32, fontSize: 16, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "#6b7280", flexShrink: 0,
            }}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: "20px 26px 26px", display: "flex", flexDirection: "column", gap: 20 }}>

          {/* AI banner */}
          <div style={{
            background: "#eff6ff", border: "1.5px dashed #93c5fd",
            borderRadius: 10, padding: "12px 16px",
            fontSize: 13, color: "#1d4ed8", fontWeight: 500,
          }}>
            ✦ {plan.summary}
          </div>

          {/* Weekly goal */}
          <div style={{ background: "#FDFAF5", borderRadius: 10, border: "1px solid #EDE8DF", padding: "14px 18px" }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, color: "#9ca3af", textTransform: "uppercase", marginBottom: 6 }}>
              Target Minggu Ini
            </div>
            <div style={{ fontSize: 14, color: "#374151", fontWeight: 600, lineHeight: 1.5 }}>
              {plan.weeklyGoal}
            </div>
          </div>

          {/* Sessions */}
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#111827", marginBottom: 12 }}>
              Jadwal Sesi
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {plan.sessions.map((s, i) => (
                <div
                  key={i}
                  style={{
                    background: subject.bgColor,
                    borderLeft: `4px solid ${subject.borderColor}`,
                    borderRadius: 8, padding: "10px 14px",
                    display: "flex", gap: 14, alignItems: "flex-start",
                  }}
                >
                  <div style={{ minWidth: 80 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: subject.color }}>{s.day}</div>
                    <div style={{ fontSize: 11, color: "#9ca3af" }}>{s.duration}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#111827", marginBottom: 2 }}>{s.topic}</div>
                    <div style={{ fontSize: 12, color: "#6b7280", fontStyle: "italic" }}>{s.activity}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: "#111827", marginBottom: 10 }}>
              Tips Pengajar
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {plan.tips.map((tip, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex", gap: 10, alignItems: "flex-start",
                    fontSize: 13, color: "#374151", lineHeight: 1.5,
                  }}
                >
                  <span style={{ color: subject.color, fontWeight: 800, flexShrink: 0 }}>→</span>
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Footer */}
        <div style={{
          borderTop: "1px solid #f3f4f6", padding: "14px 26px",
          display: "flex", justifyContent: "flex-end",
        }}>
          <button
            onClick={onClose}
            style={{
              background: "#111827", color: "#fff", border: "none",
              borderRadius: 8, padding: "9px 22px",
              fontSize: 13, fontWeight: 700, cursor: "pointer",
            }}
          >
            Tutup
          </button>
        </div>

      </div>
    </div>
  );
};

export default PlanDetailData;