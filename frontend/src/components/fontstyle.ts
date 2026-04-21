
import type { CSSProperties } from 'react';
import { colors } from './colorstyle';

export const fonts: Record<string, CSSProperties> = {
  h1: {
    fontSize: 18, 
    fontWeight: 700, 
    color: colors.eerieBlack,
    margin: 0
  },
  h2: {
    fontSize: 24, 
    fontWeight: 700, 
    color: colors.darkNavy, 
    margin: "0 0 4px"
  },

  normal700: {
    fontSize: "16px", 
    fontWeight: 700, 
    color: colors.dark,
  },
  normalCoolGrey: { 
    color: colors.coolGrey, 
    fontSize: 13,  
  },
};