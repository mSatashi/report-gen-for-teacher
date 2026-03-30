import React, { useEffect, useRef, useState } from "react";
import { IconMenu, LogoBadge } from "../icons";

interface HeaderProps {
  onOpenMobileMenu: () => void;
  namaLengkap?: string;
  email?: string;
  avatarUrl?: string;
  onSignOut?: () => void;
}

const Header: React.FC<HeaderProps> = ({ 
  onOpenMobileMenu, 
  namaLengkap = "Nama Lengkap",
  email = "email@gmail.com",
  avatarUrl,
  onSignOut }) => {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

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

      <div ref={dropdownRef} style={{ position: "relative" }}>
 
        {/* Trigger */}
        <button
          onClick={() => setOpen((v) => !v)}
          style={{
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
          }}
          title={namaLengkap}
        >
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt="user"
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          ) : (
            <LogoBadge size={32} />
          )}
        </button>
 
        {/* Dropdown panel */}
        {open && (
          <div
            style={{
              position: "absolute",
              top: "calc(100% + 10px)",
              right: 0,
              width: 275,
              background: "rgb(255, 255, 255)",
              borderRadius: 12,
              boxShadow: "0 8px 30px rgba(0,0,0,0.12)",
              zIndex: 1000,
              overflow: "hidden",
            }}
          >
            {/* User info */}
            <div style={{ display: "flex", alignItems: "center", gap: 14, padding: "16px 18px" }}>
              <div
                style={{
                  width: 50, height: 50, borderRadius: "50%", flexShrink: 0,
                  overflow: "hidden", border: "2px solid rgb(255, 255, 255)",
                  background: "#f9fafb",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}
              >
                {avatarUrl ? (
                  <img src={avatarUrl} alt="Logo" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                ) : (
                  <LogoBadge size={38} />
                )}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: "#111827", marginBottom: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {namaLengkap}
                </div>
                <div style={{ fontSize: 12, color: "#9ca3af", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {email}
                </div>
              </div>
            </div>
 
            <div style={{ height: 1, background: "#f3f4f6", margin: "0 18px" }} />
 
            {/* Sign Out */}
            <button
              onClick={() => { setOpen(false); onSignOut?.(); }}
              style={{
                display: "block", width: "100%", textAlign: "left",
                padding: "12px 18px", fontSize: 14, fontWeight: 500,
                color: "#374151", background: "none", border: "none",
                cursor: "pointer",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#f9fafb")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "none")}
            >
              Sign Out
            </button>
 
            <div style={{ height: 1, background: "#f3f4f6", margin: "0 18px" }} />

 
            <div style={{ height: 8 }} />
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;