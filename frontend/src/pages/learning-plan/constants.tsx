import type { DaySchedule, SubjectDetail, StatItem, SubjectMeta } from "./types";

export const STUDENTS = ["Aisya Putri", "Rafi Santoso", "Nadia Fajar"];

export const STAT_ITEMS: StatItem[] = [
  { label: "MATERI MINGGU INI", value: 8, sub: "Sesi direncanakan" },
  { label: "SELESAI",           value: 2, sub: "Sudah dilaksanakan", accentColor: "#2E7D52" },
  { label: "FOKUS ADAPTASI",    value: 1, sub: "Topik diperkuat",    accentColor: "#2471A3" },
];

export const SCHEDULE: DaySchedule[] = [
  {
    label: "SEN 10/3",
    sessions: [
      { time: "08:00 – 09:30", subject: "Matematika",   note: "Review bil. negatif (adaptif)", color: "#fffbeb", borderColor: "#C8860A" },
      { time: "10:00 – 11:00", subject: "B. Indonesia",  note: "Menulis deskriptif",             color: "#eff6ff", borderColor: "#2471A3" },
    ],
  },
  {
    label: "SEL 11/3",
    sessions: [
      { time: "08:00 – 09:30", subject: "IPA",           note: "Ekosistem laut · Lanjutan",      color: "#f0fdf4", borderColor: "#2E7D52" },
      { time: "10:00 – 11:30", subject: "Matematika",   note: "Aljabar: latihan soal",           color: "#fffbeb", borderColor: "#C8860A" },
    ],
  },
  {
    label: "RAB 12/3",
    sessions: [
      { time: "08:00 – 09:30", subject: "B. Inggris",   note: "Reading comprehension",           color: "#fff1f2", borderColor: "#C0392B" },
      { time: "10:00 – 11:00", subject: "Seni",          note: "Proyek kolase alam",              color: "#ecfeff", borderColor: "#17a2b8" },
    ],
  },
  {
    label: "KAM 13/3",
    sessions: [
      { time: "08:00 – 09:30", subject: "Matematika",   note: "Persamaan dua variabel",          color: "#fffbeb", borderColor: "#C8860A" },
      { time: "10:00 – 11:00", subject: "IPA",           note: "Evaluasi modul ekosistem",        color: "#f0fdf4", borderColor: "#2E7D52" },
    ],
  },
  {
    label: "JUM 14/3",
    sessions: [
      { time: "08:00 – 09:00", subject: "B. Indonesia",  note: "Presentasi karya",               color: "#eff6ff", borderColor: "#2471A3" },
      { time: "09:30 – 11:00", subject: "Matematika",   note: "Mini test aljabar",               color: "#fffbeb", borderColor: "#C8860A" },
    ],
  },
];

export const SUBJECTS: SubjectDetail[] = [
  { name: "Matematika", sessions: 4, hours: 6,   completed: 1, color: "#3b82f6" },
  { name: "IPA",        sessions: 2, hours: 3,   completed: 1, color: "#22c55e" },
  { name: "Bahasa",     sessions: 3, hours: 4.5, completed: 0, color: "#f59e0b" },
];

// ─── Subject List page data ───────────────────────────────────────────────────

export const SUBJECT_LIST: SubjectMeta[] = [
  {
    id: "matematika",
    name: "Matematika",
    icon: "∑",
    description: "Aljabar, geometri, aritmatika, dan pemecahan masalah numerik.",
    color: "#C8860A",
    borderColor: "#C8860A",
    bgColor: "#fffbeb",
  },
  {
    id: "ipa",
    name: "IPA",
    icon: "⚗",
    description: "Ilmu alam: ekosistem, materi, energi, dan sains kehidupan.",
    color: "#2E7D52",
    borderColor: "#2E7D52",
    bgColor: "#f0fdf4",
  },
  {
    id: "b-indonesia",
    name: "Bahasa Indonesia",
    icon: "✍",
    description: "Membaca, menulis deskriptif, teks narasi, dan presentasi lisan.",
    color: "#2471A3",
    borderColor: "#2471A3",
    bgColor: "#eff6ff",
  },
  {
    id: "b-inggris",
    name: "Bahasa Inggris",
    icon: "🌐",
    description: "Reading comprehension, vocabulary, writing, dan listening.",
    color: "#C0392B",
    borderColor: "#C0392B",
    bgColor: "#fff1f2",
  },
  {
    id: "ips",
    name: "IPS",
    icon: "🗺",
    description: "Sejarah, geografi, ekonomi dasar, dan kehidupan sosial.",
    color: "#7B3FA0",
    borderColor: "#7B3FA0",
    bgColor: "#faf5ff",
  },
  {
    id: "seni",
    name: "Seni & Budaya",
    icon: "🎨",
    description: "Eksplorasi visual, kolase, musik, dan ekspresi kreatif.",
    color: "#17a2b8",
    borderColor: "#17a2b8",
    bgColor: "#ecfeff",
  },
];