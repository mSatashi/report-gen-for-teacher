// import React, { useEffect } from "react";
// import type { Kelas } from "../../types";
// import type { GenerateplanResponse } from "../../service/payload";
// import { SCHEDULE } from "../constants";
// import type { Session } from "../types";

import { useEffect, useState } from "react";
import type { GenerateplanResponse, KelasResponse } from "../../service/payload";
import { useLearningPlan } from "./useLearningPlan";
// import type { Session } from "react-router-dom";

interface Props {
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
  kelas: KelasResponse;
}

// ─── Session card ─────────────────────────────────────────────────────────────

// const SessionCard: React.FC<{ session: Session }> = ({ session: s }) => (
//   <div style={{
//     // background: s.color,
//     // borderLeft: `4px solid ${s.borderColor}`,
//     borderRadius: 10,
//     padding: "12px 14px",
//   }}>
//     <span style={{ fontSize: 11, color: "#6b7280", fontWeight: 600, display: "block", marginBottom: 4 }}>
//       {'s.time'}
//     </span>
//     <span style={{ fontSize: 14, fontWeight: 700, color: "#111827", display: "block", marginBottom: 3 }}>
//       {'s.subject'}
//     </span>
//     <span style={{ fontSize: 12, color: "#6b7280", fontStyle: "italic" }}>
//       {'s.note'}
//     </span>
//   </div>
// );

// const EmptySlot: React.FC = () => (
//   <div style={{
//     border: "1.5px dashed #e5e7eb",
//     borderRadius: 10,
//     padding: "20px 14px",
//     display: "flex",
//     alignItems: "center",
//     justifyContent: "center",
//   }}>
//     <span style={{ fontSize: 12, color: "#d1d5db" }}>Tidak ada sesi</span>
//   </div>
// );

