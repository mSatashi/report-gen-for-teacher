import { useState, useCallback } from "react";

import type { ReportGeneratorPayload, ReportGeneratorResponse } from "../../service/payload";
import { createReportGenerator } from "../../service/reportAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface ReportEditorReturn {
  status: ApiStatus;
  errorMsg: string | null;
//   loadSiswaByKelas: (kelasId: string) => Promise<SiswaResponse[]>;
//   loadLogSiswa: (siswaId: string) => Promise<DailyLogResponse[]>;
  submitReportGenerator: (payload: ReportGeneratorPayload) => Promise<ReportGeneratorResponse | null>;
  resetStatus: () => void; 
}

export function useReport(): ReportEditorReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

//   const loadSiswaByKelas = useCallback(async (kelasId: string): Promise<SiswaResponse[]> => {
//     setStatus("loading");
//     setErrorMsg(null);
//     try {
//       const data = await fetchSiswaByKelas(kelasId);
//       setStatus("success");
//       return data;
//     } catch (err) {
//       const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
//       setStatus("error");
//       setErrorMsg(msg);
//       return [];
//     }
//   }, []);

  const submitReportGenerator = useCallback(
  async (payload: ReportGeneratorPayload): Promise<ReportGeneratorResponse | null> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await createReportGenerator(payload);
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
    submitReportGenerator,
    resetStatus,
  };
}