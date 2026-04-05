import React, { useEffect, useRef, useState } from "react";
import { IconMenu, LogoBadge } from "../icons";
import { styles } from "./styles";

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
      style={styles.headerStyle}
    >
      {/* Left: mobile hamburger + app title */}
      <div style={styles.headerHamberger}>
        <button
          onClick={onOpenMobileMenu}
          className="mobile-menu-btn"
          style={styles.btnHumburger}
          aria-label="Open menu"
        >
          <IconMenu />
        </button>
      </div>

      <div ref={dropdownRef} style={styles.positionRelative}>
 
        {/* Trigger */}
        <button
          onClick={() => setOpen((v) => !v)}
          style={styles.btnHeader}
          title={namaLengkap}
        >
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt="user"
              style={styles.imgAvatar}
            />
          ) : (
            <LogoBadge size={32} />
          )}
        </button>
 
        {/* Dropdown panel */}
        {open && (
          <div
            style={styles.headerDropdown}
          >
            {/* User info */}
            <div style={styles.boxHeader}>
              <div
                style={styles.avatarBoundaries}
              >
                {avatarUrl ? (
                  <img src={avatarUrl} alt="Logo" style={styles.imgAvatar} />
                ) : (
                  <LogoBadge size={38} />
                )}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={styles.nameStyle}>
                  {namaLengkap}
                </div>
                <div style={styles.emailStyle}>
                  {email}
                </div>
              </div>
            </div>
 
            <div style={styles.lineStyle} />
 
            {/* Sign Out */}
            <button
              onClick={() => { setOpen(false); onSignOut?.(); }}
              // onClick={() => navigate("/login")}
              style={styles.btnSignOut}
              onMouseEnter={(e) => (e.currentTarget.style.background = "#f9fafb")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "none")}
            >
              Sign Out
            </button>
 
            <div style={styles.lineStyle} />

 
            <div style={{ height: 8 }} />
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;