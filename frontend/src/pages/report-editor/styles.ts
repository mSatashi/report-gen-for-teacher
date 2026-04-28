import type React from "react";

// ─── Tokens ───────────────────────────────────────────────────────────────────

export const COLOR = {
  bg: "#F8F9FB",
  white: "#FFFFFF",
  border: "#E5E7EB",
  borderLight: "#F3F4F6",
  textPrimary: "#111827",
  textSecondary: "#374151",
  textMuted: "#6B7280",
  textFaint: "#9CA3AF",
  success: "#22C55E",
  successBg: "#F0FDF4",
  successBorder: "#BBF7D0",
  successText: "#15803D",
  warning: "#F59E0B",
  warningBg: "#FFFBEB",
  warningText: "#B45309",
  danger: "#E11D48",
  shadow: "rgba(0,0,0,.06)",
  shadowMd: "rgba(0,0,0,.10)",
};

export const RADIUS = { sm: 6, md: 8, lg: 12, xl: 14 };

// ─── Base card ────────────────────────────────────────────────────────────────

export const card: React.CSSProperties = {
  background: COLOR.white,
  borderRadius: RADIUS.xl,
  boxShadow: `0 1px 4px ${COLOR.shadow}`,
};

// ─── Layout ───────────────────────────────────────────────────────────────────

export const pageWrapper: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  height: "100%",
};

export const scrollArea: React.CSSProperties = {
  flex: 1,
  minHeight: 0,
  overflowY: "auto" as const,
  display: "flex",
  flexDirection: "column",
  gap: 18,
};

// ─── Page header ─────────────────────────────────────────────────────────────

export const pageHeader: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  flexWrap: "wrap",
  gap: 12,
  flexShrink: 0,
};

export const pageTitle: React.CSSProperties = {
  fontSize: 22,
  fontWeight: 800,
  color: COLOR.textPrimary,
  margin: 0,
};

export const headerActions: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
};

// ─── Buttons ──────────────────────────────────────────────────────────────────

export const btnOutline: React.CSSProperties = {
  border: `1px solid ${COLOR.border}`,
  background: COLOR.white,
  borderRadius: RADIUS.md,
  padding: "9px 16px",
  fontSize: 13,
  fontWeight: 600,
  color: COLOR.textSecondary,
  cursor: "pointer",
  fontFamily: "inherit",
  display: "flex",
  alignItems: "center",
  gap: 6,
};

export const btnPrimary: React.CSSProperties = {
  background: COLOR.textPrimary,
  color: COLOR.white,
  border: "none",
  borderRadius: RADIUS.md,
  padding: "9px 20px",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: 8,
  transition: "background .3s",
  fontFamily: "inherit",
};

export const btnPrimarySending: React.CSSProperties = {
  ...btnPrimary,
  opacity: 0.7,
  cursor: "not-allowed",
};

export const btnSave: React.CSSProperties = {
  background: "#EEF2FF",
  color: "#4338CA",
  border: "none",
  borderRadius: RADIUS.md,
  padding: "7px 18px",
  fontSize: 12,
  fontWeight: 700,
  cursor: "pointer",
  fontFamily: "inherit",
  display: "flex",
  alignItems: "center",
  gap: 5,
};

// ─── Banners ──────────────────────────────────────────────────────────────────

export const aiBanner: React.CSSProperties = {
  background: COLOR.warningBg,
  border: `1.5px dashed ${COLOR.warning}`,
  borderRadius: RADIUS.lg,
  padding: "12px 18px",
  fontSize: 13,
  color: COLOR.warningText,
  fontWeight: 600,
  flexShrink: 0,
};

export const finalizedBanner: React.CSSProperties = {
  background: COLOR.successBg,
  border: `1.5px solid ${COLOR.successBorder}`,
  borderRadius: RADIUS.lg,
  padding: "12px 18px",
  fontSize: 13,
  color: COLOR.successText,
  fontWeight: 600,
  flexShrink: 0,
};

// ─── Info card ────────────────────────────────────────────────────────────────

export const infoCard: React.CSSProperties = {
  ...card,
  padding: 0,
  flexShrink: 0,
  overflow: "hidden",
};

export const infoCardHeader: React.CSSProperties = {
  padding: "13px 20px",
  background: COLOR.textPrimary,
  display: "flex",
  alignItems: "center",
  gap: 10,
};

export const infoCardHeaderTitle: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 700,
  color: COLOR.white,
  letterSpacing: 0.3,
};

/** Badge status di ujung kanan header strip */
export const infoCardStatusBadge: React.CSSProperties = {
  marginLeft: "auto",
  display: "inline-flex",
  alignItems: "center",
  gap: 4,
  padding: "3px 10px",
  borderRadius: 20,
  fontSize: 11,
  fontWeight: 700,
  background: "rgba(255,255,255,0.15)",
  color: COLOR.white,
  letterSpacing: 0.3,
};

/**
 * Satu baris field dalam info card.
 * Menggunakan auto-fill sehingga field merata mengisi lebar card.
 */
export const infoCardBodyRow: React.CSSProperties = {
  padding: "14px 20px",
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
  gap: "10px 20px",
};

/** Garis tipis pemisah baris 1 dan baris 2 */
export const infoCardDivider: React.CSSProperties = {
  height: 1,
  background: COLOR.borderLight,
  margin: "0 20px",
};

