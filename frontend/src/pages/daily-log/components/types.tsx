export type TingkatPemahaman    = "Sangat Paham" | "Paham" | "Cukup" | "Perlu Review";
export type TingkatKeterlibatan = "Sangat Aktif" | "Aktif" | "Kurang Fokus";

export interface LogEntry {
  id: number;
  siswa: string;
  idMapel: number;
  mapel: string;
  materi: string;
  catatan: string;
  tingkat_penguasaan: TingkatPemahaman;
  tanggal?: string;
  durasi?: string;
  metode?: string;
  keterlibatan?: TingkatKeterlibatan;
  rekTindakLanjut?: string;
  targetMateri?: string;
  skor?: string;
  kompetensi?: string;
  kendala?: string;
}

export interface MakulEntry {
  id: number;
  nama: string;
  // jumlahSiswa: number;
  deskripsi?: string;
}

export interface FormState {
  kelas_id: string;
  murid_id: string;
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

export interface MakulFormState {
  nama: string;
  deskripsi: string;
}

export interface MapelSiswaState {
  id: number;
  idSiswa: number;
  idMapel: number;
}

// Hasil join MakulSiswa + SiswaData — yang dikirim ke DailyListSiswa
export interface SiswaJoined {
  id: number;
  idSiswa: number;
  idMapel: number;
  nama: string;
  kelas: string;
}