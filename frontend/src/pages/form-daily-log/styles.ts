import type { CSSProperties } from "react";
import { inputStyle } from "../daily-log/components/constants";

export const styles: Record<string, CSSProperties> = {
  lockedFieldStyle: { 
    ...inputStyle,
    background: "#f9fafb",
    color: "#6b7280",
    cursor: "not-allowed",
    border: "1px solid #f3f4f6", 
  },
};