export const infoGroup: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
};

export const infoLabel: React.CSSProperties = {
  fontSize: 10,
  fontWeight: 700,
  letterSpacing: 0.8,
  textTransform: "uppercase" as const,
  color: COLOR.textFaint,
};

export const infoValue: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 600,
  color: COLOR.textPrimary,
};

// ─── Info card badges ─────────────────────────────────────────────────────────

/** Badge ungu "✦ AI Generated" */
export const badgeAI: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 4,
  padding: "3px 10px",
  borderRadius: 20,
  fontSize: 11,
  fontWeight: 700,
  background: "#EDE9FE",
  color: "#6D28D9",
  width: "fit-content",
};

/** Badge status (Draft / Selesai) di baris 2 info card */
export const badgeStatus = (status: string): React.CSSProperties => {
  const done = ["selesai", "finalized", "sent"].includes(status);
  return {
    display: "inline-flex",
    alignItems: "center",
    gap: 4,
    padding: "3px 10px",
    borderRadius: 20,
    fontSize: 11,
    fontWeight: 700,
    background: status === "draft" ? "#FEF3C7" : done ? COLOR.successBg : "#F3F4F6",
    color: status === "draft" ? "#92400E" : done ? COLOR.successText : COLOR.textMuted,
    letterSpacing: 0.3,
    width: "fit-content",
  };
};

/** Badge "✅ Laporan Selesai" di header halaman (muncul setelah finalisasi) */
export const badgeSelesaiHeader: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "8px 14px",
  borderRadius: 20,
  fontSize: 13,
  fontWeight: 700,
  background: COLOR.successBg,
  color: COLOR.successText,
  border: `1px solid ${COLOR.successBorder}`,
};

// ─── Section card ─────────────────────────────────────────────────────────────

export const sectionGrid: React.CSSProperties = {
  display: "flex",
  gap: 18,
  flexWrap: "wrap",
  alignItems: "flex-start",
  flexShrink: 0,
};

export const sectionCard = (accentColor: string, focused: boolean): React.CSSProperties => ({
  ...card,
  borderLeft: `4px solid ${accentColor}`,
  padding: "20px 22px",
  flex: "1 1 340px",
  minWidth: 0,
  transition: "box-shadow .15s",
  boxShadow: focused
    ? `0 0 0 2px ${accentColor}33, 0 2px 10px ${COLOR.shadowMd}`
    : `0 1px 4px ${COLOR.shadow}`,
});

export const sectionLabelRow: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 12,
};

export const sectionEmoji: React.CSSProperties = { fontSize: 16 };

export const sectionLabel = (accentColor: string): React.CSSProperties => ({
  fontSize: 10,
  fontWeight: 800,
  letterSpacing: 1.2,
  textTransform: "uppercase" as const,
  color: accentColor,
});

export const editableContent = (accentColor: string, focused: boolean): React.CSSProperties => ({
  fontSize: 13,
  lineHeight: 1.75,
  color: COLOR.textSecondary,
  outline: "none",
  cursor: "text",
  borderRadius: RADIUS.sm,
  padding: focused ? "8px 10px" : "4px 0",
  background: focused ? `${accentColor}0d` : "transparent",
  border: focused ? `1px solid ${accentColor}44` : "1px solid transparent",
  transition: "all .15s",
  minHeight: 60,
  whiteSpace: "pre-wrap" as const,
});

export const sectionFooter: React.CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  alignItems: "center",
  marginTop: 14,
  paddingTop: 12,
  borderTop: `1px solid ${COLOR.borderLight}`,
};

// ─── Modal ────────────────────────────────────────────────────────────────────

export const modalOverlay: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.45)",
  zIndex: 100,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

export const modalBox: React.CSSProperties = {
  ...card,
  padding: "28px 32px",
  maxWidth: 400,
  width: "90%",
  textAlign: "center",
};

export const modalIcon: React.CSSProperties = { fontSize: 32, marginBottom: 12 };

export const modalTitle: React.CSSProperties = {
  fontSize: 17,
  fontWeight: 700,
  color: COLOR.textPrimary,
  margin: "0 0 8px",
};

export const modalBody: React.CSSProperties = {
  fontSize: 13,
  color: COLOR.textMuted,
  margin: "0 0 24px",
  lineHeight: 1.6,
};

export const modalActions: React.CSSProperties = {
  display: "flex",
  gap: 10,
  justifyContent: "center",
};

// ─── Spinner ──────────────────────────────────────────────────────────────────

export const spinner: React.CSSProperties = {
  width: 14,
  height: 14,
  border: "2px solid #fff",
  borderTopColor: "transparent",
  borderRadius: "50%",
  display: "inline-block",
  animation: "spin .7s linear infinite",
};

export const globalStyles = `
  /* Scrollbar transparan */
  .scroll-area::-webkit-scrollbar { width: 6px; }
  .scroll-area::-webkit-scrollbar-track { background: transparent; }
  .scroll-area::-webkit-scrollbar-thumb { background: transparent; border-radius: 99px; }
  .scroll-area:hover::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); }
  .scroll-area { scrollbar-width: none; }
  .scroll-area:hover { scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.12) transparent; }
  @keyframes spin { to { transform: rotate(360deg); } }
`;