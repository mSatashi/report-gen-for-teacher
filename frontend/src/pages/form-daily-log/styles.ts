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
  }
};