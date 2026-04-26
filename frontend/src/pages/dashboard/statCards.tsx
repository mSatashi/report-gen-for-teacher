import { IconStudents, IconLog, IconPlan, IconPending } from "../../icons";
import type { DashboardResponse } from "../../service/payload";
import type { StatCard } from "./StatCardItem";

export const buildStatCards = (data: DashboardResponse | null): StatCard[] => [
  {
    label: "Total Siswa",
    value: data?.total_siswa ?? 0,
    badge: { count: data?.total_siswa ?? 0, text: "Terdaftar", color: "green" },
    bg: "#f0fdf4",
    iconColor: "#22c55e",
    icon: <IconStudents />,
  },
  {
    label: "Log Hari Ini",
    value: data?.log_hari_ini ?? 0,
    badge: { count: data?.log_hari_ini ?? 0, text: "Diinput hari ini", color: "blue" },
    bg: "#eff6ff",
    iconColor: "#3b82f6",
    icon: <IconLog />,
  },
  {
    label: "Kelas Terencana", 
    value: data?.plan_aktif ?? 0,
    badge: { 
      count: data?.plan_aktif ?? 0, 
      text: "Terkini", 
      color: "green" 
    },
    bg: "#f0fdf4", 
    iconColor: "#15803d",
    icon: <IconPlan />,
  },
  {
    label: "Report Pending",
    value: data?.report_pending ?? 0,
    badge: { count: data?.report_pending ?? 0, text: "Siap dikirim", color: "red" },
    bg: "#fff1f2",
    iconColor: "#f43f5e",
    icon: <IconPending />,
  },
];