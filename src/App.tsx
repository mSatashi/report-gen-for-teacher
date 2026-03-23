import React, { useEffect, useState } from "react";
import Sidebar from "./components/sidebar";
import Header from "./components/header";
import Footer from "./components/footer";
import DashboardPage from "./pages/dashboard/Dashboard";
import { NAV_ITEMS } from "./data"; 
import DailyLogPage from "./pages/daily-log";
import LearningPlan from "./pages/learning-plan";
import ReportEditor from "./pages/report-editor";

const App: React.FC = () => {
  const [activeRoute, setActiveRoute]         = useState<string>("home");
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);

  /** Derive the current page title from NAV_ITEMS */
  const pageTitle =
    (NAV_ITEMS.find(
      (n) => n.kind === "link" && (n as { route: string }).route === activeRoute
    ) as { label?: string } | undefined)?.label ?? "Dashboard";

  /** meta title page */
  const APP_NAME = import.meta.env.META_TITLE ?? "Report GenAI Otomatis";

  useEffect(() => {
    document.title = pageTitle ? `${pageTitle} — ${APP_NAME}` : APP_NAME;
  }, [pageTitle]);


  /** Render the active page */
  const renderPage = () => {
    switch (activeRoute) {
      case "home":
        return <DashboardPage />;
      case "dailyLog":
        return <DailyLogPage />;
      case "learningPlan":
        return <LearningPlan />;
      case "reportEditor":
        return <ReportEditor />;
      default:
        return (
          <div style={{ color: "#9ca3af", fontSize: 14, padding: 8 }}>
            Halaman <strong>{pageTitle}</strong> belum tersedia.
          </div>
        );
    }
  };

  return (
    <div
      style={{
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
      }}
    >
      {/* ── Mobile overlay ── */}
      {mobileSidebarOpen && (
        <div
          onClick={() => setMobileSidebarOpen(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            zIndex: 40,
          }}
        />
      )}

      {/* ── Mobile sidebar drawer ── */}
      <div
        className="mobile-sidebar-drawer"
        style={{
          position: "fixed",
          top: 0,
          bottom: 0,
          left: mobileSidebarOpen ? 0 : -260,
          width: 240,
          zIndex: 50,
          transition: "left .25s",
          display: "none", // shown via CSS media query
        }}
      >
        <Sidebar
          activeRoute={activeRoute}
          collapsed={false}
          onNavigate={(route) => {
            setActiveRoute(route);
            setMobileSidebarOpen(false);
          }}
          onToggleCollapse={() => {}}
        />
      </div>

      {/* ── Desktop sidebar ── */}
      <div className="desktop-sidebar">
        <Sidebar
          activeRoute={activeRoute}
          collapsed={sidebarCollapsed}
          onNavigate={setActiveRoute}
          onToggleCollapse={() => setSidebarCollapsed((v) => !v)}
        />
      </div>

      {/* ── Main area ── */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          minWidth: 0,
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <Header onOpenMobileMenu={() => setMobileSidebarOpen(true)} />

        {/* Toolbar / page title */}
        <div
          style={{
            background: "#fff",
            borderBottom: "1px solid #e5e7eb",
            padding: "10px 28px",
            flexShrink: 0,
          }}
        >
          <h1 style={{ fontSize: 18, fontWeight: 700, color: "#111827", margin: 0 }}>
            {pageTitle}
          </h1>
        </div>

        {/* Content */}
        <main
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "28px 28px 40px",
          }}
        >
          {renderPage()}
        </main>

        {/* Footer */}
        <Footer />
      </div>

      {/* ── Global styles ── */}
      <style>{`
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
      `}</style>
    </div>
  );
};

export default App;