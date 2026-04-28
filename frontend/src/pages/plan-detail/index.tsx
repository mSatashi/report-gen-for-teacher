import { useEffect, useState } from "react";
import type { GenerateplanResponse, KelasResponse, MapelResponse } from "../../service/payload";
import { useLearningPlan } from "./useLearningPlan";
import { fonts } from "../../components/fontstyle";
import { styles, topikColors } from "./styles";

interface Props {
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
  kelas: KelasResponse;
  mapel: MapelResponse;
}

export default function PlanDetail({ onNavigate, kelas, mapel }: Props) {
  const [planList, setPlanList] = useState<GenerateplanResponse[]>([]);
  const { loadPlan } = useLearningPlan();

  useEffect(() => {
    loadPlan(kelas.id).then((data) => {
      if (data?.length) setPlanList(data);
    });
  }, []);

  const latestPlan = planList?.sort((a, b) => b.version - a.version)[0];
  const allTopiks = latestPlan?.daftar_rekomendasi_materi ?? [];

  return (
    <div style={styles.root}>

      {/* ── Header ── */}
      <div style={styles.header}>
        <div>
          <h2 style={{ ...fonts.h2, margin: "0 0 4px" }}>Plan Detail</h2>
          <p style={styles.pageSubtitle}>
            Learning plan • {kelas?.mata_pelajaran_obj?.nama_mata_pelajaran}
          </p>
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); onNavigate?.("detailKelas", { kelasId: kelas.id }); }}
          style={styles.backBtn}
        >
          ← Kembali
        </button>
      </div>

      {/* ── Info Cards ── */}
      {latestPlan && (
        <div style={styles.infoGrid}>
          <div style={styles.infoCard}>
            <span style={styles.infoLabel}>Mata Pelajaran</span>
            <span style={styles.infoValue}>{mapel?.nama_mata_pelajaran ?? "-"}</span>
          </div>

          <div style={styles.infoCard}>
            <span style={styles.infoLabel}>Versi Plan</span>
            <div style={styles.infoValueRow}>
              <span style={styles.infoValue}>v{latestPlan.version}</span>
              {latestPlan.is_outdated && (
                <span style={styles.outdatedBadge}>Outdated</span>
              )}
            </div>
          </div>

          <div style={styles.infoCard}>
            <span style={styles.infoLabel}>Estimasi Selesai</span>
            <span style={styles.infoValue}>
              {latestPlan.estimasi_waktu_selesai
                ? new Date(latestPlan.estimasi_waktu_selesai).toLocaleDateString("id-ID", {
                    day: "numeric", month: "long", year: "numeric",
                  })
                : "-"}
            </span>
          </div>

          <div style={styles.infoCard}>
            <span style={styles.infoLabel}>Total Minggu</span>
            <span style={styles.infoValue}>{latestPlan.jadwal_mingguan?.length ?? 0} minggu</span>
          </div>
        </div>
      )}

      {/* ── Catatan Analisa ── */}
      {latestPlan?.catatan_analisa && (
        <div style={styles.catatanBox}>
          <span style={{ fontSize: 16, flexShrink: 0 }}>💡</span>
          <div>
            <span style={styles.catatanLabel}>CATATAN ANALISA</span>
            <span style={styles.catatanText}>{latestPlan.catatan_analisa}</span>
          </div>
        </div>
      )}

      {/* ── Daftar Rekomendasi Materi ── */}
      {allTopiks.length > 0 && (
        <div style={styles.rekomendasiBox}>
          <p style={styles.rekomendasiTitle}>DAFTAR REKOMENDASI MATERI</p>
          <div style={styles.rekomendasiPills}>
            {allTopiks.map((topik, i) => {
              const c = topikColors[i % topikColors.length];
              return (
                <span key={i} style={{
                  background: c.bg, color: c.color, border: `1px solid ${c.border}`,
                  borderRadius: 8, padding: "5px 12px", fontSize: 12, fontWeight: 600,
                }}>
                  {topik}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Jadwal Mingguan ── */}
      <div style={styles.jadwalBox}>
        <h4 style={styles.jadwalTitle}>Jadwal Mingguan</h4>

        {!latestPlan ? (
          <div style={styles.emptyState}>Belum ada learning plan yang digenerate.</div>
        ) : latestPlan.jadwal_mingguan?.length === 0 ? (
          <div style={styles.emptyState}>Jadwal mingguan kosong.</div>
        ) : (
          <div style={styles.jadwalGrid}>
            {latestPlan.jadwal_mingguan?.map((item, i) => (
              <div key={i} style={styles.mingguColumn}>

                {/* Label nama minggu di atas card */}
                <span style={styles.mingguLabel}>{item.minggu}</span>

                {/* Card topik — border hijau seperti gambar */}
                <div style={styles.mingguCard}>
                  {item.topik?.length > 0 ? (
                    item.topik.map((t: string, j: number) => (
                      <div
                        key={j}
                        style={j < item.topik.length - 1 ? styles.topikRow : styles.topikRowLast}
                      >
                        {t}
                      </div>
                    ))
                  ) : (
                    <div style={styles.emptyTopik}>Tidak ada topik</div>
                  )}
                </div>

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}