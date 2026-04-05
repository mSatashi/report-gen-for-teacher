import Header from '../components/header'
import Sidebar from '../components/sidebar'
// import Header from '../components/Header'
// import Toolbar from '../components/Toolbar'
// import Footer from '../components/Footer'
// import Notification from '../components/Notification'

type Props = {
  children: React.ReactNode
}

function MainLayout({ children }: Props) {
  return (
    <div
      id="kt_body"
      className="header-fixed header-tablet-and-mobile-fixed toolbar-enabled toolbar-fixed aside-enabled aside-fixed"
      style={{
        ['--kt-toolbar-height' as any]: '55px',
        ['--kt-toolbar-height-tablet-and-mobile' as any]: '55px',
      }}
      data-kt-aside-minimize="off"
    >
      {/* Root */}
      <div className="d-flex flex-column flex-root">
        <div className="page d-flex flex-row flex-column-fluid">

          {/* Sidebar */}
          <Sidebar
            activeRoute="home"
            collapsed={false}
            onNavigate={() => {}}
            onToggleCollapse={() => {}}
          />

          {/* Wrapper */}
          <div className="wrapper d-flex flex-column flex-row-fluid" id="kt_wrapper">

            {/* Header */}
            <Header onOpenMobileMenu={() => {}} />

            {/* Content */}
            <div className="content d-flex flex-column flex-column-fluid" id="kt_content">

              {/* Toolbar */}
              <div className="toolbar" id="kt_toolbar">
                {/* <Toolbar /> */}
              </div>

              {/* Post */}
              <div className="post d-flex flex-column-fluid" id="kt_post">
                <div id="kt_content_container" className="container-xxl">

                  {/* Notification */}
                  {/* <Notification /> */}

                  {/* 🔥 INI PENGGANTI @yield('content') */}
                  {children}

                </div>
              </div>
            </div>

            {/* Footer */}
            {/* <Footer /> */}

          </div>
        </div>
      </div>
    </div>
  )
}

export default MainLayout