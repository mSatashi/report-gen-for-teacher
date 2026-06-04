import React from "react";

const Footer: React.FC = () => {
  return (
    <footer
      style={{
        background: "#fff",
        borderTop: "1px solid #e5e7eb",
        padding: "12px 28px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexShrink: 0,
        flexWrap: "wrap",
        gap: 8,
      }}
    >
      <span style={{ fontSize: 12, color: "#9ca3af" }}>
        2025©{" "}
        <a
          href="https://argenesia.com/"
          target="_blank"
          rel="noreferrer"
          style={{ color: "#6b7280", textDecoration: "none", fontWeight: 600 }}
        >
          IF5200 - Proyek Penelitian terapan
        </a>
      </span>

      <span style={{ fontSize: 12, color: "#9ca3af" }}>
        Version <strong style={{ color: "#374151" }}>1.0.0</strong>
      </span>
    </footer>
  );
};

export default Footer;