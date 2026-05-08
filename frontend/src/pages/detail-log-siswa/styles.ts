import type { CSSProperties } from "react";

export const styles: Record<string, CSSProperties> = {
  // ── Layout ──
  pageWrapper: {
    display: "flex",
    flexDirection: "column",
    height: "100%",
    gap: 0,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 20,
    flexShrink: 0,
    flexWrap: "wrap",
    gap: 12,
  },
  scrollBody: {
    flex: 1,
    minHeight: 0,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 18,
  },

  // ── Breadcrumb ──
  breadcrumbRow: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    marginBottom: 6,
  },
  breadcrumbLink: {
    fontSize: 13,
    color: "#9ca3af",
    cursor: "pointer",
  },
  breadcrumbSeparator: {
    fontSize: 13,
    color: "#d1d5db",
  },
  breadcrumbCurrent: {
    fontSize: 13,
    color: "#111827",
    fontWeight: 600,
  },

  // ── Siswa info ──
  siswaInfoRow: {
    display: "flex",
    alignItems: "center",
    gap: 14,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: "50%",
    background: "#eff6ff",
    color: "#3b82f6",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 16,
    fontWeight: 700,
    flexShrink: 0,
  },
  siswaName: {
    fontSize: 22,
    fontWeight: 700,
    color: "#111827",
    margin: "0 0 2px",
  },
  siswaMeta: {
    color: "#9ca3af",
    fontSize: 13,
    margin: 0,
  },

  // ── Header buttons ──
  headerBtnGroup: {
    display: "flex",
    gap: 10,
  },
  btnBack: {
    background: "none",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "8px 16px",
    fontSize: 13,
    fontWeight: 500,
    color: "#374151",
    cursor: "pointer",
  },

  // ── Stat cards ──
  statCardRow: {
    display: "flex",
    gap: 12,
    flexWrap: "wrap",
    flexShrink: 0,
  },

  // ── Table card ──
  tableCard: {
    background: "#fff",
    borderRadius: 14,
    padding: "24px 28px",
    boxShadow: "0 1px 4px rgba(0,0,0,.06)",
    flex: 1,
    minHeight: 0,
    display: "flex",
    flexDirection: "column",
  },
  tabRow: {
    display: "flex",
    gap: 6,
    flexWrap: "wrap",
    marginBottom: 20,
    flexShrink: 0,
  },
  tableWrapper: {
    flex: 1,
    overflowY: "auto",
    minHeight: 0,
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: 13,
  },
  tableHeadRow: {
    background: "rgba(228,230,239,0.85)",
  },
  tableBodyRow: {
    borderBottom: "1px solid #f3f4f6",
  },
  tdDefault: {
    padding: "12px 14px",
    color: "#6b7280",
  },
  tdNoWrap: {
    padding: "12px 14px",
    color: "#6b7280",
    whiteSpace: "nowrap",
  },
  tdBold: {
    padding: "12px 14px",
    fontWeight: 500,
    color: "#111827",
  },
  tdBadge: {
    padding: "12px 14px",
  },
  tdNote: {
    padding: "12px 14px",
    color: "#6b7280",
    maxWidth: 200,
  },
  noteClamp: {
    display: "-webkit-box",
    WebkitLineClamp: 2,
    WebkitBoxOrient: "vertical",
    overflow: "hidden",
  },
  tdActions: {
    padding: "12px 14px",
  },
  btnEdit: {
    background: "#f59e0b",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "5px 12px",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
  },
  emptyCell: {
    padding: "40px 14px",
    textAlign: "center",
    color: "#9ca3af",
    fontSize: 13,
  },

  // ── Toast container ──
  toastContainer: {
    position: "fixed",
    bottom: "24px",
    right: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    zIndex: 2000,
  },
  toastCloseBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    opacity: 0.6,
    fontSize: "14px",
    padding: "0 2px",
  },

  // ── Danger button ──
  btnDanger: {
    background: "#FEF2F2",
    color: "#E53E3E",
    border: "1.5px solid #FED7D7",
    borderRadius: "8px",
    padding: "7px 12px",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: "5px",
  },

  // ── Modal ──
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(15,22,36,0.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    backdropFilter: "blur(2px)",
  },
  modal: {
    background: "#fff",
    borderRadius: "18px",
    padding: "32px",
    width: "100%",
    maxWidth: "480px",
    boxShadow: "0 20px 60px rgba(15,22,36,0.2)",
    position: "relative",
  },
  modalTitle: {
    fontSize: "18px",
    fontWeight: 700,
    color: "#1E2A3B",
    marginBottom: "4px",
  },
  modalSubtitle: {
    fontSize: "13px",
    color: "#8A9BB0",
    marginBottom: "24px",
  },
  formGroup: {
    marginBottom: "18px",
  },
  label: {
    display: "block",
    fontSize: "12px",
    fontWeight: 700,
    color: "#4A5568",
    marginBottom: "6px",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  input: {
    width: "100%",
    padding: "10px 14px",
    border: "1.5px solid #E2E8F0",
    borderRadius: "10px",
    fontSize: "14px",
    color: "#1E2A3B",
    outline: "none",
    boxSizing: "border-box",
    transition: "border-color 0.15s",
    background: "#FAFBFF",
  },
  select: {
    width: "100%",
    padding: "10px 14px",
    border: "1.5px solid #E2E8F0",
    borderRadius: "10px",
    fontSize: "14px",
    color: "#1E2A3B",
    outline: "none",
    boxSizing: "border-box",
    background: "#FAFBFF",
    appearance: "none",
  },
  row2: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "14px",
  },
  modalFooter: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px",
    marginTop: "28px",
  },
  btnCancel: {
    background: "#F4F6FB",
    color: "#6B7FA3",
    border: "none",
    borderRadius: "10px",
    padding: "10px 20px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
  },
  btnSave: {
    background: "linear-gradient(135deg, #5B6BDF 0%, #4A5AC8 100%)",
    color: "#fff",
    border: "none",
    borderRadius: "10px",
    padding: "10px 24px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
    boxShadow: "0 2px 8px rgba(91,107,223,0.3)",
  },
  closeBtn: {
    position: "absolute",
    top: "18px",
    right: "18px",
    background: "#F4F6FB",
    border: "none",
    borderRadius: "8px",
    padding: "6px",
    cursor: "pointer",
    display: "flex",
    color: "#6B7FA3",
  },
};

