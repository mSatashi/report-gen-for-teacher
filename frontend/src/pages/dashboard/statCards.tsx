import { IconStudents, IconLog, IconPlan, IconPending } from "../../icons";
import type { DashboardResponse } from "../../service/payload";

export const buildStatCards = (data: DashboardResponse | null) => [
  {
    label: "Total Siswa",
    value: data?.total_siswa ?? 0,
    badge: { count: data?.total_siswa ?? 0, text: "Terdaftar", color: "green" as const },
    bg: "#f0fdf4", iconColor: "#22c55e", icon: <IconStudents />,
  },
  {
    label: "Log Hari Ini",
    value: data?.log_hari_ini ?? 0,
    badge: { count: data?.log_hari_ini ?? 0, text: "Belum diinput", color: "blue" as const },
    bg: "#eff6ff", iconColor: "#3b82f6", icon: <IconLog />,
  },
  {
    label: "Plan Aktif",
    value: data?.plan_aktif ?? 0,
    badge: { count: data?.plan_aktif ?? 0, text: "Sesuai jadwal", color: "yellow" as const },
    bg: "#fffbeb", iconColor: "#f59e0b", icon: <IconPlan />,
  },
  {
    label: "Report Pending",
    value: data?.report_pending ?? 0,
    badge: { count: data?.report_pending ?? 0, text: "Siap dikirim", color: "red" as const },
    bg: "#fff1f2", iconColor: "#f43f5e", icon: <IconPending />,
  },
];