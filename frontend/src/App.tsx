import React, { useEffect, useState } from "react";
import Sidebar from "./components/sidebar";
import Header from "./components/header";
import Footer from "./components/footer";
import DashboardPage from "./pages/dashboard/Dashboard";
import { NAV_ITEMS } from "./data";
import ReportEditor from "./pages/report-editor";
import { sidebarStyles, styles } from "./styles";
import { fonts } from "./components/fontstyle";
import LoginPage from "./pages/login";
import { loginAPI, logout, type AuthUser } from "./service/authService";
import MasterKelas from "./pages/master-kelas";
import { setUnauthorizedHandler } from "./service/apiFetch";
import MasterSiswa from "./pages/master-siswa";
import MasterMapel from "./pages/master-mapel";
import DetailKelas from "./pages/detail-kelas";
import DetailLogSiswa from "./pages/detail-log-siswa";
import DailyLogFormLog from "./pages/form-daily-log";
import type { DailyLogResponse, KelasResponse, MapelResponse, ReportGeneratorResponse, SiswaResponse } from "./service/payload";
import PlanDetail from "./pages/plan-detail";
import ListReportGenerator from "./pages/list-report";
import DetailReport from "./pages/detail-report";

// Helper token
const TOKEN_KEY = "auth_token";
const USER_KEY  = "auth_user";

const App: React.FC = () => {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const saved = localStorage.getItem(USER_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch { return null; }
  });
  const [loginError, setLoginError] = useState<string>("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [activeRoute, setActiveRoute] = useState<string>("home");
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);

  const [routeParams, setRouteParams] = useState<Record<string, unknown>>({});

  const handleNavigate = (route: string, params?: Record<string, unknown>) => {
    setActiveRoute(route);
    setRouteParams(params ?? {});
  };

  const isLoggedIn = !!user;

  /** meta title page */
  const APP_NAME = import.meta.env.META_TITLE ?? "Report GenAI Otomatis";

  /** Derive the current page title from NAV_ITEMS */
  const ROUTE_TITLES: Record<string, string> = {
    home: "Dashboard",
    learningPlan: "Learning Plan",
    reportEditor: "Report Editor",
    masterKelas: "Master Kelas",
    masterSiswa: "Master Siswa",
    masterMapel: "Master Mata Pelajaran",
    detailKelas: "Detail Kelas",
    logSiswa: "Log Siswa",
    formDailyLog: "Form Daily Log",
    planDetail: "Detail Plan",
    detailReport: 'Detail Report',
    listReportGen: 'List Report Generate'
  };

  const pageTitle =
    ROUTE_TITLES[activeRoute] ??
    (NAV_ITEMS.find(
      (n) => n.kind === "link" && (n as { route: string }).route === activeRoute
    ) as { label?: string } | undefined)?.label ??
    "Dashboard";    

  /** Login handler — dipanggil dari LoginPage */
  const handleLogin = async (data: {
    email: string;
    password: string;
  }) => {
    try {
      setLoginError("");
      setLoginLoading(true);
      const authUser = await loginAPI({
        email: data.email,
        password: data.password,
      });

      localStorage.setItem(TOKEN_KEY, authUser.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(authUser));

      setUser(authUser);
      setActiveRoute("home");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Terjadi kesalahan.";
      setLoginError(message);
    } finally {
      setLoginLoading(false);
    }
  };

  /** Logout handler */
  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.warn("Logout API gagal, tetap logout lokal:", err);
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      setUser(null);
      setActiveRoute("home");
    }
  }

  useEffect(() => {
    setUnauthorizedHandler(handleLogout);
    document.title = pageTitle ? `${pageTitle} — ${APP_NAME}` : APP_NAME;
  }, [pageTitle]);

  /** Jika belum login → tampilkan LoginPage saja  */
  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} error={loginError} loading={loginLoading} />;
  }

  /** Render the active page */
  const renderPage = () => {
    switch (activeRoute) {
      case "home":
        return <DashboardPage namaLengkap={user?.username ?? "Pengguna"} />;
      case "reportEditor":
        return <ReportEditor 
          onNavigate={handleNavigate}
          reportData={routeParams.reportData as ReportGeneratorResponse} 
          siswaId={routeParams.siswaId as string}  />;
      case "masterKelas":
        return <MasterKelas onNavigate={handleNavigate} />;
      case "masterSiswa":
        return <MasterSiswa />;
      case "masterMapel":
        return <MasterMapel />;
      case "detailKelas":
        return <DetailKelas 
          kelasId={routeParams.kelasId as string} 
          onNavigate={handleNavigate}/>;
      case "logSiswa":
        return <DetailLogSiswa 
          onNavigate={handleNavigate} 
          siswaId={routeParams.siswaId as string} 
          kelasId={routeParams.kelasId as string} 
          mapel={routeParams.mapel as MapelResponse} 
          siswa={routeParams.siswa as SiswaResponse} />;
      case "formDailyLog":
        return <DailyLogFormLog 
          onNavigate={handleNavigate} 
          namaSiswa={routeParams.namaSiswa as string}
          kelasId={routeParams.kelasId as string}
          siswa={routeParams.siswa as SiswaResponse}
          dataLog={routeParams.dataLog as DailyLogResponse | null}
          mapel={routeParams.mapel as MapelResponse} />;
      case "planDetail":
        return <PlanDetail 
          onNavigate={handleNavigate} 
          kelas={routeParams.kelas as KelasResponse}
          mapel={routeParams.mapel as MapelResponse}
           />;
      case "listReportGen":
        return <ListReportGenerator onNavigate={handleNavigate}  />;
      case "detailReport":
        return <DetailReport onNavigate={handleNavigate} siswaId={routeParams.siswaId as string} />;
      default:
        return (
          <div style={styles.pageNotFound}>
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
          onToggleCollapse={() => setMobileSidebarOpen(false)}
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
        <Header onOpenMobileMenu={() => setMobileSidebarOpen(true)}
          namaLengkap={user?.username ?? "Pengguna"}
          email={user?.email_address ?? ""}
          onSignOut={handleLogout}
        />

        {/* Toolbar / page title */}
        <div
          style={styles.toolbar}
        >
          <div style={fonts.normal700}>
            {pageTitle}
          </div>
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
      <style>{sidebarStyles}</style>
    </div>
  );
};

export default App;