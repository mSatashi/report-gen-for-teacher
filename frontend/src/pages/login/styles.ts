
export const loginStyles = `
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Serif+Display:ital@0;1&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        /* Reset paksa untuk halaman login */
        html, body, #root {
          margin: 0 !important;
          padding: 0 !important;
          overflow: hidden !important;
        }

        .lr-root {
          min-height: 100vh;
          min-height: 100dvh;
          width: 100%;
          display: flex;
          font-family: 'DM Sans', sans-serif;
          background: #0a0f1e;
          position: fixed;
          inset: 0;
          overflow: hidden;
        }

        /* ── Background mesh ── */
        .lr-bg {
          position: absolute; inset: 0; z-index: 0;
          background:
            radial-gradient(ellipse 80% 60% at 20% 10%, rgba(37,99,235,.18) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 80% 90%, rgba(99,102,241,.14) 0%, transparent 55%),
            radial-gradient(ellipse 40% 40% at 60% 40%, rgba(14,165,233,.08) 0%, transparent 50%);
        }

        /* subtle grid */
        .lr-grid {
          position: absolute; inset: 0; z-index: 0;
          background-image:
            linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
          background-size: 48px 48px;
        }

        /* floating orbs */
        .lr-orb {
          position: absolute; border-radius: 50%;
          filter: blur(72px); z-index: 0; pointer-events: none;
        }
        .lr-orb-1 {
          width: 420px; height: 420px;
          top: -120px; left: -80px;
          background: rgba(37,99,235,.22);
          animation: orbFloat1 12s ease-in-out infinite;
        }
        .lr-orb-2 {
          width: 320px; height: 320px;
          bottom: -60px; right: -60px;
          background: rgba(99,102,241,.18);
          animation: orbFloat2 15s ease-in-out infinite;
        }
        .lr-orb-3 {
          width: 180px; height: 180px;
          top: 55%; left: 60%;
          background: rgba(14,165,233,.12);
          animation: orbFloat3 10s ease-in-out infinite;
        }

        @keyframes orbFloat1 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50%       { transform: translate(30px, 40px) scale(1.06); }
        }
        @keyframes orbFloat2 {
          0%, 100% { transform: translate(0, 0) scale(1); }
          50%       { transform: translate(-20px, -30px) scale(1.04); }
        }
        @keyframes orbFloat3 {
          0%, 100% { transform: translate(0, 0); }
          50%       { transform: translate(-15px, 20px); }
        }

        /* ── Left branding panel ── */
        .lr-left {
          display: none;
          flex: 1;
          position: relative;
          z-index: 1;
          flex-direction: column;
          justify-content: space-between;
          padding: 52px 56px;
          width: 50%;
        }
        @media (min-width: 1024px) { .lr-left { display: flex; } }

        .lr-hero {
          flex: 1;
          display: flex; flex-direction: column;
          justify-content: center;
        }
        .lr-eyebrow {
          display: inline-flex; align-items: center; gap: 8px;
          background: rgba(37,99,235,.2);
          border: 1px solid rgba(37,99,235,.35);
          border-radius: 999px;
          padding: 5px 14px;
          font-size: 11px; font-weight: 600;
          color: #93c5fd; letter-spacing: .08em; text-transform: uppercase;
          margin-bottom: 24px; width: fit-content;
        }
        .lr-eyebrow-dot {
          width: 6px; height: 6px; border-radius: 50%;
          background: #3b82f6;
          animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50%       { opacity: .5; transform: scale(.8); }
        }

        .lr-headline {
          font-family: 'DM Serif Display', serif;
          font-size: clamp(36px, 4vw, 54px);
          line-height: 1.1; color: #fff;
          letter-spacing: -.5px;
          margin-bottom: 20px;
        }
        .lr-headline em {
          font-style: italic;
          background: linear-gradient(135deg, #60a5fa, #818cf8);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .lr-desc {
          font-size: 15px; color: rgba(255,255,255,.45);
          line-height: 1.75; max-width: 360px;
          font-weight: 300;
        }

        .lr-tags {
          display: flex; flex-wrap: wrap; gap: 8px; margin-top: 36px;
        }
        .lr-tag {
          padding: 6px 14px; border-radius: 999px;
          border: 1px solid rgba(255,255,255,.1);
          font-size: 12px; color: rgba(255,255,255,.55); font-weight: 500;
          background: rgba(255,255,255,.04);
          transition: border-color .2s, color .2s;
        }
        .lr-tag:hover {
          border-color: rgba(96,165,250,.4);
          color: #93c5fd;
        }

        .lr-footer-text {
          font-size: 12px; color: rgba(255,255,255,.2);
        }

        /* ── Right form panel ── */
        .lr-right {
          position: relative; z-index: 1;
          width: 100%;
          display: flex; align-items: center; justify-content: center;
          padding: 32px 24px;
        }
        @media (min-width: 1024px) {
          .lr-right {
            width: 50%; min-width: 50%; flex-shrink: 0;
            border-left: 1px solid rgba(255,255,255,.06);
            background: rgba(255,255,255,.02);
            backdrop-filter: blur(24px);
          }
        }

        /* ── Form card ── */
        .lr-card {
          width: 100%; max-width: 400px;
          animation: slideUp .5s cubic-bezier(.22,.68,0,1.2) both;
        }
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(24px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .lr-card-title {
          font-family: 'DM Serif Display', serif;
          font-size: 32px; color: #fff;
          letter-spacing: -.3px; margin-bottom: 8px;
          line-height: 1.15;
        }
        .lr-card-sub {
          font-size: 14px; color: rgba(255,255,255,.4);
          margin-bottom: 36px; font-weight: 300; line-height: 1.6;
        }

        /* ── Error banner ── */
        .lr-error {
          display: flex; gap: 10px; align-items: flex-start;
          background: rgba(239,68,68,.1);
          border: 1px solid rgba(239,68,68,.25);
          border-radius: 10px; padding: 12px 16px;
          font-size: 13px; color: #fca5a5;
          margin-bottom: 20px; line-height: 1.5;
        }

        /* ── Form fields ── */
        .lr-field { margin-bottom: 20px; }

        .lr-label {
          display: block;
          font-size: 12px; font-weight: 600;
          color: rgba(255,255,255,.5);
          margin-bottom: 8px;
          letter-spacing: .06em; text-transform: uppercase;
        }

        .lr-input-wrap { position: relative; }

        .lr-input {
          width: 100%; padding: 14px 16px;
          border-radius: 12px;
          border: 1.5px solid rgba(255,255,255,.08);
          background: rgba(255,255,255,.05);
          color: #fff; font-size: 14px;
          font-family: 'DM Sans', sans-serif;
          outline: none;
          transition: border-color .2s, background .2s, box-shadow .2s;
        }
        .lr-input::placeholder { color: rgba(255,255,255,.2); }
        .lr-input:focus {
          border-color: rgba(59,130,246,.6);
          background: rgba(59,130,246,.06);
          box-shadow: 0 0 0 3px rgba(59,130,246,.1);
        }
        .lr-input-pw { padding-right: 56px; }

        .lr-pw-toggle {
          position: absolute; right: 14px; top: 50%;
          transform: translateY(-50%);
          background: none; border: none; cursor: pointer;
          color: rgba(255,255,255,.3); padding: 4px;
          display: flex; align-items: center;
          transition: color .2s;
        }
        .lr-pw-toggle:hover { color: rgba(255,255,255,.7); }

        /* ── Submit button ── */
        .lr-btn {
          width: 100%; padding: 14px;
          border-radius: 12px; border: none;
          background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
          color: #fff; font-size: 15px; font-weight: 600;
          font-family: 'DM Sans', sans-serif;
          cursor: pointer; letter-spacing: .02em;
          transition: opacity .2s, transform .15s, box-shadow .2s;
          box-shadow: 0 4px 20px rgba(37,99,235,.35);
          margin-top: 8px;
          position: relative; overflow: hidden;
        }
        .lr-btn::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(135deg, rgba(255,255,255,.12) 0%, transparent 60%);
          pointer-events: none;
        }
        .lr-btn:hover:not(:disabled) {
          opacity: .92; transform: translateY(-1px);
          box-shadow: 0 8px 28px rgba(37,99,235,.45);
        }
        .lr-btn:active:not(:disabled) { transform: translateY(0); }
        .lr-btn:disabled { opacity: .5; cursor: not-allowed; }

        /* loading spinner */
        .lr-spinner {
          display: inline-block;
          width: 16px; height: 16px;
          border: 2px solid rgba(255,255,255,.3);
          border-top-color: #fff;
          border-radius: 50%;
          animation: spin .7s linear infinite;
          vertical-align: middle; margin-right: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        .lr-card-footer {
          margin-top: 28px; text-align: center;
          font-size: 12px; color: rgba(255,255,255,.2);
        }

        /* ── Mobile: dark overlay behind form ── */
        @media (max-width: 1023px) {
          .lr-right {
            background: rgba(10,15,30,.85);
            backdrop-filter: blur(20px);
          }
        }
      `;
