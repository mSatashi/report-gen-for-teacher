export interface ReportSection {
  id: string;
  emoji: string;
  label: string;
  accentColor: string;
  content: string;
}

export interface SubjectStat {
  name: string;
  sessions: number;
  progress: number;
  color: string;
  bgColor: string;
}