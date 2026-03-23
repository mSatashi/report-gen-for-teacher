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