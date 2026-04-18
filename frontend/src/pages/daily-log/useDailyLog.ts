import { useState, useCallback } from "react";

import type { SiswaResponse } from "../../service/payload";
import { fetchSiswaByKelas } from "../../service/kelasAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseDailyLogReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadSiswaByKelas: (kelasId: string) => Promise<SiswaResponse[]>;
//   submitCreateSiswa: (payload: SiswaPayload) => Promise<SiswaResponse | null>;
//   submitUpdateSiswa: (id: string, payload: SiswaPayload) => Promise<SiswaResponse | null>;
//   submitDeleteSiswa: (id: string) => Promise<boolean>;
  resetStatus: () => void; 
}

export function useDailyLog(): UseDailyLogReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadSiswaByKelas = useCallback(async (kelasId: string): Promise<SiswaResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchSiswaByKelas(kelasId);
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  return {
    status,
    errorMsg,
    loadSiswaByKelas,
    resetStatus,
  };
}