// ─── Subject Schedule page ────────────────────────────────────────────────────
export default function PlanDetail({ onNavigate, kelas }: Props) {
const [planList, setPlanList] = useState<GenerateplanResponse[]>([]);

  const { loadPlan } = useLearningPlan();

  useEffect(() => {
    loadPlan(kelas.id).then((data) => {
      if (data?.length) setPlanList(data);
    });
  }, []);

  const latestPlan = planList
    ?.sort((a, b) => b.version - a.version)[0];

  // useEffect(() => {
  //   onGenerated?.(kelas.id);
  // }, [kelas.id, onGenerated]);

  // const filteredSchedule = plan.map((day) => ({
  //   ...day,
  //   sessions: day.sessions.filter(
  //     (s) =>
  //       s.kelas.toLowerCase().includes(kelas.mata_pelajaran.toLowerCase()) ||
  //       kelas.mata_pelajaran.toLowerCase().includes(s.kelas.toLowerCase())
  //   ),
  // }));

  // const totalSessions = filteredSchedule.reduce((sum, d) => sum + d.sessions.length, 0);
  // const totalMinutes = filteredSchedule.reduce((sum, day) => {
  //   return sum + day.sessions.reduce((s, session) => {
  //     const [start, end] = session.time.split("–").map((t) => {
  //       const [h, m] = t.trim().split(":").map(Number);
  //       return h * 60 + m;
  //     });
  //     return s + (end - start);
  //   }, 0);
  // }, 0);
  // const totalHours = (totalMinutes / 60).toFixed(1);

  console.log("kelas di plan detail:", planList);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 20 }}>

      {/* Back + Header */}
      <div style={{ flexShrink: 0 }}>
        <div style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "flex-start", 
          marginBottom: 20, 
          flexShrink: 0, 
          flexWrap: "wrap", 
          gap: 12 
          }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <span style={{ fontSize: 13, color: "#9ca3af", cursor: "pointer" }} 
              onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog"); }}
              >
                Daily Log
              </span>
            </div>
  
            {/* Siswa info row */}
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div style={{ width: 44, height: 44, borderRadius: "50%", background: "#eff6ff", color: "#3b82f6", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 700, flexShrink: 0 }}>
                {'initials'}
              </div>
              <div>
                {/* <h2 style={{ fontSize: 22, fontWeight: 700, color: "#111827", margin: "0 0 2px" }}>
                  {siswa.nama}
                </h2>
                <p style={{ color: "#9ca3af", fontSize: 13, margin: 0 }}>
                  {siswa.education_level} · {mapel.nama_mata_pelajaran}
                </p> */}
              </div>
            </div>
          </div>
  
          <div style={{ display: "flex", gap: 10 }}>
            <button 
              // onClick={(e) => { e.stopPropagation(); onNavigate?.("detailKelas", { kelasId }) }}
              style={{ background: "none", border: "1px solid #e5e7eb", borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 500, color: "#374151", cursor: "pointer" }}>
              ← Kembali
            </button>
            <button 
              // onClick={(e) => { e.stopPropagation(); onNavigate?.("formDailyLog", { namaSiswa: siswa.nama, mapel: mapel, kelasId, siswa }) }}
              // style={btnAddStyle}
              >
              + Tambah Log
            </button>
          </div>
        </div>

        {/* <button
          onClick={(e) => { e.stopPropagation(); onNavigate?.("detailKelas", { kelasId: kelas.id }); }}
          style={{
            background: "none", border: "none", cursor: "pointer",
            color: "#6b7280", fontSize: 13, fontWeight: 600,
            padding: 0, marginBottom: 14,
            display: "flex", alignItems: "center", gap: 5,
          }}
        >
          ← Kembali ke Mata Pelajaran
        </button> */}

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 12,
            // background: subject.bgColor,
            // border: `2px solid ${subject.borderColor}33`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 24, flexShrink: 0,
          }}>
            {/* {subject.icon} */}
          </div>
          <div>
            <h2 style={{ fontSize: 24, fontWeight: 800, color: "#111827", margin: "0 0 3px" }}>
              {kelas?.mata_pelajaran_obj?.nama_mata_pelajaran }
            </h2>
            <p style={{ fontSize: 13, color: "#9ca3af", margin: 0 }}>
              Jadwal mingguan
            </p>
          </div>
        </div>
      </div>

      {/* Stat chips */}
      <div style={{ display: "flex", gap: 10, flexShrink: 0, flexWrap: "wrap" }}>
        {/* {[
          { label: "Total Sesi", value: "String(totalSessions)" },
          { label: "Total Jam", value: "`${totalHours} jam`" },
        ].map((chip) => (
          <div
            key={chip.label}
            style={{
              // background: subject.bgColor,
              // border: `1px solid ${subject.borderColor}33`,
              borderRadius: 10,
              padding: "10px 18px",
            }}
          >
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: 1, 
              // color: subject.color, 
              textTransform: "uppercase", marginBottom: 3 }}>
              {`chip.label`}
            </div>
            <div style={{ fontSize: 22, fontWeight: 800, color: "#111827" }}>{chip.value}</div>
          </div>
        ))} */}

        {/* {totalSessions === 0 && (
          <div style={{
            background: "#fff7ed", border: "1px solid #fed7aa",
            borderRadius: 10, padding: "10px 18px",
            fontSize: 13, color: "#c2410c", fontWeight: 500,
            display: "flex", alignItems: "center",
          }}>
            Belum ada sesi {kelas.mata_pelajaran} di minggu ini.
          </div>
        )} */}
      </div>

      {/* Weekly schedule grid */}
      <div style={{
        background: "#fff",
        borderRadius: 14,
        boxShadow: "0 1px 4px rgba(0,0,0,.06)",
        border: "1px solid #e5e7eb",
        padding: "22px 24px",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
          <h4 style={{ fontSize: 16, fontWeight: 700, color: "#111827", margin: 0 }}>Jadwal Mingguan</h4>
          {/* <span style={{
            fontSize: 12, color: "#9ca3af",
            background: "#f3f4f6", borderRadius: 6,
            padding: "4px 12px", fontWeight: 500,
          }}>
            Klik sesi untuk detail
          </span> */}
        </div>

        {/* Day headers */}
        {Object.entries(latestPlan?.jadwal_mingguan ?? {}).map(([mingguKey]) => (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10, marginBottom: 12 }}>
          {/* {planList?..map((val) => ( */}
            <div
              key={mingguKey}
              style={{
                // background: day.sessions.length > 0 ? subject.bgColor : "#f3f4f6",
                // border: day.sessions.length > 0 ? `1px solid ${subject.borderColor}33` : "none",
                borderRadius: 8,
                textAlign: "center",
                padding: "10px 4px",
                fontSize: 12,
                fontWeight: 700,
                // color: day.sessions.length > 0 ? subject.color : "#6b7280",
              }}
            >
              {mingguKey}
            </div>
          {/* ))} */}
        </div>
        ))}

        {/* Session columns */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
          {/* {latestPlan?.jadwal_mingguan && Object.entries(latestPlan.jadwal_mingguan).map(([mingguKey, sessions]) => (
            <div key={mingguKey} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {sessions.length > 0
                ? sessions.map((session, i) => <SessionCard key={i} session={session} />)
                : <EmptySlot />
              }
            </div>
          ))} */}
        </div>
      </div>

    </div>
  );
};