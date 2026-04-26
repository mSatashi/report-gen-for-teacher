import { useState, useCallback } from "react";
import type { ReportGeneratorPayload, ReportGeneratorResponse } from "../../service/payload";
import { createReportGenerator } from "../../service/reportAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseReportGeneratorApiReturn {
  status: ApiStatus;
  errorMsg: string | null;
  submitCreateReportGenerator: (kelasId: string, siswaId: string, payload: ReportGeneratorPayload) => Promise<ReportGeneratorResponse | null>;
  resetStatus: () => void;
}

export function useReportGeneratorApi(): UseReportGeneratorApiReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

//   const loadKelas = useCallback(async (): Promise<KelasResponse[]> => {
//     setStatus("loading");
//     setErrorMsg(null);
//     try {
//       const data = await fetchKelasList();
//       setStatus("success");
//       return data;
//     } catch (err) {
//       const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
//       setStatus("error");
//       setErrorMsg(msg);
//       return [];
//     }
//   }, []);

  const submitCreateReportGenerator = useCallback(
    async (kelasId: string, siswaId: string, payload: ReportGeneratorPayload): Promise<ReportGeneratorResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await createReportGenerator(kelasId, siswaId, payload);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal membuat kelas";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

//   const submitUpdateKelas = useCallback(
//     async (id: string, payload: KelasPayload): Promise<KelasResponse | null> => {
//       setStatus("loading");
//       setErrorMsg(null);
//       try {
//         const data = await updateKelas(id, payload);
//         setStatus("success");
//         return data;
//       } catch (err) {
//         const msg = err instanceof Error ? err.message : "Gagal mengupdate kelas";
//         setStatus("error");
//         setErrorMsg(msg);
//         return null;
//       }
//     },
//     []
//   );

  return {
    status,
    errorMsg,
    submitCreateReportGenerator,
    resetStatus,
  };
}