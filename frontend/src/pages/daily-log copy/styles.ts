
import type { CSSProperties } from 'react';
import { colors } from '../../components/colorstyle';

export const styles: Record<string, CSSProperties> = {
  container: { 
    display: "flex", 
    flexDirection: "column", 
    height: "100%", 
    gap: 0 
  },
  btnAdd: {
    background: colors.cyan, 
    color: colors.white, 
    border: "none",
    borderRadius: 8, 
    padding: "8px 16px", 
    fontSize: 13, 
    fontWeight: 600, 
    cursor: "pointer",
  },
};