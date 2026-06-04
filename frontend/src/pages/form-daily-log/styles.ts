import type { CSSProperties } from "react";
import { cardStyle, inputStyle } from "../daily-log/components/constants";
import { colors } from "../../components/colorstyle";

export const styles: Record<string, CSSProperties> = {
  lockedFieldStyle: { 
    ...inputStyle,
    background: colors.offWhite,
    color: colors.slateGray,
    cursor: "not-allowed",
    border: "1px solid " + colors.flashWhite, 
  },

  btnSimpanLog: {
    background: colors.green, 
    color: colors.white, 
    border: "none",
    borderRadius: 8,
    fontSize: 13, 
    fontWeight: 700, 
    cursor: "pointer",
  },
  label: { 
    fontSize: 13, 
    fontWeight: 600, 
    color: colors.darkSlateGray, 
    marginBottom: 6 
  },
  optional: { 
    fontWeight: 400, 
    color: colors.coolGrey, 
    marginLeft: 4
  },

  ctnMain: { 
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
  tagP: { 
    color: colors.coolGrey, 
    fontSize: 13, 
    margin: 0 
  },
  buttonRightWrapper: { 
    display: "flex", 
    gap: 10, 
    alignItems: "center" 
  },
  btnKembali: {
    background: "none", 
    border: "1px solid #e5e7eb", 
    borderRadius: 8,
    padding: "8px 16px", 
    fontSize: 13, 
    fontWeight: 500, 
    color: "#374151", 
    cursor: "pointer",
  },

  ctnScroll: { 
    flex: 1, 
    minHeight: 200, 
    overflowY: "auto", 
    display: "flex", 
    flexDirection: "column", 
    gap: 18 
  },

  row: {
    display: "flex", 
    gap: 18, 
    flexWrap: "wrap", 
    alignItems: "flex-start"
  },

  cardStyle: { 
    ...cardStyle, 
    flex: "1 1 340px", 
    minWidth: 0 
  },

  filedInitialStyle: {
    width: 28, 
    height: 28, 
    borderRadius: "50%",
    background: colors.aliceBlue, 
    color: colors.cyan,
    display: "flex", 
    alignItems: "center", 
    justifyContent: "center",
    fontSize: 11, 
    fontWeight: 700, 
    flexShrink: 0,
  },
  cardContent: { 
    display: "grid", 
    gridTemplateColumns: "1fr 1fr", 
    gap: 16 
  },
  cardInitialWrapper: { 
    display: "flex", 
    alignItems: "center", 
    gap: 8 
  },
  inputWrapper: { 
    display: "flex", 
    alignItems: "center", 
    gap: 8 
  },
  inputTingkatPemahamanWrapper: { 
    display: "flex", 
    gap: 8, 
    flexWrap: "wrap", 
    marginBottom: 18 
  },

  // ── Capaian & Kompetensi card ──
  capaianCard: {
    flexShrink: 0,
  },
  capaianHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },
  capaianTitle: {
    fontSize: 15,
    fontWeight: 700,
    color: "#111827",
    margin: 0,
  },
  capaianBadge: {
    fontSize: 12,
    color: "#3b82f6",
    fontWeight: 600,
    background: "#eff6ff",
    borderRadius: 6,
    padding: "4px 10px",
  },
  capaianGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 16,
  },

  // ── Bottom action bar ──
  bottomBar: {
    display: "flex",
    justifyContent: "flex-end",
    gap: 10,
    padding: "4px 0 8px",
    flexShrink: 0,
  },
  btnBatal: {
    background: "none",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "9px 20px",
    fontSize: 13,
    fontWeight: 500,
    color: "#374151",
    cursor: "pointer",
  },

  // ── Toast ──
  toastContainer: {
    position: "fixed" as const,
    bottom: "24px",
    right: "24px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
    zIndex: 2000,
  },
  toastCloseBtn: {
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "inherit",
    opacity: 0.6,
    fontSize: "14px",
    padding: "0 2px",
  },
};
// Toggle button (Pemahaman & Keterlibatan) — warna bergantung state active
export function toggleBtnStyle(active: boolean, activeBg: string): import("react").CSSProperties {
  return {
    border: active ? "none" : "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "7px 14px",
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
    background: active ? activeBg : "#fff",
    color: active ? "#fff" : "#374151",
    transition: "all .15s",
  };
}

// Toast item — warna bergantung type
export function toastItemStyle(type: "success" | "error"): import("react").CSSProperties {
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