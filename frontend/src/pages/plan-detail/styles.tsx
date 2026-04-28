import type { CSSProperties } from "react";

export const styles: Record<string, CSSProperties> = {

  // ── Layout ──────────────────────────────────────────────────────────────
  root: {
    display: "flex",
    flexDirection: "column",
    gap: 20,
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
  },

  // ── Header ──────────────────────────────────────────────────────────────
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    flexWrap: "wrap",
    gap: 12,
  },

  pageSubtitle: {
    fontSize: 13,
    color: "#9CA3AF",
    margin: 0,
  },

  backBtn: {
    background: "none",
    border: "1px solid #E5E7EB",
    borderRadius: 8,
    padding: "8px 16px",
    fontSize: 13,
    fontWeight: 500,
    color: "#374151",
    cursor: "pointer",
  },

  // ── Info Cards Grid ──────────────────────────────────────────────────────
  infoGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: 12,
  },

  infoCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 12,
    padding: "14px 18px",
    display: "flex",
    flexDirection: "column",
    gap: 4,
    boxShadow: "0 1px 3px rgba(0,0,0,.04)",
  },

  infoLabel: {
    fontSize: 11,
    fontWeight: 700,
    color: "#94A3B8",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },

  infoValue: {
    fontSize: 14,
    fontWeight: 700,
    color: "#0F172A",
  },

  outdatedBadge: {
    fontSize: 10,
    background: "#FEF3C7",
    color: "#D97706",
    borderRadius: 99,
    padding: "2px 8px",
    fontWeight: 600,
  },

  infoValueRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
  },

  // ── Catatan Analisa ──────────────────────────────────────────────────────
  catatanBox: {
    background: "#F0F9FF",
    border: "1px solid #BAE6FD",
    borderRadius: 12,
    padding: "12px 16px",
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
  },

  catatanLabel: {
    fontSize: 11,
    fontWeight: 700,
    color: "#0284C7",
    display: "block",
    marginBottom: 3,
    letterSpacing: "0.04em",
  },

  catatanText: {
    fontSize: 13,
    color: "#0369A1",
    lineHeight: 1.5,
  },

  // ── Rekomendasi Materi ───────────────────────────────────────────────────
  rekomendasiBox: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: 14,
    padding: "16px 20px",
    boxShadow: "0 1px 4px rgba(0,0,0,.05)",
  },

  rekomendasiTitle: {
    fontSize: 11,
    fontWeight: 700,
    color: "#64748B",
    margin: "0 0 12px",
    letterSpacing: "0.05em",
  },

  rekomendasiPills: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
  },

  // ── Jadwal Mingguan ──────────────────────────────────────────────────────
  jadwalBox: {
    background: "#fff",
    borderRadius: 14,
    boxShadow: "0 1px 4px rgba(0,0,0,.06)",
    border: "1px solid #E5E7EB",
    padding: "20px 24px",
  },

  jadwalTitle: {
    fontSize: 15,
    fontWeight: 700,
    color: "#111827",
    margin: "0 0 20px",
  },

  jadwalGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
    gap: 16,
    alignItems: "start",
  },

  // ── Minggu Column ────────────────────────────────────────────────────────
  mingguColumn: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 10,
  },

  mingguLabel: {
    fontSize: 13,
    fontWeight: 800,
    color: "#16A34A",
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    textAlign: "center",
  },

  mingguCard: {
    width: "100%",
    background: "#fff",
    border: "1.5px solid #86EFAC",
    borderRadius: 12,
    padding: "14px",
    boxShadow: "0 1px 4px rgba(0,0,0,.04)",
    display: "flex",
    flexDirection: "column",
    gap: 0,
    boxSizing: "border-box",
  },

  topikRow: {
    fontSize: 13,
    fontWeight: 500,
    color: "#1E293B",
    padding: "6px 0",
    borderBottom: "1px solid #F1F5F9",
  },

  topikRowLast: {
    fontSize: 13,
    fontWeight: 500,
    color: "#1E293B",
    padding: "6px 0",
  },

  emptyState: {
    textAlign: "center",
    padding: "40px 0",
    color: "#CBD5E1",
    fontSize: 13,
  },

  emptyTopik: {
    fontSize: 12,
    color: "#CBD5E1",
    padding: "6px 0",
  },
};

// Topik pill colors — cycling
export const topikColors = [
  { bg: "#EEF2FF", color: "#4338CA", border: "#C7D2FE" },
  { bg: "#FDF4FF", color: "#9333EA", border: "#E9D5FF" },
  { bg: "#FFF7ED", color: "#EA580C", border: "#FED7AA" },
  { bg: "#F0FDF4", color: "#16A34A", border: "#BBF7D0" },
  { bg: "#FFF1F2", color: "#E11D48", border: "#FECDD3" },
  { bg: "#F0F9FF", color: "#0284C7", border: "#BAE6FD" },
];