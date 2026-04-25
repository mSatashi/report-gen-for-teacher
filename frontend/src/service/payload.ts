import type { Activity, Student } from "../types";

export interface KelasPayload {
  nama: string;
  mata_pelajaran: string;
  kredit: number;
  jadwal: string;
}

export interface KelasResponse {
  id: string;
  nama: string;
  mata_pelajaran_id: string;
  mata_pelajaran_obj: MataPelajaranObj;
  pengajar_id: string;
  hari: string;
  jam: string;
  created_at: string;
}

export interface MataPelajaranObj {
  id: string;
  nama_mata_pelajaran: string;
  topik: string[];
  created_at: string;
  updated_at: string;
}


export interface Toast { id: number; message: string; type: "success" | "error" }

export interface SiswaPayload {
  email_address: string;
  nama: string;
  jenis_kelamin: string;
  education_level: string;
  is_active: boolean;
}
 
export interface SiswaResponse {
  id: string;
  email_address: string;
  nama: string;
  jenis_kelamin: string;
  education_level: string;
  is_active: boolean;
}

export interface addSiswaPayload {
  murid_id: string,
}

export interface messageResponse {
  message: string;
}

export interface DailyLogPayload {
  // siswa: string;
  // mapel: string;
  // catatanGuru?: string;
  // pemahaman: string;
  // durasi: string;
  // metode: string;
  // keterlibatan: string;
  
  kelas_id: string;
  murid_id: string;
  tanggal: string;
  topik?: string;
  nilai: Float32Array;
  tingkat_pemahaman: string;
  tingkat_keterlibatan: string;
  kompetensi_dicapai: string;
  target_materi_berikutnya: string;
  kendala?: string;
  catatan?: string;
  durasi_menit: number;
  metode_belajar: string;
}


export interface DailyLogResponse {
  id: number;
  // siswa: string;
  // idMapel: number;
  // mapel: string;
  // materi: string;
  // catatan: string;
  // tingkat_penguasaan: string;
  // tanggal: string;
  // durasi: string;
  // metode: string;
  // keterlibatan: string;
  kelas_id: string;
  murid_id: string;
  tanggal: string;
  topik?: string;
  nilai: Float32Array;
  tingkat_pemahaman: string;
  tingkat_keterlibatan: string;
  kompetensi_dicapai: string;
  target_materi_berikutnya: string;
  kendala?: string;
  catatan?: string;
  durasi_menit: number;
  metode_belajar: string;
  created_at: string;
}

export interface GenerateplanResponse {
  id: string;
  kelas_id: string;
  murid_id?: string;
  waktu: string;
  daftar_rekomendasi_materi: string[];
  estimasi_waktu_selesai: string;
  catatan_analisa: string;
  jadwal_mingguan: Record<string, string[]>;
  version: number;
}

export interface ReportGeneratorResponse {
  id: string;
  murid_id: string;
  kelas_id: string;
  konten: string;
  tipe_laporan: string;
  status: string;
  pdf_path: string;
  tanggal: string;
  tanggal_dikirim?: string;
  is_ai_generated: boolean;
  periode_mulai: string;
  periode_selesai: string;
}

export interface ReportGeneratorPayload {  
  murid_id: string;
  kelas_id?: string;
  periode_mulai?: string;
  periode_selesai?: string;
  tipe_laporan?: string;
}

export interface DashboardResponse {  
  total_siswa: number;
  log_hari_ini: number;
  plan_aktif: number;
  report_pending: number;
  // aktivitas_terbaru: Record<string, string[]>;
  // progress_siswa: Record<string, string[]>;
  aktivitas_terbaru: Activity[]; // ← pakai type Activity
  progress_siswa: Student[];
}

export interface MapelResponse {  
  id: string;
  nama_mata_pelajaran: string;
  topik: string[];
  created_at: string;
  updated_at: string;
}

export interface MapelPayload {  
  nama_mata_pelajaran: string;
  topik: string[];
}