import type { CSSProperties } from "react";

export const styles: Record<string, CSSProperties> = {
  // header
  headerStyle: {
    height: 60,
    background: "#fff",
    borderBottom: "1px solid #e5e7eb",
    display: "flex",
    alignItems: "center",
    padding: "0 20px",
    justifyContent: "space-between",
    flexShrink: 0,
  },
  headerHamberger: { 
    display: "flex", 
    alignItems: "center", 
    gap: 12 
  },
  btnHumburger: {
    display: "none",
    background: "none",
    border: "none",
    cursor: "pointer",
    color: "#374151",
    alignItems: "center",
  },
  positionRelative: {
    position: "relative" 
  },
  btnHeader: {
    width: 38,
    height: 38,
    borderRadius: "50%",
    border: "2px solid rgb(255, 255, 255)",
    overflow: "hidden",
    cursor: "pointer",
    padding: 0,
    background: "none",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  imgAvatar: { 
    width: "100%", 
    height: "100%", 
    objectFit: "cover" 
  },
  headerDropdown: {
    position: "absolute",
    top: "calc(100% + 10px)",
    right: 0,
    width: 275,
    background: "rgb(255, 255, 255)",
    borderRadius: 12,
    boxShadow: "0 8px 30px rgba(0,0,0,0.12)",
    zIndex: 1000,
    overflow: "hidden",
  },
  boxHeader: { 
    display: "flex", 
    alignItems: "center", 
    gap: 14, 
    padding: "16px 18px" 
  },
  avatarBoundaries: {
    width: 50, 
    height: 50, 
    borderRadius: "50%", 
    flexShrink: 0,
    overflow: "hidden", 
    border: "2px solid rgb(255, 255, 255)",
    background: "#f9fafb",
    display: "flex", 
    alignItems: "center", 
    justifyContent: "center",
  },
  nameStyle: { 
    fontWeight: 700, 
    fontSize: 14, 
    color: "#111827", 
    marginBottom: 2, 
    whiteSpace: "nowrap", 
    overflow: "hidden", 
    textOverflow: "ellipsis" 
  },
  emailStyle: { 
    fontSize: 12, 
    color: "#9ca3af", 
    whiteSpace: "nowrap", 
    overflow: "hidden", 
    textOverflow: "ellipsis" 
  },
  lineStyle: { 
    height: 1, 
    background: "#f3f4f6", 
    margin: "0 18px" 
  },
  btnSignOut: {
    display: "block", 
    width: "100%", 
    textAlign: "left",
    padding: "12px 18px", 
    fontSize: 14, 
    fontWeight: 500,
    color: "#374151", 
    background: "none", 
    border: "none",
    cursor: "pointer",
  },

  // sidebar
  asside: {
    background: "#1e2130",
    display: "flex",
    flexDirection: "column",
    transition: "width .25s",
    flexShrink: 0,
    zIndex: 50,
    overflow: "hidden",
  },
  brandSide: {
    display: "flex",
    alignItems: "center",
    padding: "16px 18px",
    borderBottom: "1px solid rgba(24, 21, 21, 0.07)",
    minHeight: 60,
  },
  aStyle: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    textDecoration: "none",
  },
  brandText: { 
    color: "#fff", 
    fontWeight: 700, 
    fontSize: 14, 
    whiteSpace: "nowrap" 
  },
  btnCollapse: {
    background: "none",
    border: "none",
    color: "#9ca3af",
    cursor: "pointer",
    padding: 4,
    display: "flex",
    alignItems: "center",
  },
  btnExpand: {
    background: "none",
    border: "none",
    color: "#9ca3af",
    cursor: "pointer",
    padding: "10px 0",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    margin: "4px 0",
  },
  navStyle: { 
    flex: 1, 
    overflowY: "auto", 
    overflowX: "hidden", 
    padding: "8px 0" 
  },
  itemNavTitle: {
    padding: "16px 18px 0px",
    fontSize: 10,
    letterSpacing: 1,
    color: "#6b7280",
    fontWeight: 600,
    textTransform: "uppercase",
    whiteSpace: "nowrap",
  },
  btnNavSection: {
    display: "flex",
    alignItems: "center",
    width: "100%",
    borderTop: "none",
    borderRight: "none",
    borderBottom: "none",
    cursor: "pointer",
    fontSize: 13,
    transition: "all .15s",
    whiteSpace: "nowrap",
  }
};