import { useEffect, useState } from "react";
import type { GenerateplanResponse, KelasResponse } from "../../service/payload";
import { useLearningPlan } from "./useLearningPlan";

interface Props {
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
  kelas: KelasResponse;
}

export default function PlanDetail({ onNavigate, kelas }: Props) {
  const [planList, setPlanList] = useState<GenerateplanResponse[]>([]);
  const { loadPlan, status } = useLearningPlan();

  useEffect(() => {
    loadPlan(kelas.id).then((data) => {
      if (data?.length) setPlanList(data);
    });
  }, [kelas.id, loadPlan]);

  const latestPlan = planList?.sort((a, b) => b.version - a.version)[0];
  
  // LOGIC FALLBACK: Jika plan belum ada, gunakan topik_list dari Mapel
  const hasPlan = !!latestPlan;
  const defaultTopics = kelas.mata_pelajaran_obj?.topik_list?.map(t => t.nama) || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 20, padding: 20 }}>
      <button
        onClick={() => onNavigate?.("detailKelas", { kelasId: kelas.id })}
        style={{ background: "none", border: "none", color: "#6b7280", cursor: "pointer", fontWeight: 600 }}
      >
        ← Kembali ke Detail Kelas
      </button>

      <div>
        <h2 style={{ fontSize: 24, fontWeight: 800 }}>{kelas.mata_pelajaran_obj?.nama_mata_pelajaran}</h2>
        <p style={{ color: "#9ca3af" }}>{hasPlan ? `Learning Plan AI (Versi ${latestPlan.version})` : "Menggunakan Urutan Kurikulum Standar"}</p>
      </div>

      {!hasPlan && status !== "loading" && (
        <div style={{ background: "#fffbeb", border: "1px dashed #f59e0b", padding: 16, borderRadius: 12, color: "#b45309", fontSize: 14 }}>
          ⚠️ <strong>Rencana Studi AI belum di-generate.</strong> Menampilkan urutan materi default berdasarkan kurikulum mata pelajaran.
        </div>
      )}

      <div style={{ background: "#fff", borderRadius: 14, padding: 24, border: "1px solid #e5e7eb" }}>
        <h4 style={{ marginBottom: 18 }}>Jadwal / Urutan Materi</h4>
        
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {hasPlan ? (
            // Render dari hasil PSO
            Object.entries(latestPlan.jadwal_mingguan).map(([minggu, topiks]) => (
              <div key={minggu} style={{ padding: 12, background: "#f8fafc", borderRadius: 10 }}>
                <strong style={{ display: "block", marginBottom: 5, color: "#4f46e5" }}>{minggu}</strong>
                {topiks.map((t, i) => <div key={i} style={{ fontSize: 13 }}>• {t}</div>)}
              </div>
            ))
          ) : (
            // Render dari Master Mapel (Standard)
            defaultTopics.map((topic, idx) => (
              <div key={idx} style={{ padding: "10px 15px", background: "#f3f4f6", borderRadius: 8, fontSize: 13 }}>
                {idx + 1}. {topic}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}