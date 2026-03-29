import React from "react";

const Header: React.FC = () => {
  return (
    <div id="kt_header" className="header align-items-stretch">
      <div className="container-fluid d-flex align-items-stretch justify-content-between">
        
        {/* Mobile toggle */}
        <div className="d-flex align-items-center d-lg-none ms-n2 me-2">
          <div
            className="btn btn-icon btn-active-light-primary w-30px h-30px w-md-40px h-md-40px"
            id="kt_aside_mobile_toggle"
          >
            <span className="svg-icon svg-icon-1">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M21 7H3C2.4 7 2 6.6 2 6V4C2 3.4 2.4 3 3 3H21C21.6 3 22 3.4 22 4V6C22 6.6 21.6 7 21 7Z"
                  fill="currentColor"
                />
                <path
                  opacity="0.3"
                  d="M21 14H3C2.4 14 2 13.6 2 13V11C2 10.4 2.4 10 3 10H21C21.6 10 22 10.4 22 11V13C22 13.6 21.6 14 21 14Z"
                  fill="currentColor"
                />
              </svg>
            </span>
          </div>
        </div>

        {/* Logo */}
        <div className="d-flex align-items-center flex-grow-1 flex-lg-grow-0">
          <a href="#" className="d-lg-none">
            <img
              alt="Logo"
              src="/images/logo_itb_512.png"
              className="h-30px"
            />
          </a>
        </div>

        {/* Right side */}
        <div className="d-flex align-items-stretch justify-content-between flex-lg-grow-1">
          
          {/* Navbar kosong */}
          <div className="d-flex align-items-stretch" id="kt_header_nav"></div>

          {/* User Menu */}
          <div className="d-flex align-items-stretch flex-shrink-0">
            <div
              className="d-flex align-items-center ms-1 ms-lg-3"
              id="kt_header_user_menu_toggle"
            >
              
              {/* Avatar */}
              <div
                className="cursor-pointer symbol symbol-30px symbol-md-40px"
                data-kt-menu-trigger="click"
              >
                <img src="/images/logo_itb_512.png" alt="user" />
              </div>

              {/* Dropdown */}
              <div className="menu menu-sub menu-sub-dropdown menu-column menu-rounded py-4 fs-6 w-275px">
                
                <div className="menu-item px-3">
                  <div className="menu-content d-flex align-items-center px-3">
                    <div className="symbol symbol-50px me-5">
                      <img src="/images/logo_itb_512.png" alt="Logo" />
                    </div>

                    <div className="d-flex flex-column">
                      <div className="fw-bolder fs-5">
                        Nama Lengkap
                      </div>
                      <span className="fw-bold text-muted fs-7">
                        email@gmail.com
                      </span>
                    </div>
                  </div>
                </div>

                <div className="separator my-2"></div>

                <div className="menu-item px-5">
                  <a href="#" className="menu-link px-5">
                    Sign Out
                  </a>
                </div>

                <div className="menu-item px-5">
                  <a href="#" className="menu-link px-5">
                    Sign Out SSO
                  </a>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Header;