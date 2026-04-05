
import type { CSSProperties } from 'react';

export const styles: Record<string, CSSProperties> = {
  container: {
    display: "flex",
    width: "100vw",
    height: "100vh",
    maxWidth: "100vw",
    maxHeight: "100vh",
    fontFamily: "'Poppins', sans-serif",
    background: "#f9fafb",
    overflow: "hidden",
    position: "fixed",
    top: 0,
    left: 0,
  },
  sidebarMobile: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.4)",
    zIndex: 40,
  },
  mSidebarDrawer: {
    position: "fixed",
    top: 0,
    bottom: 0,
    width: 240,
    zIndex: 50,
    transition: "left .25s",
    display: "none", // shown via CSS media query
  },
  mainArea: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    minWidth: 0,
    overflow: "hidden",
  },
  toolbar: {
    background: "#fff",
    borderBottom: "1px solid #e5e7eb",
    padding: "10px 28px",
    flexShrink: 0,
  },
  root: {
    flex: 1,
    overflowY: "auto",
    padding: "28px 28px 40px",
  },
  pageNotFound: { 
    color: "#9ca3af", 
    fontSize: 14, 
    padding: 8 
  },
};

export const sidebarStyles = `
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
  * { box-sizing: border-box; }
  body { margin: 0; }

  /* Desktop: show desktop sidebar, hide mobile drawer */
  .desktop-sidebar  { display: flex; }
  .mobile-sidebar-drawer { display: none; }
  .mobile-menu-btn  { display: none !important; }

  @media (max-width: 1023px) {
    .desktop-sidebar        { display: none !important; }
    .mobile-sidebar-drawer  { display: flex !important; }
    .mobile-menu-btn        { display: flex !important; }
  }
`;