import React from "react";
import type { LogEntry, TingkatPemahaman, TingkatKeterlibatan, MakulEntry, MapelSiswaState } from "./types";

// ─── Seed data ────────────────────────────────────────────────────────────────

export const INITIAL_LOG_DATA: LogEntry[] = [
  { id: 1, siswa: "Aisya Putri",  idMapel: 1, mapel: "Matematika",       materi: "Integral",                     catatan: "Belum terlalu menguasai perhitungan integral",           tingkat_penguasaan: "Perlu Review", tanggal: "2025-01-15", durasi: "90", metode: "Penjelasan langsung", keterlibatan: "Aktif" },
  { id: 2, siswa: "Rafi Santoso", idMapel: 2, mapel: "Bahasa Indonesia", materi: "Menentukan ide pokok kalimat", catatan: "Memahami dengan mudah menentukan ide pokok pada kalimat",  tingkat_penguasaan: "Sangat Paham", tanggal: "2025-01-15", durasi: "60", metode: "Diskusi",             keterlibatan: "Sangat Aktif" },
  { id: 3, siswa: "Nadia Fajar",  idMapel: 3, mapel: "Fisika",           materi: "Kecepatan",                    catatan: "Siswa dapat memahami dan mengerjakan soal kecepatan",    tingkat_penguasaan: "Sangat Paham", tanggal: "2025-01-16", durasi: "90", metode: "Latihan soal",       keterlibatan: "Sangat Aktif" },
  { id: 4, siswa: "Aisya Putri",  idMapel: 1, mapel: "Matematika",       materi: "Turunan",                      catatan: "Siswa mulai memahami konsep turunan dasar",               tingkat_penguasaan: "Cukup",        tanggal: "2025-01-17", durasi: "90", metode: "Latihan soal",       keterlibatan: "Aktif" },
  { id: 5, siswa: "Budi Santoso", idMapel: 1, mapel: "Matematika",       materi: "Integral",                     catatan: "Siswa mampu mengerjakan soal integral sederhana",          tingkat_penguasaan: "Paham",        tanggal: "2025-01-15", durasi: "90", metode: "Penjelasan langsung", keterlibatan: "Aktif" },
];

export const INITIAL_MAKUL_DATA: MakulEntry[] = [
  { id: 1, nama: "Matematika",       jumlahSiswa: 15, deskripsi: "Aljabar, Kalkulus, Statistika" },
  { id: 2, nama: "Bahasa Indonesia", jumlahSiswa: 20, deskripsi: "Teks, Sastra, Tata Bahasa"     },
  { id: 3, nama: "Fisika",           jumlahSiswa: 15, deskripsi: "Mekanika, Termodinamika"        },
  { id: 4, nama: "IPA",              jumlahSiswa: 20, deskripsi: "Biologi, Kimia, Fisika Dasar"   },
  { id: 5, nama: "Bahasa Inggris",   jumlahSiswa: 15, deskripsi: "Grammar, Reading, Speaking"     },
];

export const INITIAL_SISWA_DATA = [
  { id: 1, nama: "Aisya Putri",  kelas: "X IPA 1" },
  { id: 2, nama: "Rafi Santoso", kelas: "X IPA 1" },
  { id: 3, nama: "Nadia Fajar",  kelas: "X IPA 2" },
  { id: 4, nama: "Budi Santoso", kelas: "X IPA 2" },
  { id: 5, nama: "Citra Dewi",   kelas: "X IPA 1" },
];

// Pivot: siswa mana yang ikut makul mana
export const INITIAL_MAKUL_SISWA: MapelSiswaState[] = [
  { id: 1, idSiswa: 1, idMapel: 1 },  // Aisya  → Matematika
  { id: 2, idSiswa: 4, idMapel: 1 },  // Budi   → Matematika
  { id: 3, idSiswa: 5, idMapel: 1 },  // Citra  → Matematika
  { id: 4, idSiswa: 2, idMapel: 2 },  // Rafi   → Bahasa Indonesia
  { id: 5, idSiswa: 1, idMapel: 2 },  // Aisya  → Bahasa Indonesia
  { id: 6, idSiswa: 3, idMapel: 3 },  // Nadia  → Fisika
  { id: 7, idSiswa: 4, idMapel: 3 },  // Budi   → Fisika
];

// ─── Select options ───────────────────────────────────────────────────────────

export const SISWA_OPTIONS  = ["Aisya Putri", "Rafi Santoso", "Nadia Fajar", "Budi Santoso", "Citra Dewi"];
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
  width: "100%", padding: "9px 12px", borderRadius: 8, border: "1px solid #e5e7eb",
  fontSize: 13, color: "#111827", background: "#fff", outline: "none",
  fontFamily: "inherit", boxSizing: "border-box",
};

export const textareaStyle: React.CSSProperties = { ...inputStyle, resize: "vertical", minHeight: 90 };

export const cardStyle: React.CSSProperties = {
  background: "#fff", borderRadius: 14, padding: "24px 28px", boxShadow: "0 1px 4px rgba(0,0,0,.06)",
};

export const btnAddStyle: React.CSSProperties = {
  background: "#06b6d4", color: "#fff", border: "none",
  borderRadius: 8, padding: "8px 16px", fontSize: 13, fontWeight: 600, cursor: "pointer",
};

// ─── Shared atoms ─────────────────────────────────────────────────────────────

export const Label: React.FC<{ text: string; optional?: boolean }> = ({ text, optional }) => (
  <div style={{ fontSize: 13, fontWeight: 600, color: "#374151", marginBottom: 6 }}>
    {text}
    {optional && <span style={{ fontWeight: 400, color: "#9ca3af", marginLeft: 4 }}>(opsional)</span>}
  </div>
);