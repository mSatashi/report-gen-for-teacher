export interface Session {
  time: string;
  subject: string;
  note: string;
  color: string;       // border-left & bg tint
  borderColor: string;
}

export interface DaySchedule {
  label: string;       // e.g. "SEN 10/3"
  sessions: Session[];
}

export interface SubjectDetail {
  name: string;
  sessions: number;
  hours: number;
  completed: number;
  color: string;       // progress bar & top border
}

export interface StatItem {
  label: string;
  value: number;
  sub: string;
  accentColor?: string;
}