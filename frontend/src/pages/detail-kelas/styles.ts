import type { CSSProperties } from "react";
import { colors } from "../../components/colorstyle";

export const styles: Record<string, CSSProperties> = {
  root: {
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
    background: colors.white,
    minHeight: "100vh",
    padding: "32px 28px",
    color: "#1E293B",

    borderRadius: "14px",
    boxShadow: "rgba(30, 42, 59, 0.07) 0px 1px 4px", 
    overflow: "hidden",
    border: "1.5px solid rgb(234, 236, 245)",
  },

  backBtn: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "none",
    border: "none",
    color: "#4F46E5",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
    padding: "0 0 16px 0",
  },

  pageTitle: {
    fontSize: "22px",
    fontWeight: 700,
    color: "#0F172A",
    margin: "0 0 4px",
  },

  pageSubtitle: {
    fontSize: "13px",
    color: "#64748B",
    margin: "0 0 24px",
  },

  layout: {
    display: "flex",
    gap: "20px",
    alignItems: "flex-start",
  },

  leftPanel: {
    flex: 1,
    minWidth: 0,
  },

  rightPanel: {
    width: "280px",
    flexShrink: 0,
    background: colors.white,
    border: "1px solid #E2E8F0",
    borderRadius: "14px",
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
    alignSelf: "flex-start",
  },

  rightPanelBody: {
    padding: "20px",
    flex: 1,
  },

  rightPanelFooter: {
    padding: "12px 20px",
    borderTop: "1px solid #E2E8F0",
    background: "#fff",
    display: "flex",
    gap: "8px",
  },

  btnGenerate: {
    background: "#7C3AED",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "7px 14px",
    fontSize: "12px",
    fontWeight: 700,
    cursor: "pointer",
    whiteSpace: "nowrap" as const,
  },

  btnDetailPlan: {
    background: "#fff",
    color: "#7C3AED",
    border: "1.5px solid #7C3AED",
    borderRadius: "8px",
    padding: "7px 14px",
    fontSize: "12px",
    fontWeight: 700,
    cursor: "pointer",
    whiteSpace: "nowrap" as const,
  },

  infoCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: "14px",
    padding: "20px 24px",
    marginBottom: "20px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  },

  infoGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
  },

  infoItem: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "3px",
  },

  infoLabel: {
    fontSize: "11px",
    fontWeight: 600,
    color: "#94A3B8",
    textTransform: "uppercase" as const,
    letterSpacing: "0.06em",
  },

  infoValue: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#0F172A",
  },

  sectionTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#0F172A",
    margin: "0 0 12px",
  },

  siswaList: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "8px",
  },

  siswaRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    background: "#F8FAFF",
    border: "1px solid #E2E8F0",
    borderRadius: "9px",
    padding: "11px 14px",
    transition: "box-shadow 0.15s",
  },

  siswaName: {
    fontSize: "13px",
    fontWeight: 600,
    color: "#1E293B",
  },

  siswaInfo: {
    fontSize: "11px",
    color: "#64748B",
    marginTop: "2px",
  },

  btnDetail: {
    background: "#7C3AED",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    padding: "5px 14px",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
  },

  emptyState: {
    textAlign: "center" as const,
    color: "#CBD5E1",
    fontSize: "13px",
    padding: "32px 0",
    border: "1.5px dashed #E2E8F0",
    borderRadius: "10px",
  },

  badge: {
    display: "inline-block",
    background: "#EEF2FF",
    color: "#4338CA",
    border: "1px solid #C7D2FE",
    borderRadius: "6px",
    padding: "3px 10px",
    fontSize: "12px",
    fontWeight: 500,
    marginBottom: "6px",
  },

  topikItem: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "6px 0",
    borderBottom: "1px solid #F1F5F9",
    fontSize: "13px",
    color: "#334155",
  },

  mapelName: {
    fontSize: "15px",
    fontWeight: 700,
    color: "#0F172A",
    marginBottom: "4px",
  },

  divider: {
    border: "none",
    borderTop: "1px solid #F1F5F9",
    margin: "14px 0",
  },

  loadingWrap: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "200px",
    color: "#94A3B8",
    fontSize: "14px",
  },

  toolbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "20px",
  },

  btnPrimary: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "9px 16px",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
  },

  overlay: {
    position: "fixed" as const,
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
    position: "relative" as const,
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
    textTransform: "uppercase" as const,
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
    boxSizing: "border-box" as const,
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
    boxSizing: "border-box" as const,
    background: "#FAFBFF",
    appearance: "none" as const,
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
    position: "absolute" as const,
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
  btnEdit: {
    background: "#EEF2FF",
    color: "#5B6BDF",
    border: "1.5px solid #D4D9F5",
    borderRadius: "8px",
    padding: "7px 12px",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: "5px",
  },
  kelasActions: {
    display: "flex",
    gap: "8px",
    alignItems: "center",
  },

};