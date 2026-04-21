
import type { CSSProperties } from 'react';
import { colors } from './colorstyle';

export const table: Record<string, CSSProperties> = {
  tableWrapper: { 
    flex: 1, 
    overflowY: "auto", 
    minHeight: 0 
  },
  table: { 
    width: "100%", 
    borderCollapse: "collapse", 
    fontSize: 13
  },
  tableHeaderRow: { 
    background: "rgba(228,230,239,0.85)"
  },
  tableHeaderLabel: {
    padding: "10px 14px",
    textAlign: "left",
    fontWeight: 600,
    color: colors.darkSlateGray,
    whiteSpace: "nowrap",
  },
  tdNumber: { 
    padding: "12px 14px", 
    color: colors.slateGray
  },
  td: { 
    padding: "12px 14px", 
    color: colors.darkSlateGray
  },
  tdPadding: { 
    padding: "12px 14px" 
  },
  tdNoData: { 
    padding: "40px 14px", 
    textAlign: "center", 
    color: colors.coolGrey, 
    fontSize: 13 
  },
  tdBorderBottom: { 
    borderBottom: "1px solid #f3f4f6" 
  },
};