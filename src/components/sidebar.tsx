import React from "react";
import { IconChevronLeft, IconChevronRight, LogoBadge } from "../icons";
import { NAV_ITEMS } from "../data";

interface SidebarProps {
  activeRoute: string;
  collapsed: boolean;
  onNavigate: (route: string) => void;
  onToggleCollapse: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  activeRoute,
  collapsed,
  onNavigate,
  onToggleCollapse,
}) => {
  return (
    <aside
      style={{
        width: collapsed ? 72 : 240,
        background: "#1e2130",
        display: "flex",
        flexDirection: "column",
        transition: "width .25s",
        flexShrink: 0,
        zIndex: 50,
        overflow: "hidden",
      }}
    >
      {/* ── Brand row ── */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: collapsed ? "center" : "space-between",
          padding: "16px 18px",
          borderBottom: "1px solid rgba(24, 21, 21, 0.07)",
          minHeight: 60,
        }}
      >
        {!collapsed && (
          <a
            href="#"
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              textDecoration: "none",
            }}
          >
            <LogoBadge size={32} />
            <span style={{ color: "#fff", fontWeight: 700, fontSize: 14, whiteSpace: "nowrap" }}>
              Automatic Report
            </span>
          </a>
        )}

        {collapsed && <LogoBadge size={32} />}

        {!collapsed && (
          <button
            onClick={onToggleCollapse}
            style={{
              background: "none",
              border: "none",
              color: "#9ca3af",
              cursor: "pointer",
              padding: 4,
              display: "flex",
              alignItems: "center",
            }}
            title="Collapse sidebar"
          >
            <IconChevronLeft />
          </button>
        )}
      </div>

      {/* ── Expand button (collapsed state) ── */}
      {collapsed && (
        <button
          onClick={onToggleCollapse}
          style={{
            background: "none",
            border: "none",
            color: "#9ca3af",
            cursor: "pointer",
            padding: "10px 0",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "4px 0",
          }}
          title="Expand sidebar"
        >
          <IconChevronRight />
        </button>
      )}

      {/* ── Nav menu ── */}
      <nav style={{ flex: 1, overflowY: "auto", overflowX: "hidden", padding: "8px 0" }}>
        {NAV_ITEMS.map((item, i) => {
          if (item.kind === "section") {
            if (collapsed) return null;
            return (
              <div
                key={i}
                style={{
                  padding: "16px 18px 0px",
                  fontSize: 10,
                  letterSpacing: 1,
                  color: "#6b7280",
                  fontWeight: 600,
                  textTransform: "uppercase",
                  whiteSpace: "nowrap",
                }}
              >
                {item.label}
              </div>
            );
          }

          const isActive = activeRoute === item.route;

          return (
            <button
              key={i}
              onClick={() => onNavigate(item.route)}
              title={collapsed ? item.label : undefined}
              style={{
                display: "flex",
                alignItems: "center",
                gap: collapsed ? 0 : 12,
                padding: collapsed ? "10px 0" : "10px 18px",
                width: "100%",
                background: isActive ? "rgba(99,102,241,0.15)" : "none",
                border: "none",
                borderLeft: isActive ? "3px solid #6366f1" : "3px solid transparent",
                color: isActive ? "#a5b4fc" : "#9ca3af",
                cursor: "pointer",
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                justifyContent: collapsed ? "center" : "flex-start",
                transition: "all .15s",
                whiteSpace: "nowrap",
              }}
            >
              <span style={{ color: isActive ? "#a5b4fc" : "#6b7280", flexShrink: 0 }}>
                {item.icon}
              </span>
              {!collapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;