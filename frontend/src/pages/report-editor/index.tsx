import React, { useEffect, useState } from "react";
import { INITIAL_SECTIONS } from "./constants";
import type { ReportSection } from "./types";
import * as S from "./styles";
import type { ReportGeneratorResponse, SiswaResponse } from "../../service/payload";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import type { Toast } from "../../types";
import { useReport } from "./useReport";

import { generateReportPdf } from "./generatePdf";


export interface ReportData {
  id: string;
  murid_id: string;
  kelas_id: string;
  konten: string;
  tipe_laporan: string;
  status: string;
  pdf_path: string | null;
  tanggal: string;
  tanggal_dikirim: string | null;
  is_ai_generated: boolean;
  periode_mulai: string;
  periode_selesai: string;
  nama_siswa?: string;
  nama_kelas?: string;
  nama_mapel?: string;
}

interface ReportEditorProps {
  reportData: ReportGeneratorResponse;
  siswaId: string;
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
}

const capitalize = (s: string) =>
  s ? s.charAt(0).toUpperCase() + s.slice(1) : "—";

const isSelesai = (s: string) => ["selesai", "finalized", "sent"].includes(s);

const parseKonten = (konten: string): ReportSection[] => {
  if (!konten) return INITIAL_SECTIONS;
  return [{
    id: "konten",
    emoji: "📋",
    label: "Laporan Perkembangan",
    accentColor: "#3b82f6",
    content: konten,
  }];
};

interface SectionCardProps {
  section: ReportSection;
  onChange: (id: string, value: string) => void;
  onSave: (id: string, value: string) => void;
  done: boolean;
  reportData: ReportGeneratorResponse;
}

const SectionCard: React.FC<SectionCardProps> = ({ section: s, onChange, onSave, done, reportData }) => {
  const [focused, setFocused] = useState(false);
  const [localValue, setLocalValue] = useState(s.content);
  
  return (
    <div style={S.sectionCard(s.accentColor, focused)}>
      <div style={S.sectionLabelRow}>
        <span style={S.sectionEmoji}>{s.emoji}</span>
        <span style={S.sectionLabel(s.accentColor)}>{s.label}</span>
      </div>

      {reportData?.status === 'final' ? (
        <div
          onFocus={() => setFocused(true)}
          onBlur={(e) => {
            setFocused(false);
            const v = e.currentTarget.innerText;
            setLocalValue(v);
            onChange(s.id, v);
          }}
          onInput={(e) => setLocalValue(e.currentTarget.textContent ?? "")}
          style={S.editableContent(s.accentColor, focused)}
        >
          {s.content}
        </div>
      ): (
        <div
          contentEditable
          suppressContentEditableWarning
          onFocus={() => setFocused(true)}
          onBlur={(e) => {
            setFocused(false);
            const v = e.currentTarget.innerText;
            setLocalValue(v);
            onChange(s.id, v);
          }}
          onInput={(e) => setLocalValue(e.currentTarget.textContent ?? "")}
          style={S.editableContent(s.accentColor, focused)}
        >
          {s.content}
        </div>
      )}


      {!done && reportData?.status !== 'final' && (
        <div style={S.sectionFooter}>
          <button style={S.btnSave} onClick={() => onSave(s.id, localValue)}>
            💾 Simpan
          </button>
        </div>
      )}
    </div>
  );
};

const FinalizeModal: React.FC<{ onConfirm: () => void; onCancel: () => void }> = ({
  onConfirm, onCancel,
}) => (
  <div style={S.modalOverlay} onClick={onCancel}>
    <div style={S.modalBox} onClick={(e) => e.stopPropagation()}>
      <div style={S.modalIcon}>📄</div>
      <h3 style={S.modalTitle}>Finalisasi Laporan?</h3>
      <p style={S.modalBody}>
        Yakin ingin memfinalisasi dan mengirim laporan ini?<br />
        Tindakan ini tidak dapat dibatalkan.
      </p>
      <div style={S.modalActions}>
        <button onClick={onCancel} style={S.btnOutline}>Batal</button>
        <button onClick={onConfirm} style={S.btnPrimary}>Ya, Finalisasi</button>
      </div>
    </div>
  </div>
);

let toastId = 0;

const ReportEditor: React.FC<ReportEditorProps> = ({ reportData, onNavigate }) => {
  const [sections, setSections] = useState<ReportSection[]>(() =>
    reportData ? parseKonten(reportData.konten) : INITIAL_SECTIONS
  );
  const [showModal, setShowModal] = useState(false);
  const [status, setStatus] = useState(reportData?.status ?? "draft");
  const [sending, setSending] = useState(false);
  const [siswaList, setSiswaList] = useState<SiswaResponse[]>([]);
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null);

  const { loadSiswa } = useSiswaApi();
  const { errorMsg, submitUpdateReportSiswa, submitUpdateStatusReport } = useReport();

  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const done = isSelesai(status);

  const handleChange = (id: string, value: string) => {
    setSections((prev) => prev.map((s) => (s.id === id ? { ...s, content: value } : s)));
  };

  const handleSave = async (value: string) => {
    try {
      await submitUpdateReportSiswa(reportData?.id, value);
      showToast("Report berhasil diperbarui", "success");
    } catch {
      showToast(errorMsg ?? "Gagal memperbarui report", "error");
    }
  };
  
  useEffect(() => {
    loadSiswa().then((data) => {
      if (data.length) setSiswaList(data);
    });
  }, []);

  const siswa = siswaList.find((m) => m.id === reportData?.murid_id) ?? null;

  const handleFinalize = async () => {
    try {
      const status = await submitUpdateStatusReport(reportData?.id); // ✅ pakai value dari section
      console.log('status edit: ', status);
      showToast("Report berhasil diperbarui", "success");
      setShowModal(false);
      setSending(false);
      setStatus("selesai");
    } catch {
      showToast(errorMsg ?? "Gagal memperbarui report", "error");
      setShowModal(false);
    }
  };

  const getCurrentKonten = () =>
    sections.find((s) => s.id === "konten")?.content ?? reportData?.konten ?? "";

  const handleDownloadPdf = () => {
    const doc = generateReportPdf(reportData, siswa?.nama ?? "-", getCurrentKonten());
    doc.save(`laporan-${siswa?.nama ?? "siswa"}-${reportData?.tanggal?.split("T")[0]}.pdf`);
  };

  const handlePreviewPdf = () => {
    const doc = generateReportPdf(reportData, siswa?.nama ?? "-", getCurrentKonten());
    const url = doc.output("bloburl") as unknown as string;
    setPdfPreviewUrl(url);
  };

  return (
    <>
      {showModal && (
        <FinalizeModal onConfirm={handleFinalize} onCancel={() => setShowModal(false)} />
      )}

      <div style={S.pageWrapper}>
        <div style={S.scrollArea} className="scroll-area">

          {/* ── Header ── */}
          <div style={S.pageHeader}>
            <h2 style={S.pageTitle}>Report Editor</h2>

            <div style={S.headerActions}>
              {/* Preview PDF + Download PDF + badge — hanya jika selesai */}
              {done && (
                <>
                  <button style={S.btnOutline} onClick={handlePreviewPdf}>👁 Preview PDF</button>
                  <button style={S.btnOutline} onClick={handleDownloadPdf}>⬇ Download PDF</button>
                  <span style={S.badgeSelesaiHeader}>✅ Laporan Selesai</span>
                </>
              )}

              {reportData?.status === 'final' && (
                <>
                  <button style={S.btnOutline} onClick={handlePreviewPdf}>👁 Preview PDF</button>
                  <button style={S.btnOutline} onClick={handleDownloadPdf}>⬇ Download PDF</button>
                </>
              )}

              {/* Finalisasi — hanya jika belum selesai */}
              {!done && reportData?.status !== 'final' && (
                <button
                  disabled={sending}
                  onClick={() => setShowModal(true)}
                  style={sending ? S.btnPrimarySending : S.btnPrimary}
                >
                  {sending ? <><span style={S.spinner} /> Mengirim...</> : "Finalisasi"}
                </button>
              )}

              <button
                onClick={() => onNavigate?.("detailReport", { siswaId:reportData.murid_id })}
                style={{ background: "none", border: "1px solid #e5e7eb", borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}
              >
                ← Kembali
              </button>
            </div>
          </div>

          {/* ── Info card — selalu tampil menggunakan activeData ── */}
          {/* <StudentInfoCard r={activeData} status={status} /> */}
          <div style={S.infoCard}>
      <div style={S.infoCardHeader}>
        <span style={{ fontSize: 14 }}>🗂️</span>
        <span style={S.infoCardHeaderTitle}>Detail Peserta</span>
        <span style={S.infoCardStatusBadge}>
          {isSelesai(status) ? "✅ Final" : "⏳ " + capitalize(status)}
        </span>
      </div>

      <div style={S.infoCardDivider} />
        <div style={S.infoCardBodyRow}>
          <div style={S.infoGroup}>
            <span style={S.infoLabel}>Nama Siswa</span>
            <span style={S.infoValue}>{siswa?.nama ?? '-'}</span>
          </div>

          <div style={S.infoGroup}>
            <span style={S.infoLabel}>Tanggal</span>
            <span style={S.infoValue}>
                {reportData?.tanggal
                ? new Date(reportData.tanggal).toLocaleDateString("id-ID", {
                    day: "2-digit",
                    month: "long",
                    year: "numeric",
                  })
                : "-"}
              </span>
          </div>

          <div style={S.infoGroup}>
            <span style={S.infoLabel}>Type Laporan</span>
            <span style={S.infoValue}>{reportData?.tipe_laporan ?? '-'}</span>
          </div>

          <div style={S.infoGroup}>
            <span style={S.infoLabel}>Status</span>
            <span style={S.badgeStatus(status)}>
              {isSelesai(status) ? "Selesai" : capitalize(status)}
            </span>
          </div>
        </div>
      </div>

          {/* ── Banner ── */}
          {!done && reportData?.status !== 'final' && (
            <div style={S.aiBanner}>
              ✦ Draft ini digenerate AI dari log belajar siswa. Edit konten lalu klik <strong>Simpan</strong> sebelum finalisasi.
            </div>
          )}
          {reportData?.status === 'final' && (
            <div style={S.aiBanner}>
              ✦ Draft ini digenerate AI dari log belajar siswa.
            </div>
          )}
          {done && (
            <div style={S.finalizedBanner}>
              ✓ Laporan telah berhasil difinalisasi dan dikirim.
            </div>
          )}

          {/* ── Section cards ── */}
          <div style={S.sectionGrid}>
            {sections.map((s) => (
              <SectionCard
                key={s.id}
                section={s}
                onChange={handleChange}
                onSave={handleSave}
                done={done} 
                reportData={reportData}
              />
            ))}
          </div>

        </div>
      </div>

      <style>{S.globalStyles}</style>

      <div
        style={{
          position: "fixed",
          right: 24,
          bottom: 24,
          display: "flex",
          flexDirection: "column",
          gap: 10,
          zIndex: 1200,
        }}
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            style={{
              minWidth: 240,
              maxWidth: 320,
              padding: "12px 14px",
              borderRadius: "12px",
              color: "#fff",
              fontSize: "13px",
              fontWeight: 600,
              boxShadow: "0 10px 30px rgba(15,22,36,0.18)",
              background: toast.type === "success" ? "#22C55E" : "#EF4444",
            }}
          >
            {toast.message}
          </div>
        ))}
      </div>

      {pdfPreviewUrl && (
        <div
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)",
            zIndex: 200, display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center", gap: 12,
          }}
          onClick={() => setPdfPreviewUrl(null)}
        >
          <div style={{ display: "flex", gap: 10 }}>
            <button
              onClick={(e) => { e.stopPropagation(); setPdfPreviewUrl(null); }}
              style={{ ...S.btnOutline, background: "#fff" }}
            >
              ✕ Tutup
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); handleDownloadPdf(); }}
              style={{ ...S.btnPrimary }}
            >
              ⬇ Download
            </button>
          </div>
          <iframe
            src={pdfPreviewUrl}
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "min(900px, 95vw)",
              height: "85vh",
              border: "none",
              borderRadius: 10,
              boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
            }}
          />
        </div>
      )}
    </>
  );
};

export default ReportEditor;