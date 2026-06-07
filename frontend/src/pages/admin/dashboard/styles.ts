export const adminDashboardStyles = `
  .adm-content-header {
    margin-bottom: 24px;
  }
  .adm-content-header h1 {
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 4px;
  }
  .adm-content-header p {
    font-size: 13px;
    color: #6b7280;
    margin: 0;
  }

  /* ── Stat cards ── */
  .adm-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 24px;
  }
  @media (max-width: 900px) {
    .adm-stats { grid-template-columns: repeat(2, 1fr); }
    .adm-row2col { grid-template-columns: 1fr !important; }
  }
  .adm-stat {
    background: var(--adm-card-bg, #f9fafb);
    border: 1px solid var(--adm-border, #e5e7eb);
    border-radius: 10px;
    padding: 16px;
  }
  .adm-stat-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }
  .adm-stat-label {
    font-size: 12px;
    color: #6b7280;
    font-weight: 500;
  }
  .adm-stat-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
  }
  .adm-stat-val {
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
  }
  .adm-stat-sub {
    font-size: 11px;
    margin-top: 4px;
  }

  /* ── Two-column row ── */
  .adm-row2col {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 16px;
    margin-bottom: 16px;
  }

  /* ── Card ── */
  .adm-card {
    background: var(--adm-card-bg, #f9fafb);
    border: 1px solid var(--adm-border, #e5e7eb);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
  }
  .adm-card:last-child {
    margin-bottom: 0;
  }
  .adm-card-title {
    font-size: 13px;
    font-weight: 600;
    margin: 0 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .adm-card-title span {
    font-size: 11px;
    color: #6366f1;
    font-weight: 500;
    cursor: pointer;
  }

  /* ── Bar chart ── */
  .adm-chart-wrap {
    display: flex;
    align-items: flex-end;
    gap: 6px;
    height: 160px;
    margin-top: 8px;
  }
  .adm-chart-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    height: 100%;
    justify-content: flex-end;
  }
  .adm-bar-wrap {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 2px;
    align-items: center;
    justify-content: flex-end;
    flex: 1;
  }
  .adm-bar {
    width: 70%;
    border-radius: 3px 3px 0 0;
    min-height: 4px;
    transition: opacity 0.15s;
  }
  .adm-bar:hover { opacity: 0.75; }
  .adm-chart-label {
    font-size: 10px;
    color: #9ca3af;
  }

  /* ── Activity feed ── */
  .adm-act-item {
    display: flex;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid var(--adm-border, #e5e7eb);
    align-items: flex-start;
  }
  .adm-act-item:last-child { border-bottom: none; }
  .adm-act-icon {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 1px;
  }
  .adm-act-main {
    font-size: 12px;
    color: #6b7280;
    line-height: 1.4;
  }
  .adm-act-main strong {
    color: #111827;
    font-weight: 600;
  }
  .adm-act-time {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 2px;
  }

  /* ── User table ── */
  .adm-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }
  .adm-table th {
    text-align: left;
    padding: 8px 0;
    color: #9ca3af;
    font-weight: 600;
    font-size: 11px;
    border-bottom: 1px solid var(--adm-border, #e5e7eb);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .adm-table td {
    padding: 10px 0;
    border-bottom: 1px solid var(--adm-border, #e5e7eb);
    color: #6b7280;
    vertical-align: middle;
  }
  .adm-table td:first-child { color: #111827; }
  .adm-table tr:last-child td { border-bottom: none; }

  .adm-user-av {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
    flex-shrink: 0;
  }
  .adm-user-name {
    font-size: 12px;
    font-weight: 600;
    color: #111827;
  }
  .adm-user-role {
    font-size: 11px;
    color: #9ca3af;
  }

  /* ── Status pills ── */
  .adm-pill {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 20px;
    display: inline-block;
  }
  .adm-pill-aktif    { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
  .adm-pill-nonaktif { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
  .adm-pill-pending  { background: #fef9c3; color: #a16207; border: 1px solid #fde68a; }

  /* ── Kelola button ── */
  .adm-btn-sm {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid #d1d5db;
    background: transparent;
    color: #6b7280;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }
  .adm-btn-sm:hover {
    background: #f3f4f6;
    color: #111827;
  }
`;