// Stat card style is data-driven, so we keep a factory function here
export function statCardStyle(bg: string): CSSProperties {
  return {
    background: bg,
    borderRadius: 12,
    padding: "14px 20px",
    minWidth: 90,
    flex: "1 1 90px",
  };
}

// Tab button style factory
export function tabBtnStyle(active: boolean, badgeBg?: string, badgeColor?: string): CSSProperties {
  return {
    border: active ? "none" : "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "6px 14px",
    fontSize: 12,
    fontWeight: 600,
    cursor: "pointer",
    background: active ? (badgeBg ?? "#eff6ff") : "#fff",
    color: active ? (badgeColor ?? "#3b82f6") : "#6b7280",
    transition: "all .15s",
  };
}

// Table th style
export function thStyle(width: number | string): CSSProperties {
  return {
    padding: "10px 14px",
    textAlign: "left",
    fontWeight: 600,
    color: "#374151",
    width,
    whiteSpace: "nowrap",
  };
}

// Toast item style factory
export function toastItemStyle(type: "success" | "error"): CSSProperties {
  return {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    background: type === "success" ? "#F0FDF4" : "#FFF1F2",
    border: `1.5px solid ${type === "success" ? "#4ADE80" : "#FDA4AF"}`,
    color: type === "success" ? "#15803D" : "#9F1239",
    borderRadius: "10px",
    padding: "12px 16px",
    fontSize: "13px",
    fontWeight: 600,
    boxShadow: "0 4px 16px rgba(0,0,0,0.10)",
    minWidth: "260px",
    maxWidth: "360px",
    animation: "slideIn 0.2s ease",
  };
}