import React, { useState } from "react";
import { loginStyles } from "./styles";

interface LoginPageProps {
  onLogin?: (data: { email: string; password: string; captchaAnswer: string }) => void;
  error?: string;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLogin, error }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [focused, setFocused] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    onLogin?.({ email, password, captchaAnswer: "" });
  };

  return (
    <>
      <style>{loginStyles}</style>

      <div className="lr-root">
        <div className="lr-bg" />
        <div className="lr-grid" />
        <div className="lr-orb lr-orb-1" />
        <div className="lr-orb lr-orb-2" />
        <div className="lr-orb lr-orb-3" />

        {/* ── Left branding ── */}
        <div className="lr-left">
          {/* Hero */}
          <div className="lr-hero">
            <div className="lr-eyebrow">
              <span className="lr-eyebrow-dot" />
              Automatic Report
            </div>
            <h1 className="lr-headline">
              Laporan <em>cerdas</em><br />untuk pendidikan<br />yang lebih baik
            </h1>
            <p className="lr-desc">
              Platform pelaporan otomatis berbasis AI untuk memantau perkembangan siswa secara efisien dan terstruktur.
            </p>
            <div className="lr-tags">
              {["Daily Log", "Learning Plan", "Progress Siswa", "Report Editor", "AI Otomatis"].map((t) => (
                <span key={t} className="lr-tag">{t}</span>
              ))}
            </div>
          </div>

          <div className="lr-footer-text">
            © {new Date().getFullYear()} Kelompok Minion — IF5200 Proyek Penelitian Terapan
          </div>
        </div>

        {/* ── Right form ── */}
        <div className="lr-right">
          <div className="lr-card">

            <div className="lr-card-title">Selamat datang</div>
            <div className="lr-card-sub">
              Masuk ke dashboard untuk mulai mengelola laporan siswa Anda.
            </div>

            {/* Error */}
            {error && (
              <div className="lr-error">
                <span>⚠</span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit}>

              {/* Email */}
              <div className="lr-field">
                <label className="lr-label">Email</label>
                <div className="lr-input-wrap">
                  <input
                    type="email"
                    className="lr-input"
                    placeholder="nama@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={() => setFocused("email")}
                    onBlur={() => setFocused(null)}
                    required
                    autoComplete="email"
                  />
                </div>
              </div>

              {/* Password */}
              <div className="lr-field">
                <label className="lr-label">Password</label>
                <div className="lr-input-wrap">
                  <input
                    type={showPassword ? "text" : "password"}
                    className="lr-input lr-input-pw"
                    placeholder="Masukkan password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onFocus={() => setFocused("password")}
                    onBlur={() => setFocused(null)}
                    required
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="lr-pw-toggle"
                    onClick={() => setShowPassword((v) => !v)}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      /* eye-off */
                      <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                        <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                        <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    ) : (
                      /* eye */
                      <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Submit */}
              <button type="submit" className="lr-btn" disabled={loading}>
                {loading && <span className="lr-spinner" />}
                {loading ? "Memproses..." : "Masuk"}
              </button>

            </form>

            <div className="lr-card-footer">
              Automatic Report &nbsp;·&nbsp; Version 0.1.0
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginPage;