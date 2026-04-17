
import type { CSSProperties } from 'react';
import { colors } from './colorstyle';

export const fonts: Record<string, CSSProperties> = {
  h1: {
    fontSize: 18, 
    fontWeight: 700, 
    color: colors.eerieBlack,
    margin: 0
  },

  normal700: {
    fontSize: "16px", 
    fontWeight: 700, 
    color: colors.dark,
  } 
};