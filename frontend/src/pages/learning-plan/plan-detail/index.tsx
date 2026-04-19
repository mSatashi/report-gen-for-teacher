import React, { useEffect } from "react";
// import { SCHEDULE } from "../constants";
// import type { Session } from "../types";
import type { GenerateplanResponse, KelasResponse } from "../../../service/payload";

interface Props {
  kelas: KelasResponse;
  plan: GenerateplanResponse;
  onBack: () => void;
  onGenerated?: (kelasId: string) => void;
}

// ─── Session card ─────────────────────────────────────────────────────────────

// const SessionCard: React.FC<{ session: Session }> = ({ session: s }) => (
//   <div style={{
//     background: s.color,
//     borderLeft: `4px solid ${s.borderColor}`,
//     borderRadius: 10,
//     padding: "12px 14px",
//   }}>
//     <span style={{ fontSize: 11, color: "#6b7280", fontWeight: 600, display: "block", marginBottom: 4 }}>
//       {s.time}
//     </span>
//     <span style={{ fontSize: 14, fontWeight: 700, color: "#111827", display: "block", marginBottom: 3 }}>
//       {s.subject}
//     </span>
//     <span style={{ fontSize: 12, color: "#6b7280", fontStyle: "italic" }}>
//       {s.note}
//     </span>
//   </div>
// );

// ─── Empty slot ───────────────────────────────────────────────────────────────

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

const PlanDetail: React.FC<Props> = ({ kelas, plan, onBack, onGenerated }) => {
  console.log('plan', plan)
  
  useEffect(() => {
    onGenerated?.(kelas.id);
  }, [kelas.id, onGenerated]);

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

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 20 }}>

      {/* Back + Header */}
      <div style={{ flexShrink: 0 }}>
        <button
          onClick={onBack}
          style={{
            background: "none", border: "none", cursor: "pointer",
            color: "#6b7280", fontSize: 13, fontWeight: 600,
            padding: 0, marginBottom: 14,
            display: "flex", alignItems: "center", gap: 5,
          }}
        >
          ← Kembali ke Mata Pelajaran
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {/* <div style={{
            width: 48, height: 48, borderRadius: 12,
            background: subject.bgColor,
            border: `2px solid ${subject.borderColor}33`,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 24, flexShrink: 0,
          }}>
            {subject.icon}
          </div> */}
          <div>
            <h2 style={{ fontSize: 24, fontWeight: 800, color: "#111827", margin: "0 0 3px" }}>
              {kelas.mata_pelajaran}
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
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10, marginBottom: 12 }}>
          {plan.daftar_rekomendasi_materi.map((val) => (
            <div
              key={val}
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
              {val}
            </div>
          ))}
        </div>

        {/* Session columns */}
        {/* <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
          {filteredSchedule.map((day) => (
            <div key={day.label} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {day.sessions.length > 0
                ? day.sessions.map((session, i) => <SessionCard key={i} session={session} />)
                : <EmptySlot />
              }
            </div>
          ))}
        </div> */}
      </div>

    </div>
  );
};

export default PlanDetail;