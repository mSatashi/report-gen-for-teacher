import { Link, useLocation } from 'react-router-dom'

function Sidebar() {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path ? 'here show' : ''
  }

  return (
    <div
      id="kt_aside"
      className="aside aside-dark aside-hoverable"
      data-kt-drawer="true"
      data-kt-drawer-name="aside"
    >
      {/* Logo */}
      <div className="aside-logo flex-column-auto" id="kt_aside_logo">
        <Link to="/">
          <img
            alt="Logo"
            src="/src/assets/images/logo_itb_512.png"
            className="h-25px logo"
          />
        </Link>

        {/* Toggle */}
        <div
          id="kt_aside_toggle"
          className="btn btn-icon w-auto px-0 btn-active-color-primary aside-toggle active"
        >
          <span className="svg-icon svg-icon-1 rotate-180">
            {/* SVG tetap */}
          </span>
        </div>
      </div>

      {/* Menu */}
      <div className="aside-menu flex-column-fluid">
        <div className="hover-scroll-overlay-y my-5 my-lg-5">

          <div className="menu menu-column">

            {/* Section */}
            <div className="menu-item">
              <div className="menu-content pt-8 pb-2">
                <span className="menu-section text-muted text-uppercase fs-8 ls-1">
                  Main Menu
                </span>
              </div>
            </div>

            {/* Dashboard */}
            <div className={`menu-item ${isActive('/')}`}>
              <Link className="menu-link" to="/">
                <span className="menu-icon">📊</span>
                <span className="menu-title">Dashboard</span>
              </Link>
            </div>

            {/* Daily Log */}
            <div className={`menu-item ${isActive('/daililog')}`}>
              <Link className="menu-link" to="/daililog">
                <span className="menu-icon">📝</span>
                <span className="menu-title">Daily Log</span>
              </Link>
            </div>

            {/* Learning Plan */}
            <div className={`menu-item ${isActive('/learning-plan')}`}>
              <Link className="menu-link" to="/learning-plan">
                <span className="menu-icon">📚</span>
                <span className="menu-title">Learning Plan</span>
              </Link>
            </div>

            {/* Section */}
            <div className="menu-item">
              <div className="menu-content pt-8 pb-2">
                <span className="menu-section text-muted text-uppercase fs-8 ls-1">
                  Report
                </span>
              </div>
            </div>

            {/* Report Editor */}
            <div className={`menu-item ${isActive('/report-editor')}`}>
              <Link className="menu-link" to="/report-editor">
                <span className="menu-icon">📄</span>
                <span className="menu-title">Report Editor</span>
              </Link>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar