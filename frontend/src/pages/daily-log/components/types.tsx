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
  jumlahSiswa: number;
  deskripsi?: string;
}

export interface FormState {
  siswa: string;
  tanggal: string;
  idMapel: string;
  mapel: string;
  topik: string;
  durasi: string;
  metode: string;
  pemahaman: TingkatPemahaman;
  keterlibatan: TingkatKeterlibatan;
  catatanGuru: string;
  rekTindakLanjut: string;
  targetMateri: string;
  skor: string;
  kompetensi: string;
  kendala: string;
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