export interface KelasPayload {
  nama: string;
  mata_pelajaran_id?: string;
  hari: string;
  jam: string;
}

export interface KelasResponse {
  id: string;
  nama: string;
  mata_pelajaran_id?: string;
  mata_pelajaran_obj?: MataPelajaranObj;
  pengajar_id: string;
  hari: string;
  jam: string;
  created_at: string;
}

export interface MataPelajaranObj {
  id: string;
  nama_mata_pelajaran: string;
  topik_list: TopikPayload[];
  created_at: string;
  updated_at: string;
}


export interface Toast { id: number; message: string; type: "success" | "error" }
export interface ToastMsg { id: number; msg: string; type: "success" | "error" }

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
  kelas_id: string;
  murid_id: string;
  mata_pelajaran_id: string;
  tanggal: string;
  topik?: string;
  nilai: number;
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
  id: string;
  kelas_id: string;
  murid_id: string;
  mata_pelajaran_id: string;
  tanggal: string;
  topik?: string;
  nilai: number;
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
  murid_id: string;
  waktu: string;
  daftar_rekomendasi_materi: string[];
  estimasi_waktu_selesai: string;
  catatan_analisa: string;
  is_outdated: boolean;
  jadwal_mingguan: JadwalMingguan[];
  version: number;
}

export interface JadwalMingguan {
  minggu: string; 
  topik: string[];
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
  kelas_id: string;
  periode_mulai: string;
  periode_selesai: string;
  tipe_laporan: string;
}

export interface DashboardResponse {  
  total_siswa: number;
  log_hari_ini: string;
  plan_aktif: string;
  report_pending: string;
  // aktivitas_terbaru: Record<string, string[]>;
  // progress_siswa: Record<string, string[]>;
  aktivitas_terbaru: AktivitasTerbaruResponse[]; // ← pakai type Activity
  progress_siswa: ProgressDashboardResponse[]; // ← pakai type ProgressDashboardResponse
}

export interface ProgressDashboardResponse {  
  avg_nilai: number;
  murid_id: string;
  nama: string;
  status: string;
  total_sesi: number;
}

export interface AktivitasTerbaruResponse {  
  tanggal: string;
  topik: string;
  kelas_id: string;
  murid_id: string;
  nilai: number;
  tingkat_pemahaman: string;
  tingkat_keterlibatan: string;
  nama_mata_pelajaran: string;
}

export interface MapelResponse {  
  id: string;
  nama_mata_pelajaran: string;
  topik_list: TopikPayload[];
  created_at: string;
  updated_at: string;
}

export interface MapelPayload { 
  nama_mata_pelajaran: string;
  topik_awal?: TopikPayload[];
}

export interface MapelUpdatePayload { 
  nama_mata_pelajaran: string;
  topik_list?: TopikUpdatePayload[];
}

export interface TopikResponse {
  id: string;
  nama: string;
  difficulty_index: number;
}

export interface TopikPayload {
  id?: string | null | undefined;
  nama: string;
  difficulty_index: number;
  prasyarat_ids?: string[];
}

export interface TopikUpdatePayload {
  id: string | null | undefined;
  nama: string;
  difficulty_index: number;
  prasyarat_ids: string[];
}

export interface MailPayload {
  email_tujuan: string;
  catatan_tambahan: string;
}

export interface MailResponse {
  message: string;
  laporan_id: string;
}

export interface PenggunaPayload {
  email_address: string;
  username: string;
  password: string;
  tipe_pengguna: string;
  confirmPassword?: string;
}

export interface PenggunaResponse {
  id: string;
  username: string;
  email_address: string;
  tipe_pengguna: string;
  is_active: boolean;
}