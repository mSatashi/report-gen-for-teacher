import React from "react";
import { IconMenu, LogoBadge } from "../icons";

interface HeaderProps {
  onOpenMobileMenu: () => void;
}

const Header: React.FC<HeaderProps> = ({ onOpenMobileMenu }) => {
  return (
    <header
      style={{
        height: 60,
        background: "#fff",
        borderBottom: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        padding: "0 20px",
        justifyContent: "space-between",
        flexShrink: 0,
      }}
    >
      {/* Left: mobile hamburger + app title */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <button
          onClick={onOpenMobileMenu}
          className="mobile-menu-btn"
          style={{
            display: "none",
            background: "none",
            border: "none",
            cursor: "pointer",
            color: "#374151",
            alignItems: "center",
          }}
          aria-label="Open menu"
        >
          <IconMenu />
        </button>

        {/* <span style={{ fontSize: 14, fontWeight: 600, color: "#111827" }}>
          Sistem Perencanaan Materi Adaptif &amp; Pelaporan Otomatis
        </span> */}
      </div>

      {/* Right: user avatar */}
      {/* <div
        style={{
          width: 38,
          height: 38,
          borderRadius: "50%",
          background: "linear-gradient(135deg,#3b82f6,#6366f1)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#fff",
          fontWeight: 700,
          fontSize: 14,
          cursor: "pointer",
          flexShrink: 0,
        }}
        title="Bu Rara"
      >
        BR
      </div> */}
      <LogoBadge size={32} />
    </header>
  );
};

export default Header;