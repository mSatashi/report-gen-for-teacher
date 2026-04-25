import { useState, useCallback } from "react";
import type { DailyLogResponse } from "../../service/payload";
import { fetchLogSiswa } from "../../service/dailyLogAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface useDailyLogSiswaReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadLogSiswa: (siswaId: string) => Promise<DailyLogResponse[]>;
  resetStatus: () => void;
}

export function useDailyLogSiswa(): useDailyLogSiswaReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

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

//   const submitCreateKelas = useCallback(
//     async (payload: KelasPayload): Promise<KelasResponse | null> => {
//       setStatus("loading");
//       setErrorMsg(null);
//       try {
//         const data = await createKelas(payload);
//         setStatus("success");
//         return data;
//       } catch (err) {
//         const msg = err instanceof Error ? err.message : "Gagal membuat kelas";
//         setStatus("error");
//         setErrorMsg(msg);
//         return null;
//       }
//     },
//     []
//   );

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

//   const submitDeleteKelas = useCallback(async (id: string): Promise<boolean> => {
//     setStatus("loading");
//     setErrorMsg(null);
//     try {
//       await deleteKelasApi(id);
//       setStatus("success");
//       return true;
//     } catch (err) {
//       const msg = err instanceof Error ? err.message : "Gagal menghapus kelas";
//       setStatus("error");
//       setErrorMsg(msg);
//       return false;
//     }
//   }, []); 


  return {
    status,
    errorMsg,
    loadLogSiswa,
    // submitCreateKelas,
    // submitUpdateKelas,
    // submitDeleteKelas,
    // loadSiswaKelas,
    // addSiswa,
    // submitDeleteSiswaKelas,
    resetStatus,
  };
}