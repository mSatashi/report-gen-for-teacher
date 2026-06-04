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

  rootMobile: {
    padding: "16px 12px",
    borderRadius: "0",
    border: "none",
    boxShadow: "none",
  },

  headerRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 20,
    flexShrink: 0,
    flexWrap: "wrap",
    gap: 12,
  },

  headerRowMobile: {
    flexDirection: "column",
    alignItems: "stretch",
    gap: 8,
  },

  titleSection: {
    flex: 1,
  },

  pageTitle: {
    fontSize: "22px",
    fontWeight: 700,
    color: "#111827",
    margin: "0 0 2px",
  },

  pageTitleMobile: {
    fontSize: "18px",
  },

  breadcrumb: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    marginBottom: 6,
    flexWrap: "wrap",
  },

  breadcrumbText: {
    fontSize: "13px",
    color: "#9ca3af",
    cursor: "pointer",
  },

  breadcrumbTextMobile: {
    fontSize: "11px",
  },

  breadcrumbSeparator: {
    fontSize: "13px",
    color: "#d1d5db",
  },

  backButtonWrapper: {
    display: "flex",
    gap: 10,
  },

  backButtonWrapperMobile: {
    justifyContent: "flex-start",
  },

  backButton: {
    background: "none",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "8px 16px",
    fontSize: 13,
    fontWeight: 500,
    color: "#374151",
    cursor: "pointer",
    transition: "all 0.2s ease",
  },

  backButtonMobile: {
    padding: "7px 14px",
    fontSize: 12,
  },

  progressBar: {
    background: "#f0fdf4",
    border: "1.5px solid #86efac",
    borderRadius: 10,
    padding: "11px 16px",
    fontSize: 13,
    color: "#166534",
    fontWeight: 500,
    display: "flex",
    alignItems: "center",
    gap: 10,
    marginBottom: 16,
    flexWrap: "wrap",
  },

  progressBarMobile: {
    padding: "10px 12px",
    fontSize: 12,
    gap: 8,
  },

  progressBarInner: {
    flex: 1,
    background: "#bbf7d0",
    borderRadius: 99,
    height: 5,
    minWidth: 60,
  },

  progressBarText: {
    fontSize: 12,
    fontWeight: 700,
    whiteSpace: "nowrap" as const,
  },

  layout: {
    display: "flex",
    gap: "20px",
    alignItems: "flex-start",
  },

  layoutMobile: {
    flexDirection: "column",
    gap: "16px",
  },

  leftPanel: {
    flex: 1,
    minWidth: 0,
    width: "100%",
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

  rightPanelMobile: {
    width: "100%",
    alignSelf: "stretch",
  },

  rightPanelBody: {
    padding: "20px",
    flex: 1,
  },

  rightPanelBodyMobile: {
    padding: "14px",
  },

  rightPanelFooter: {
    padding: "12px 20px",
    borderTop: "1px solid #E2E8F0",
    background: "#fff",
    display: "flex",
    gap: "8px",
  },

  rightPanelFooterMobile: {
    padding: "10px 14px",
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
    transition: "all 0.2s ease",
    flex: 1,
    textAlign: "center" as const,
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
    transition: "all 0.2s ease",
    flex: 1,
    textAlign: "center" as const,
  },

  infoCard: {
    background: "#fff",
    border: "1px solid #E2E8F0",
    borderRadius: "14px",
    padding: "20px 24px",
    marginBottom: "16px",
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  },

  infoCardMobile: {
    padding: "14px",
    borderRadius: "12px",
    marginBottom: "12px",
  },

  infoGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "16px",
  },

  infoGridMobile: {
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
  },

  infoGridSmall: {
    gridTemplateColumns: "1fr",
    gap: "10px",
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
    wordBreak: "break-word" as const,
  },

  infoValueMobile: {
    fontSize: "13px",
  },

  sectionTitle: {
    fontSize: "14px",
    fontWeight: 700,
    color: "#0F172A",
    margin: "0 0 0",
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
    gap: "8px",
  },

  siswaRowMobile: {
    flexDirection: "column",
    alignItems: "flex-start",
    gap: "10px",
    padding: "12px",
  },

  siswaName: {
    fontSize: "13px",
    fontWeight: 600,
    color: "#1E293B",
  },

  siswaActions: {
    display: "flex",
    alignItems: "center",
    gap: "6px",
    flexShrink: 0,
  },

  siswaActionsMobile: {
    width: "100%",
    justifyContent: "flex-start",
    flexWrap: "wrap" as const,
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
    transition: "all 0.2s ease",
    whiteSpace: "nowrap" as const,
  },

  emptyState: {
    textAlign: "center" as const,
    color: "#CBD5E1",
    fontSize: "13px",
    padding: "32px 0",
    border: "1.5px dashed #E2E8F0",
    borderRadius: "10px",
  },

  toolbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "16px",
    gap: "8px",
  },

  toolbarMobile: {
    flexWrap: "wrap" as const,
  },

  btnPrimary: {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    background: "#4F46E5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "8px 14px",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    transition: "all 0.2s ease",
    whiteSpace: "nowrap" as const,
    flexShrink: 0,
  },

  kelasActions: {
    display: "flex",
    gap: "6px",
    alignItems: "center",
    flexWrap: "wrap" as const,
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
    wordBreak: "break-word" as const,
  },

  mapelName: {
    fontSize: "15px",
    fontWeight: 700,
    color: "#0F172A",
    marginBottom: "4px",
    wordBreak: "break-word" as const,
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

  overlay: {
    position: "fixed" as const,
    inset: 0,
    background: "rgba(15,22,36,0.45)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    backdropFilter: "blur(2px)",
    padding: "16px",
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

  modalMobile: {
    padding: "24px 18px",
    borderRadius: "14px",
  },

  modalTitle: {
    fontSize: "18px",
    fontWeight: 700,
    color: "#1E2A3B",
    marginBottom: "4px",
  },

  modalTitleMobile: {
    fontSize: "16px",
  },

  modalSubtitle: {
    fontSize: "13px",
    color: "#8A9BB0",
    marginBottom: "24px",
  },

  modalSubtitleMobile: {
    fontSize: "12px",
    marginBottom: "18px",
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

  modalFooter: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px",
    marginTop: "28px",
  },

  modalFooterMobile: {
    flexDirection: "column-reverse" as const,
    gap: "10px",
    marginTop: "20px",
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
    transition: "all 0.2s ease",
  },

  btnCancelMobile: {
    padding: "12px 20px",
    width: "100%",
    textAlign: "center" as const,
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
    transition: "all 0.2s ease",
  },

  btnSaveMobile: {
    padding: "12px 24px",
    width: "100%",
    textAlign: "center" as const,
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
    transition: "all 0.2s ease",
  },

  closeBtnMobile: {
    top: "14px",
    right: "14px",
  },

  btnDanger: {
    background: "#FEF2F2",
    color: "#E53E3E",
    border: "1.5px solid #FED7D7",
    borderRadius: "8px",
    padding: "5px 10px",
    fontSize: "12px",
    fontWeight: 600,
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "4px",
    transition: "all 0.2s ease",
    flexShrink: 0,
  },

  generateButton: {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    border: "none",
    borderRadius: 8,
    padding: "6px 12px",
    fontSize: 12,
    fontWeight: 700,
    whiteSpace: "nowrap" as const,
    background: "#4F46E5",
    color: "#fff",
    cursor: "pointer",
    transition: "all 0.2s ease",
  },

  spinner: {
    width: 12,
    height: 12,
    border: "2px solid #fff",
    borderTopColor: "transparent",
    borderRadius: "50%",
    display: "inline-block",
    animation: "spin 0.7s linear infinite",
  },

  toastContainer: {
    position: "fixed" as const,
    bottom: "24px",
    right: "24px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
    zIndex: 2000,
  },

  toastContainerMobile: {
    bottom: "12px",
    right: "12px",
    left: "12px",
  },

  toast: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    borderRadius: "10px",
    padding: "12px 16px",
    fontSize: "13px",
    fontWeight: 600,
    boxShadow: "0 4px 16px rgba(0,0,0,0.10)",
    minWidth: "260px",
    maxWidth: "360px",
    animation: "slideIn 0.2s ease",
  },

  toastMobile: {
    minWidth: "unset",
    maxWidth: "100%",
    width: "100%",
  },

  toastSuccess: {
    background: "#F0FDF4",
    border: "1.5px solid #4ADE80",
    color: "#15803D",
  },

  toastError: {
    background: "#FFF1F2",
    border: "1.5px solid #FDA4AF",
    color: "#9F1239",
  },

  siswaCountBadge: {
    marginLeft: "8px",
    background: "#EEF2FF",
    color: "#4338CA",
    borderRadius: "999px",
    padding: "1px 10px",
    fontSize: "11px",
    fontWeight: 700,
  },
};

export const globalStyles = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }

  @media (max-width: 480px) {
    @keyframes slideIn {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  }
`;