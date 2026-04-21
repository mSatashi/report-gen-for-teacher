export interface StatCard {
  label: string;
  value: number;
  badge: { count: number; text: string; color: "green" | "blue" | "yellow" | "red" };
  bg: string;
  iconColor: string;
  icon: React.ReactNode;
}

export interface Student {
  name: string;
  subject: string;
  subtopic: string;
  progress: number;
  status: "On Track" | "Perlu Perhatian";
  note?: string;
  avatarColor: string;
}

export interface Activity {
  date: string;
  title: string;
  subtitle: string;
  tags: { label: string; color: string }[];
}

export type NavItem =
  | { kind: "section"; label: string }
  | { kind: "link"; label: string; route: string; icon: React.ReactNode };

export interface Kelas {
  id: string;
  nama: string;
  mata_pelajaran: string;
  pengajar_id: string;
  kredit: number;
  jadwal: string;
  created_at?: string;
  siswa: Siswa[];
}

export interface Siswa {
  id: string;
  username: string;
  email_address: string;
  password?: string;
  nama: string;
  usia: string;
  level: string;
  credit_total: number;
  credit_used?: number;
}

export type ModalMode = "add-siswa" | "edit-siswa" | null;
export type ToastType = "success" | "error";

export type Toast = {
  id: number;
  message: string;
  type: ToastType;
};