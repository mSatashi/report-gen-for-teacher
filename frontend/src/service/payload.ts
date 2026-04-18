export interface KelasPayload {
  nama: string;
  mata_pelajaran: string;
  kredit: number;
  jadwal: string;
}

export interface KelasResponse {
  id: string;
  nama: string;
  mata_pelajaran: string;
  pengajar_id: string;
  kredit: number;
  jadwal: string;
  created_at: string;
}

export interface Toast { id: number; message: string; type: "success" | "error" }

export interface SiswaPayload {
  username: string;
  email_address: string;
  password?: string;
  nama: string;
  usia: string;
  level: string;
  credit_total?: number;
}
 
export interface SiswaResponse {
  id: string;
  username: string;
  email_address: string;
  nama: string;
  usia: string;
  level: string;
  credit_total: number;
  credit_used?: number;
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