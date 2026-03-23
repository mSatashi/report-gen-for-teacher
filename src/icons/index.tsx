import React from "react";
import { logoITB } from "../data/images";

export const IconDashboard: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <rect x="2" y="2" width="9" height="9" rx="2" fill="currentColor" />
    <rect opacity="0.3" x="13" y="2" width="9" height="9" rx="2" fill="currentColor" />
    <rect opacity="0.3" x="13" y="13" width="9" height="9" rx="2" fill="currentColor" />
    <rect opacity="0.3" x="2" y="13" width="9" height="9" rx="2" fill="currentColor" />
  </svg>
);

export const IconDailyLog: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path d="M17.5 11H6.5C4 11 2 9 2 6.5C2 4 4 2 6.5 2H17.5C20 2 22 4 22 6.5C22 9 20 11 17.5 11ZM15 6.5C15 7.9 16.1 9 17.5 9C18.9 9 20 7.9 20 6.5C20 5.1 18.9 4 17.5 4C16.1 4 15 5.1 15 6.5Z" fill="currentColor" />
    <path opacity="0.3" d="M17.5 22H6.5C4 22 2 20 2 17.5C2 15 4 13 6.5 13H17.5C20 13 22 15 22 17.5C22 20 20 22 17.5 22ZM4 17.5C4 18.9 5.1 20 6.5 20C7.9 20 9 18.9 9 17.5C9 16.1 7.9 15 6.5 15C5.1 15 4 16.1 4 17.5Z" fill="currentColor" />
  </svg>
);

export const IconCalendar: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 25 28" fill="none">
    <path d="M24.026 11.44H1.973c-.556.01-1.087.23-1.479.632-.392.401-.597.94-.593 1.488v7.56c-.012.945.162 1.883.514 2.76.352.877.874 1.675 1.536 2.35.662.674 1.45 1.21 2.32 1.578.87.368 1.805.56 2.75.565H17.999c1.886-.045 3.678-.832 4.988-2.19 1.31-1.357 2.033-3.176 2.011-5.063V12.52a1.556 1.556 0 00-.49-1.051 1.56 1.56 0 00-1.083-.43zM8.732 21.84a1.333 1.333 0 110-2.667 1.333 1.333 0 010 2.667zm0-4.253a1.333 1.333 0 110-2.667 1.333 1.333 0 010 2.667zm4.267 4.253a1.333 1.333 0 110-2.667 1.333 1.333 0 010 2.667zm0-4.253a1.333 1.333 0 110-2.667 1.333 1.333 0 010 2.667zm4.24 4.253a1.333 1.333 0 110-2.667 1.333 1.333 0 010 2.667zm0-4.253a1.333 1.333 0 110-2.667 1.333 1.333 0 010 2.667zM24.64 8.133a1.333 1.333 0 01-1.015 1.48H2.626a1.333 1.333 0 01-.333-2.613 1.64 1.64 0 01.333-.04c.772-1.81 2.22-3.268 4.133-3.853V1.627a.906.906 0 111.813 0V3.333h4.733V1.627a.908.908 0 111.814 0V3.333h4.227V1.627a.908.908 0 111.813 0v2.08c1.039.345 1.985.924 2.766 1.691.781.768 1.377 1.703 1.741 2.735z" fill="currentColor" />
  </svg>
);

export const IconReport: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path opacity="0.3" d="M19 22H5C4.4 22 4 21.6 4 21V3C4 2.4 4.4 2 5 2H14L20 8V21C20 21.6 19.6 22 19 22Z" fill="currentColor" />
    <path d="M10.4343 15.4343L9.25 14.25C8.836 13.836 8.164 13.836 7.75 14.25C7.336 14.664 7.336 15.336 7.75 15.75L10.293 18.293C10.683 18.683 11.317 18.683 11.707 18.293L16.25 13.75C16.664 13.336 16.664 12.664 16.25 12.25C15.836 11.836 15.164 11.836 14.75 12.25L11.566 15.434C11.253 15.747 10.747 15.747 10.434 15.434z" fill="currentColor" />
    <path d="M15 8H20L14 2V7C14 7.6 14.4 8 15 8Z" fill="currentColor" />
  </svg>
);

export const IconMenu: React.FC = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path d="M21 7H3C2.4 7 2 6.6 2 6V4C2 3.4 2.4 3 3 3H21C21.6 3 22 3.4 22 4V6C22 6.6 21.6 7 21 7Z" fill="currentColor" />
    <path opacity="0.3" d="M21 14H3C2.4 14 2 13.6 2 13V11C2 10.4 2.4 10 3 10H21C21.6 10 22 10.4 22 11V13C22 13.6 21.6 14 21 14ZM22 20V18C22 17.4 21.6 17 21 17H3C2.4 17 2 17.4 2 18V20C2 20.6 2.4 21 3 21H21C21.6 21 22 20.6 22 20Z" fill="currentColor" />
  </svg>
);

