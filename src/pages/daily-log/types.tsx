export type TingkatPemahaman    = "Sangat Paham" | "Paham" | "Cukup" | "Perlu Review";
export type TingkatKeterlibatan = "Sangat Aktif" | "Aktif" | "Kurang Fokus";

export interface LogEntry {
  id: number;
  mapel: string;
  materi: string;
  catatan: string;
  tingkat_penguasaan: TingkatPemahaman;
}

export interface FormState {
  siswa: string;
  tanggal: string;
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