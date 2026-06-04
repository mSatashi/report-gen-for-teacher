import React from "react";
import { IconChevronLeft, IconChevronRight, LogoBadge } from "../icons";
import { NAV_ITEMS } from "../data";
import { styles } from "./styles";

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
      style={{ width: collapsed ? 72 : 240, ...styles.asside}}
    >
      {/* ── Brand row ── */}
      <div
        style={{
          justifyContent: collapsed ? "center" : "space-between",
          ...styles.brandSide
        }}
      >
        {!collapsed && (
          <a
            href="#"
            style={styles.aStyle}
          >
            <LogoBadge size={32} />
            <span style={styles.brandText}>
              Automatic Report
            </span>
          </a>
        )}

        {collapsed && <LogoBadge size={32} />}

        {!collapsed && (
          <button
            onClick={(e) => { e.stopPropagation(); onToggleCollapse(); }}
            style={styles.btnCollapse}
            title="Collapse sidebar"
          >
            <IconChevronLeft />
          </button>
        )}
      </div>

      {/* ── Expand button (collapsed state) ── */}
      {collapsed && (
        <button
          onClick={(e) => { e.stopPropagation(); onToggleCollapse(); }}
          style={styles.btnExpand}
          title="Expand sidebar"
        >
          <IconChevronRight />
        </button>
      )}

      {/* ── Nav menu ── */}
      <nav style={styles.navStyle}>
        {NAV_ITEMS.map((item, i) => {
          if (item.kind === "section") {
            if (collapsed) return null;
            return (
              <div
                key={i}
                style={styles.itemNavTitle}
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
                gap: collapsed ? 0 : 12,
                padding: collapsed ? "10px 0" : "10px 18px",
                background: isActive ? "rgba(99,102,241,0.15)" : "none",
                borderLeft: isActive ? "3px solid #6366f1" : "3px solid transparent",
                color: isActive ? "#a5b4fc" : "#9ca3af",
                fontWeight: isActive ? 600 : 400,
                justifyContent: collapsed ? "center" : "flex-start",
                ...styles.btnNavSection,
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