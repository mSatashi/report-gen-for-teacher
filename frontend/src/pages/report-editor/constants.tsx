import type { ReportSection, SubjectStat } from "./types";

export const STUDENTS = ["Aisya Putri", "Rafi Santoso", "Nadia Fajar"];

export const INITIAL_SECTIONS: ReportSection[] = [
  // {
  //   id: "ringkasan",
  //   emoji: "📋",
  //   label: "Ringkasan Periode",
  //   accentColor: "#f59e0b",
  //   content:
  //     "Aisya Putri telah menyelesaikan 24 sesi belajar selama periode Februari – Maret 2025 dengan total 48 jam pembelajaran. Secara keseluruhan, Aisya menunjukkan kemajuan yang konsisten dan motivasi belajar yang tinggi.",
  // },
  // {
  //   id: "pengembangan",
  //   emoji: "💡",
  //   label: "Area Pengembangan",
  //   accentColor: "#f43f5e",
  //   content:
  //     "Beberapa area yang masih perlu dikembangkan antara lain: (1) Operasi bilangan negatif dalam aljabar, (2) Kecepatan membaca teks berbahasa Inggris, dan (3) Konsistensi dalam mengerjakan latihan mandiri di rumah.",
  // },
  // {
  //   id: "capaian",
  //   emoji: "📝",
  //   label: "Capaian Akademik",
  //   accentColor: "#3b82f6",
  //   content:
  //     "Matematika: Aisya berhasil menguasai konsep aljabar dasar dengan tingkat pemahaman 78%. Persamaan linear satu variabel telah dikuasai dengan baik. Area yang membutuhkan perhatian adalah operasi bilangan negatif yang akan menjadi fokus minggu berikutnya.",
  // },
  {
    id: "rekomendasi",
    emoji: "🎯",
    label: "Rekomendasi Plan ke Depan",
    accentColor: "#22c55e",
    content:
      "Untuk periode berikutnya, disarankan untuk: (1) Memperkuat pemahaman bilangan negatif dengan latihan soal bertahap, (2) Menambah sesi reading 2x seminggu, dan (3) Memperkenalkan proyek lintas mata pelajaran untuk memperkuat koneksi konsep.",
  },
  // {
  //   id: "karakter",
  //   emoji: "🌱",
  //   label: "Perkembangan Karakter",
  //   accentColor: "#8b5cf6",
  //   content:
  //     "Aisya menunjukkan sikap yang sangat positif dalam proses pembelajaran. Ia terbiasa mengajukan pertanyaan, aktif berpartisipasi, dan menunjukkan rasa ingin tahu yang tinggi terhadap materi baru. Kedisiplinan dalam mengikuti jadwal belajar juga meningkat signifikan.",
  // },
];

export const SUBJECT_STATS: SubjectStat[] = [
  { name: "Matematika",   sessions: 10, progress: 78, color: "#3b82f6", bgColor: "#eff6ff" },
  { name: "IPA",          sessions: 6,  progress: 91, color: "#22c55e", bgColor: "#f0fdf4" },
  { name: "B. Inggris",   sessions: 5,  progress: 52, color: "#f43f5e", bgColor: "#fff1f2" },
  { name: "B. Indonesia", sessions: 3,  progress: 70, color: "#f59e0b", bgColor: "#fffbeb" },
];