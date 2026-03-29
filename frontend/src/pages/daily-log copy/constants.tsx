import React from "react";
import type { LogEntry, TingkatPemahaman, TingkatKeterlibatan } from "./types";

// ─── Seed data ────────────────────────────────────────────────────────────────

export const INITIAL_DATA: LogEntry[] = [
  { id: 1, mapel: "Matematika",       materi: "Integral",                     catatan: "Belum terlalu menguasai dan belum terlalu memahami perhitungan integral",   tingkat_penguasaan: "Perlu Review" },
  { id: 2, mapel: "Bahasa Indonesia", materi: "Menentukan ide pokok kalimat", catatan: "Memahami dengan mudah jenis-jenis menentukan ide pokok pada suatu kalimat", tingkat_penguasaan: "Sangat Paham" },
  { id: 3, mapel: "Fisika",           materi: "Kecepatan",                    catatan: "Siswa dapat dengan mudah memahami dan mengerjakan soal terkait kecepatan",  tingkat_penguasaan: "Sangat Paham" },
];

// ─── Select options ───────────────────────────────────────────────────────────

export const SISWA_OPTIONS  = ["Aisya Putri", "Rafi Santoso", "Nadia Fajar"];
export const MAPEL_OPTIONS  = ["Matematika", "Bahasa Indonesia", "Fisika", "IPA", "Bahasa Inggris"];
export const METODE_OPTIONS = ["Penjelasan langsung", "Diskusi", "Latihan soal", "Praktik", "Presentasi"];

// ─── Toggle button options ────────────────────────────────────────────────────

export const PEMAHAMAN_OPTIONS: { value: TingkatPemahaman; emoji: string; activeBg: string }[] = [
  { value: "Sangat Paham", emoji: "🤩", activeBg: "#22c55e" },
  { value: "Paham",        emoji: "😊", activeBg: "#3b82f6" },
  { value: "Cukup",        emoji: "😐", activeBg: "#f59e0b" },
  { value: "Perlu Review", emoji: "😟", activeBg: "#f43f5e" },
];

export const KETERLIBATAN_OPTIONS: { value: TingkatKeterlibatan; emoji: string; activeBg: string }[] = [
  { value: "Sangat Aktif", emoji: "⚡", activeBg: "#f59e0b" },
  { value: "Aktif",        emoji: "✔",  activeBg: "#22c55e" },
  { value: "Kurang Fokus", emoji: "🧘", activeBg: "#9ca3af" },
];

// ─── Badge colour map ─────────────────────────────────────────────────────────

export const PENGUASAAN_BADGE: Record<TingkatPemahaman, { bg: string; color: string }> = {
  "Sangat Paham": { bg: "#dcfce7", color: "#15803d" },
  "Paham":        { bg: "#dbeafe", color: "#1d4ed8" },
  "Cukup":        { bg: "#fef9c3", color: "#ca8a04" },
  "Perlu Review": { bg: "#fee2e2", color: "#dc2626" },
};

// ─── Shared styles ────────────────────────────────────────────────────────────

export const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "9px 12px",
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  fontSize: 13,
  color: "#111827",
  background: "#fff",
  outline: "none",
  fontFamily: "inherit",
  boxSizing: "border-box",
};

export const textareaStyle: React.CSSProperties = {
  ...inputStyle,
  resize: "vertical",
  minHeight: 90,
};

export const cardStyle: React.CSSProperties = {
  background: "#fff",
  borderRadius: 14,
  padding: "24px 28px",
  boxShadow: "0 1px 4px rgba(0,0,0,.06)",
};

// ─── Shared atoms ─────────────────────────────────────────────────────────────

export const Label: React.FC<{ text: string; optional?: boolean }> = ({ text, optional }) => (
  <div style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 }}>
    {text}
    {optional && <span style={{ fontWeight: 400, color: "#9ca3af", marginLeft: 4 }}>(opsional)</span>}
  </div>
);