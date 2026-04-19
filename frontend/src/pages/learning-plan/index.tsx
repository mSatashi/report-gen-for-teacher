import React, { useState, useCallback, useEffect } from "react";
import type { GenerateplanResponse, KelasResponse } from "../../service/payload";
import PlanDetail from "./plan-detail";
import { useLearningPlan } from "./useLearningPlan";
import type { Kelas } from "../../types";
import { useKelasApi } from "../master-kelas/useKelasApi";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function thStyle(align: "left" | "center" | "right", width?: number): React.CSSProperties {
  return {
    padding: "11px 16px",
    fontSize: 12,
    fontWeight: 700,
    color: "#6b7280",
    textAlign: align,
    width,
    letterSpacing: 0.3,
    textTransform: "uppercase",
  };
}

// ─── Spinner ──────────────────────────────────────────────────────────────────

const Spinner: React.FC<{ color?: string }> = ({ color = "#fff" }) => (
  <>
    <style>{`@keyframes _spin { to { transform: rotate(360deg); } }`}</style>
    <span style={{
      display: "inline-block", width: 12, height: 12, flexShrink: 0,
      border: `2px solid ${color}44`, borderTopColor: color,
      borderRadius: "50%", animation: "_spin 0.7s linear infinite",
    }} />
  </>
);

// ─── Per-row state ────────────────────────────────────────────────────────────

type RowStatus = "idle" | "loading" | "done" | "error";

interface RowState {
  status: RowStatus;
  result: GenerateplanResponse | null;
  errorMsg: string | null;
}

const DEFAULT_ROW: RowState = { status: "idle", result: null, errorMsg: null };

// ─── Mapper ───────────────────────────────────────────────────────────────────

const mapApiToKelas = (data: KelasResponse): Kelas => ({
  id: data.id,
  nama: data.nama,
  mata_pelajaran: data.mata_pelajaran,
  pengajar_id: data.pengajar_id,
  kredit: data.kredit,
  jadwal: data.jadwal,
  created_at: data.created_at,
  siswa: [],
});

const mapApiToPlan = (data: GenerateplanResponse): GenerateplanResponse => ({
  id: data.id,
  kelas_id: data.kelas_id,
  murid_id: data.murid_id,
  waktu: data.waktu,
  daftar_rekomendasi_material: data.daftar_rekomendasi_material,
  estimasi_waktu_selesai: data.estimasi_waktu_selesai,
  catatan_analisa: data.catatan_analisa,
  jadwal_mingguan: data.jadwal_mingguan,
  version: data.version,
});

// ─── Main page ────────────────────────────────────────────────────────────────