export const IconChevronLeft: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path opacity="0.5" d="M14.266 11.434L18.45 7.25a1.333 1.333 0 10-1.885-1.885l-5.543 5.543a1.333 1.333 0 000 1.885l5.543 5.543A1.333 1.333 0 1018.45 16.5l-4.184-4.184a.889.889 0 010-1.257z" fill="currentColor" />
    <path d="M8.266 11.434L12.45 7.25a1.333 1.333 0 10-1.885-1.885L5.022 10.908a1.333 1.333 0 000 1.885l5.543 5.543A1.333 1.333 0 1012.45 16.5L8.266 12.566a.889.889 0 010-1.257z" fill="currentColor" />
  </svg>
);

export const IconChevronRight: React.FC = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <path opacity="0.5" d="M9.734 11.434L5.55 7.25a1.333 1.333 0 111.885-1.885l5.543 5.543a1.333 1.333 0 010 1.885L7.435 18.336A1.333 1.333 0 115.55 16.45l4.184-4.184a.889.889 0 000-1.257z" fill="currentColor" />
    <path d="M15.734 11.434L11.55 7.25a1.333 1.333 0 111.885-1.885l5.543 5.543a1.333 1.333 0 010 1.885l-5.543 5.543A1.333 1.333 0 1111.55 16.45l4.184-4.184a.889.889 0 000-1.257z" fill="currentColor" />
  </svg>
);

export const IconStudents: React.FC = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path d="M16 7C16 9.2 14.2 11 12 11C9.8 11 8 9.2 8 7C8 4.8 9.8 3 12 3C14.2 3 16 4.8 16 7Z" fill="currentColor" />
    <path opacity="0.3" d="M12 14C8.7 14 6 15.8 6 18V21H18V18C18 15.8 15.3 14 12 14Z" fill="currentColor" />
  </svg>
);

export const IconLog: React.FC = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path opacity="0.3" d="M5 8.04999L11.8 11.95V19.85L5 15.85V8.04999Z" fill="currentColor" />
    <path d="M20.1 6.65L12.3 2.15C12 1.95 11.6 1.95 11.3 2.15L3.5 6.65C3.2 6.85 3 7.15 3 7.45V16.45C3 16.85 3.2 17.15 3.5 17.35L11.3 21.85C11.6 22.05 12 22.05 12.3 21.85L20.1 17.35C20.4 17.15 20.5 16.85 20.5 16.45V7.45C20.5 7.15 20.3 6.85 20.1 6.65Z" fill="currentColor" />
  </svg>
);

export const IconPlan: React.FC = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path opacity="0.3" d="M19 22H5C4.4 22 4 21.6 4 21V3C4 2.4 4.4 2 5 2H14L20 8V21C20 21.6 19.6 22 19 22Z" fill="currentColor" />
    <path d="M15 8H20L14 2V7C14 7.6 14.4 8 15 8Z" fill="currentColor" />
    <path d="M8 12H16V14H8V12ZM8 16H13V18H8V16Z" fill="currentColor" />
  </svg>
);

export const IconPending: React.FC = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path opacity="0.3" d="M21.4 8.35303L19.241 10.511C18.561 11.191 17.301 11.251 16.561 10.511L13.489 7.43903C12.749 6.69903 12.809 5.43903 13.489 4.75903L15.647 2.60103C14.028 2.21103 12.296 2.36403 10.747 3.08103C9.198 3.79803 7.92 5.03903 7.11 6.59803C6.29 8.15703 6.03 9.94903 6.37 11.681C6.19 11.961 6.03 12.261 5.87 12.571L3.43 17.341C2.75 18.691 3.32 20.361 4.67 21.041C6.02 21.721 7.69 21.151 8.37 19.801L10.81 15.031C11.12 14.431 11.27 13.761 11.25 13.081C13.61 13.341 16.01 12.491 17.67 10.831C18.61 9.89103 19.24 8.68303 19.46 7.37503L21.4 8.35303Z" fill="currentColor" />
    <path d="M16.45 8.97303C16.65 9.17303 17.05 9.17303 17.25 8.97303L19.9 6.32303C20.5 5.72303 20.5 4.72303 19.9 4.12303C19.3 3.52303 18.3 3.52303 17.7 4.12303L15.75 6.07303L14.85 5.17303C14.65 4.97303 14.25 4.97303 14.05 5.17303C13.45 5.77303 13.45 6.77303 14.05 7.37303L16.45 8.97303Z" fill="currentColor" />
  </svg>
);

/** Logo in sidebar & header */
export const LogoBadge: React.FC<{ size?: number }> = ({ size = 32 }) => (
  <img
    alt="Logo"
    src={logoITB}
    style={{
      height: size,
      width: "auto",
      flexShrink: 0,
      objectFit: "contain",
    }}
  />
);

