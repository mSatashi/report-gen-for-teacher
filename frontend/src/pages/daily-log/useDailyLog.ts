import { useState, useCallback } from "react";

import type { DailyLogPayload, DailyLogResponse, SiswaResponse } from "../../service/payload";
import { fetchSiswaByKelas } from "../../service/kelasAPI";
import { createDailyLog, fetchLogSiswa } from "../../service/dailyLogAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseDailyLogReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadSiswaByKelas: (kelasId: string) => Promise<SiswaResponse[]>;
  loadLogSiswa: (siswaId: string) => Promise<DailyLogResponse[]>;
  submitCreateLog: (payload: DailyLogPayload) => Promise<DailyLogResponse | null>;
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

  const loadLogSiswa = useCallback(async (siswaId: string): Promise<DailyLogResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchLogSiswa(siswaId);
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  const submitCreateLog = useCallback(
  async (payload: DailyLogPayload): Promise<DailyLogResponse | null> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await createDailyLog(payload);
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal membuat log";
      setStatus("error");
      setErrorMsg(msg);
      return null;
    }
  }, []);

  return {
    status,
    errorMsg,
    loadSiswaByKelas,
    loadLogSiswa,
    submitCreateLog,
    resetStatus,
  };
}