const PlanList: React.FC = () => {
  const [kelasList, setKelasList] = useState<Kelas[]>([]);
  const [planList, setPlanList] = useState<GenerateplanResponse[]>([]);
  const [isLoadingKelas, setIsLoadingKelas] = useState(true);

  // rows keyed by kelas.id — diinisialisasi dinamis saat data masuk
  const [rows, setRows] = useState<Record<string, RowState>>({});

  // kelas yang sedang dilihat detail plan-nya
  const [viewingKelas, setViewingKelas] = useState<Kelas | null>(null);

  const { submitGeneratePlan, loadPlan } = useLearningPlan();
  const { loadKelas } = useKelasApi();

  useEffect(() => {
    const init = async () => {
      try {
        const kelasData = await loadKelas();

        const mappedKelas = kelasData.map(mapApiToKelas);
        setKelasList(mappedKelas);

        const planResults = await Promise.all(
          mappedKelas.map(async (kelas) => {
            const plans = await loadPlan(kelas.id);
            return {
              kelasId: kelas.id,
              plans
            };
          })
        );

        const rowMap: Record<string, RowState> =
          Object.fromEntries(
            planResults.map(item => [
              item.kelasId,
              item.plans.length
                ? {
                    status:"done",
                    result:item.plans[0],
                    errorMsg:null
                  }
                : DEFAULT_ROW
            ])
          );

        setRows(rowMap);
      } catch(err) {
        console.error("ERROR INIT:", err);
      } finally {
        setIsLoadingKelas(false);
      }
    };

    init();

  }, []);

  // ── Generate plan untuk satu kelas ──
  const handleGenerate = useCallback(async (kelas: Kelas) => {
    setRows((prev) => ({
      ...prev,
      [kelas.id]: { status: "loading", result: null, errorMsg: null },
    }));

    const result = await submitGeneratePlan(kelas.id);

    if (result) {
      setRows((prev) => ({
        ...prev,
        [kelas.id]: { status: "done", result, errorMsg: null },
      }));
    } else {
      setRows((prev) => ({
        ...prev,
        [kelas.id]: { status: "error", result: null, errorMsg: "Gagal generate plan. Coba lagi." },
      }));
    }
  }, [submitGeneratePlan]);

  // ── Detail view ──
  if (viewingKelas) {
    const row = rows[viewingKelas.id];
    return (
      <PlanDetail
        kelas={viewingKelas}
        plan={row?.result ?? null}
        onBack={() => setViewingKelas(null)}
      />
    );
  }

  const doneCount = Object.values(rows).filter((r) => r.status === "done").length;
  const totalCount = kelasList.length;

  console.log(doneCount);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 18 }}>

      {/* Header */}
      <div style={{ flexShrink: 0 }}>
        <h2 style={{ fontSize: 26, fontWeight: 800, color: "#111827", margin: "0 0 4px" }}>
          Mata Pelajaran
        </h2>
        <p style={{ fontSize: 13, color: "#9ca3af", margin: 0 }}>
          Generate learning plan adaptif per mata pelajaran · AI-powered
        </p>
      </div>

      {/* Progress banner — hanya muncul jika ada yang sudah done */}
      {doneCount > 0 && totalCount > 0 && (
        <div style={{
          background: "#f0fdf4", border: "1.5px solid #86efac", borderRadius: 10,
          padding: "11px 16px", fontSize: 13, color: "#166534", fontWeight: 500,
          flexShrink: 0, display: "flex", alignItems: "center", gap: 10,
        }}>
          <span>✓</span>
          <span>{doneCount} dari {totalCount} kelas sudah memiliki learning plan.</span>
          <div style={{ flex: 1, background: "#bbf7d0", borderRadius: 99, height: 5, marginLeft: 4 }}>
            <div style={{
              width: `${Math.round((doneCount / totalCount) * 100)}%`,
              background: "#16a34a", borderRadius: 99, height: "100%", transition: "width .4s",
            }} />
          </div>
          <span style={{ fontSize: 12, fontWeight: 700 }}>
            {Math.round((doneCount / totalCount) * 100)}%
          </span>
        </div>
      )}

      {/* Table */}
      <div style={{
        background: "#fff", borderRadius: 14,
        border: "1px solid #e5e7eb", overflow: "hidden", flexShrink: 0,
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <colgroup>
            <col style={{ width: 56 }} />
            <col />
            <col style={{ width: 310 }} />
            <col style={{ width: 230 }} />
          </colgroup>
          <thead>
            <tr style={{ background: "#f9fafb", borderBottom: "1px solid #e5e7eb" }}>
              <th style={thStyle("center")}>No</th>
              <th style={thStyle("left")}>Mata Pelajaran</th>
              <th style={thStyle("left")}>Status Generate Plan</th>
              <th style={thStyle("right")}>Aksi</th>
            </tr>
          </thead>
          <tbody>
            {/* Loading state saat fetch kelas */}
            {isLoadingKelas && (
              <tr>
                <td colSpan={4} style={{ padding: "40px 16px", textAlign: "center" }}>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 13, color: "#9ca3af" }}>
                    <Spinner color="#9ca3af" />
                    Memuat daftar kelas…
                  </span>
                </td>
              </tr>
            )}

            {/* Empty state */}
            {!isLoadingKelas && kelasList.length === 0 && (
              <tr>
                <td colSpan={4} style={{ padding: "40px 16px", textAlign: "center", fontSize: 13, color: "#9ca3af" }}>
                  Belum ada kelas terdaftar.
                </td>
              </tr>
            )}

            {/* Data rows */}
            {!isLoadingKelas && kelasList.map((kelas, idx) => {
              // Ambil row state, fallback ke DEFAULT_ROW agar tidak crash
              const row: RowState = rows[kelas.id] ?? DEFAULT_ROW;
              const isLoading = row.status === "loading";
              const isDone = row.status === "done";
              const isError = row.status === "error";
              const result = row.result;

              return (
                <tr
                  key={kelas.id}
                  style={{ borderTop: "1px solid #f3f4f6", transition: "background .1s" }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "#fafafa")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                >
                  {/* No */}
                  <td style={{ padding: "15px 16px", fontSize: 13, color: "#9ca3af", textAlign: "center", fontWeight: 600 }}>
                    {idx + 1}
                  </td>

                  {/* Mata Pelajaran */}
                  <td style={{ padding: "15px 16px 15px 0" }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: "#111827" }}>
                      {kelas.mata_pelajaran}
                    </div>
                    <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 2 }}>
                      {kelas.nama} · {kelas.jadwal}
                    </div>
                  </td>

                  {/* Status Generate Plan */}
                  <td style={{ padding: "15px 16px 15px 0" }}>
                    {row.status === "idle" && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: "#9ca3af", fontWeight: 500 }}>
                        <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "#d1d5db" }} />
                        Belum digenerate
                      </span>
                    )}

                    {isLoading && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 7, fontSize: 13, color: "#2563eb", fontWeight: 500 }}>
                        <Spinner color="#2563eb" />
                        Sedang digenerate…
                      </span>
                    )}

                    {isError && (
                      <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13, color: "#b91c1c", fontWeight: 500 }}>
                        ✕ {row.errorMsg}
                      </span>
                    )}

                    {isDone && result && (
                      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                        {/* Badge versi */}
                        <span style={{
                          display: "inline-flex", alignItems: "center", gap: 5, alignSelf: "flex-start",
                          fontSize: 11, color: "#16a34a", fontWeight: 700,
                          background: "#f0fdf4", border: "1px solid #86efac",
                          borderRadius: 99, padding: "2px 9px",
                        }}>
                          ✓ Plan siap · v{result.version}
                        </span>
                        {/* Waktu generate */}
                        <div style={{ fontSize: 12, color: "#6b7280" }}>
                          Terakhir digenerate pada {formatDate(result.waktu)}
                        </div>
                        {/* Estimasi selesai */}
                        {result.estimasi_waktu_selesai && (
                          <div style={{ fontSize: 12, color: "#374151" }}>
                            🎯 Estimasi selesai: <strong>{result.estimasi_waktu_selesai}</strong>
                          </div>
                        )}
                        {/* Catatan analisa — 2 baris */}
                        {result.catatan_analisa && (
                          <div style={{
                            fontSize: 11, color: "#6b7280", fontStyle: "italic",
                            lineHeight: 1.5, maxWidth: 270,
                            display: "-webkit-box", WebkitLineClamp: 2,
                            WebkitBoxOrient: "vertical", overflow: "hidden",
                          }}>
                            {result.catatan_analisa}
                          </div>
                        )}
                      </div>
                    )}
                  </td>

                  {/* Aksi */}
                  <td style={{ padding: "15px 16px" }}>
                    <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", alignItems: "center" }}>

                      {/* Generate / Regenerate */}
                      <button
                        onClick={() => handleGenerate(kelas)}
                        disabled={isLoading}
                        style={{
                          display: "inline-flex", alignItems: "center", gap: 6,
                          background: isLoading ? "#f3f4f6" : "#f59e0b",
                          color: isLoading ? "#9ca3af" : "#fff",
                          border: "none", borderRadius: 8,
                          padding: "8px 14px", fontSize: 12, fontWeight: 700,
                          cursor: isLoading ? "not-allowed" : "pointer",
                          whiteSpace: "nowrap",
                        }}
                        onMouseEnter={(e) => { if (!isLoading) e.currentTarget.style.background = "#d97706"; }}
                        onMouseLeave={(e) => { if (!isLoading) e.currentTarget.style.background = "#f59e0b"; }}
                      >
                        {isLoading
                          ? <><Spinner color="#9ca3af" /> Generating…</>
                          : isDone ? <>✦ Regenerate</> : <>✦ Generate Plan</>
                        }
                      </button>

                      {/* Lihat Detail — hanya setelah done */}
                      {isDone && (
                        <button
                          onClick={() => setViewingKelas(kelas)}
                          style={{
                            display: "inline-flex", alignItems: "center", gap: 5,
                            background: "#111827", color: "#fff",
                            border: "none", borderRadius: 8,
                            padding: "8px 14px", fontSize: 12, fontWeight: 700,
                            cursor: "pointer", whiteSpace: "nowrap",
                          }}
                          onMouseEnter={(e) => (e.currentTarget.style.background = "#374151")}
                          onMouseLeave={(e) => (e.currentTarget.style.background = "#111827")}
                        >
                          Lihat Detail →
                        </button>
                      )}

                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlanList;