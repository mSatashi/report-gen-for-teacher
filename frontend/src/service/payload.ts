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