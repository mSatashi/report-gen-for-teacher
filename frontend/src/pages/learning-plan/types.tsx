export interface Session {
  time: string;
  subject: string;
  note: string;
  color: string;
  borderColor: string;
}

export interface DaySchedule {
  label: string;
  sessions: Session[];
}

export interface SubjectDetail {
  name: string;
  sessions: number;
  hours: number;
  completed: number;
  color: string;
}

export interface StatItem {
  label: string;
  value: number;
  sub: string;
  accentColor?: string;
}

// ─── Subject List page types ──────────────────────────────────────────────────

export type GenerateStatus = "idle" | "loading" | "done" | "error";

export interface SubjectMeta {
  id: string;
  name: string;
  icon: string;
  description: string;
  color: string;
  borderColor: string;
  bgColor: string;
  studentCount?: number;
}

export interface GeneratedPlan {
  subjectId: string;
  generatedAt: string;
  summary: string;
  weeklyGoal: string;
  sessions: GeneratedSession[];
  tips: string[];
}

export interface GeneratedSession {
  day: string;
  duration: string;
  topic: string;
  activity: string;
}