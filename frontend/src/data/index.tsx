import {
  IconDashboard,
  IconDailyLog,
  IconCalendar,
  IconReport,
  IconStudents,
  IconLog,
  IconPlan,
  IconPending,
  IconKelas,
} from "../icons";
import type { NavItem, StatCard, Student, Activity } from "../types";

export const NAV_ITEMS: NavItem[] = [
  { kind: "section", label: "Main Menu" },
  { kind: "link", label: "Dashboards",    route: "home",         icon: <IconDashboard /> },
  { kind: "link", label: "Daily Log",     route: "dailyLog",     icon: <IconDailyLog /> },
  { kind: "link", label: "Learning Plan", route: "learningPlan", icon: <IconCalendar /> },
  { kind: "section", label: "Master Data" },
  { kind: "link", label: "Kelas", route: "masterKelas", icon: <IconKelas /> },
  { kind: "link", label: "Mata Pelajaran", route: "masterMapel", icon: <IconKelas /> },
  { kind: "link", label: "Siswa", route: "masterSiswa", icon: <IconStudents /> },
  { kind: "section", label: "Report" },
  { kind: "link", label: "Report Editor", route: "reportEditor", icon: <IconReport /> },
  { kind: "section", label: "IF5200 - PPT" },
];

export const STAT_CARDS: StatCard[] = [
  {
    label: "Total Siswa",
    value: 3,
    badge: { count: 2, text: "Completed", color: "green" },
    bg: "#f0fdf4",
    iconColor: "#22c55e",
    icon: <IconStudents />,
  },
  {
    label: "Log Hari Ini",
    value: 2,
    badge: { count: 1, text: "Belum diinput", color: "blue" },
    bg: "#eff6ff",
    iconColor: "#3b82f6",
    icon: <IconLog />,
  },
  {
    label: "Plan Aktif",
    value: 3,
    badge: { count: 3, text: "Sesuai jadwal", color: "yellow" },
    bg: "#fffbeb",
    iconColor: "#f59e0b",
    icon: <IconPlan />,
  },
  {
    label: "Report Pending",
    value: 1,
    badge: { count: 1, text: "Siap dikirim", color: "red" },
    bg: "#fff1f2",
    iconColor: "#f43f5e",
    icon: <IconPending />,
  },
];

export const STUDENTS: Student[] = [
  {
    name: "Aisya Putri",
    subject: "Matematika",
    subtopic: "Aljabar Dasar",
    progress: 78,
    status: "On Track",
    note: "78% target terpenuhi",
    avatarColor: "#dbeafe",
  },
  {
    name: "Rafi Santoso",
    subject: "Bahasa Inggris",
    subtopic: "Reading Comp.",
    progress: 52,
    status: "Perlu Perhatian",
    note: "52% · Plan diadaptasi AI hari ini",
    avatarColor: "#fef3c7",
  },
  {
    name: "Nadia Fajar",
    subject: "IPA",
    subtopic: "Ekosistem",
    progress: 85,
    status: "On Track",
    note: "85% target terpenuhi",
    avatarColor: "#dcfce7",
  },
];

export const ACTIVITIES: Activity[] = [
  {
    date: "10 MAR",
    title: "Log Aisya · Matematika",
    subtitle: "Aljabar: persamaan linear · 90 menit",
    tags: [
      { label: "Paham",  color: "#dcfce7" },
      { label: "Aktif",  color: "#dbeafe" },
    ],
  },
  {
    date: "10 MAR",
    title: "Log Nadia · IPA",
    subtitle: "Ekosistem laut · Praktik observasi",
    tags: [{ label: "Sangat Baik", color: "#dcfce7" }],
  },
  {
    date: "9 MAR",
    title: "Log Rafi · Bahasa Inggris",
    subtitle: "Reading Comp. · 60 menit",
    tags: [{ label: "Perlu Ulang", color: "#fee2e2" }],
  },
];

