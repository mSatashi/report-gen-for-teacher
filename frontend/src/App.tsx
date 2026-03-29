import React, { useEffect, useState } from "react";
import Sidebar from "./components/sidebar";
import Header from "./components/header";
import Footer from "./components/footer";
import DashboardPage from "./pages/dashboard/Dashboard";
import { NAV_ITEMS } from "./data"; 
import DailyLogPage from "./pages/daily-log";
import LearningPlan from "./pages/learning-plan";
import ReportEditor from "./pages/report-editor";
import { styles } from "./styles";
import { fonts } from "./components/fontstyle";

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
      style={styles.container}
    >
      {/* ── Mobile overlay ── */}
      {mobileSidebarOpen && (
        <div
          onClick={() => setMobileSidebarOpen(false)}
          style={styles.sidebarMobile}
        />
      )}

      {/* ── Mobile sidebar drawer ── */}
      <div
        className="mobile-sidebar-drawer"
        style={{ ...styles.mSidebarDrawer,
          left: mobileSidebarOpen ? 0 : -260,
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
        style={styles.mainArea}
      >
        {/* Header */}
        <Header onOpenMobileMenu={() => setMobileSidebarOpen(true)} />

        {/* Toolbar / page title */}
        <div
          style={styles.toolbar}
        >
          <h1 style={fonts.h1}>
            {pageTitle}
          </h1>
        </div>

        {/* Content */}
        <main
          style={styles.root}
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