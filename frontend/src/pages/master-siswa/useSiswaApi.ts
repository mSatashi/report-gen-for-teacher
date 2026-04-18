import { useState, useCallback } from "react";

import type { SiswaPayload, SiswaResponse } from "../../service/payload";
import { createSiswa, deleteSiswaApi, fetchSiswaList, updateSiswa } from "../../service/siswaAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseSiswaApiReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadSiswa: () => Promise<SiswaResponse[]>;
  submitCreateSiswa: (payload: SiswaPayload) => Promise<SiswaResponse | null>;
  submitUpdateSiswa: (id: string, payload: SiswaPayload) => Promise<SiswaResponse | null>;
  submitDeleteSiswa: (id: string) => Promise<boolean>;
  resetStatus: () => void; 
}

export function useSiswaApi(): UseSiswaApiReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadSiswa = useCallback(async (): Promise<SiswaResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchSiswaList();
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  const submitCreateSiswa = useCallback(
    async (payload: SiswaPayload): Promise<SiswaResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await createSiswa(payload);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal membuat Siswa";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitUpdateSiswa = useCallback(
    async (id: string, payload: SiswaPayload): Promise<SiswaResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await updateSiswa(id, payload);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal mengupdate Siswa";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitDeleteSiswa = useCallback(async (id: string): Promise<boolean> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      await deleteSiswaApi(id);
      setStatus("success");
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal menghapus Siswa";
      setStatus("error");
      setErrorMsg(msg);
      return false;
    }
  }, []);

  // interface UseSiswaApiReturn {
  //   siswaStatus: ApiStatus;
  //   siswaErrorMsg: string | null;
  //   loadSiswa: (SiswaId: string) => Promise<SiswaResponse[]>;
  //   submitCreateSiswa: (SiswaId: string, payload: SiswaPayload) => Promise<SiswaResponse | null>;
  //   submitUpdateSiswa: (siswaId: string, payload: SiswaPayload) => Promise<SiswaResponse | null>;
  //   submitDeleteSiswa: (siswaId: string) => Promise<boolean>;
  // }
 
// export function useSiswaApi(): UseSiswaApiReturn {
//   const [siswaStatus, setSiswaStatus] = useState<ApiStatus>("idle");
//   const [siswaErrorMsg, setSiswaErrorMsg] = useState<string | null>(null);
 
//   const loadSiswa = useCallback(async (SiswaId: string): Promise<SiswaResponse[]> => {
//     setSiswaStatus("loading");
//     setSiswaErrorMsg(null);
//     try {
//       const data = await fetchSiswaBySiswa(SiswaId);
//       setSiswaStatus("success");
//       return data;
//     } catch (err) {
//       const msg = err instanceof Error ? err.message : "Gagal memuat siswa";
//       setSiswaStatus("error");
//       setSiswaErrorMsg(msg);
//       return [];
//     }
//   }, []);
 
//   const submitCreateSiswa = useCallback(
//     async (SiswaId: string, payload: SiswaPayload): Promise<SiswaResponse | null> => {
//       setSiswaStatus("loading");
//       setSiswaErrorMsg(null);
//       try {
//         const data = await createSiswa(SiswaId, payload);
//         setSiswaStatus("success");
//         return data;
//       } catch (err) {
//         const msg = err instanceof Error ? err.message : "Gagal menambahkan siswa";
//         setSiswaStatus("error");
//         setSiswaErrorMsg(msg);
//         return null;
//       }
//     },
//     []
//   );
 
//   const submitUpdateSiswa = useCallback(
//     async (siswaId: string, payload: SiswaPayload): Promise<SiswaResponse | null> => {
//       setSiswaStatus("loading");
//       setSiswaErrorMsg(null);
//       try {
//         const data = await updateSiswa(siswaId, payload);
//         setSiswaStatus("success");
//         return data;
//       } catch (err) {
//         const msg = err instanceof Error ? err.message : "Gagal mengupdate siswa";
//         setSiswaStatus("error");
//         setSiswaErrorMsg(msg);
//         return null;
//       }
//     },
//     []
//   );
 
//   const submitDeleteSiswa = useCallback(async (siswaId: string): Promise<boolean> => {
//     setSiswaStatus("loading");
//     setSiswaErrorMsg(null);
//     try {
//       await deleteSiswaApi(siswaId);
//       setSiswaStatus("success");
//       return true;
//     } catch (err) {
//       const msg = err instanceof Error ? err.message : "Gagal menghapus siswa";
//       setSiswaStatus("error");
//       setSiswaErrorMsg(msg);
//       return false;
//     }
//   }, []);

  return {
    status,
    errorMsg,
    loadSiswa,
    submitCreateSiswa,
    submitUpdateSiswa,
    submitDeleteSiswa,
    resetStatus,

    // siswaStatus,
    // siswaErrorMsg,
    // loadSiswa,
    // submitCreateSiswa,
    // submitUpdateSiswa,
    // submitDeleteSiswa,
  };
}