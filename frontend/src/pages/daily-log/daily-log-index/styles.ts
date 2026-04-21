import type { CSSProperties } from "react";
import { colors } from "../../../components/colorstyle";

export const styles: Record<string, CSSProperties> = {
  root: { 
    display: "flex", 
    flexDirection: "column", 
    height: "100%", 
    gap: 0 
  },
  headingContent: { 
    marginBottom: 20, 
    flexShrink: 0
  },
  card: {
    background: colors.white,
    borderRadius: 14,
    padding: "24px 28px",
    boxShadow: "0 1px 4px rgba(0,0,0,.06)",
    flex: 1,
    minHeight: 0,
    display: "flex",
    flexDirection: "column",
  },
  btnDetail: {
    background: colors.cyan, 
    color: colors.white, 
    border: "none",
    borderRadius: 6, 
    padding: "5px 12px",
    fontSize: 12, 
    fontWeight: 600, 
    cursor: "pointer",
  }
}