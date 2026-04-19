import { useState, useCallback } from "react";
import {
  createKelas,
  updateKelas,
  deleteKelasApi,
  fetchKelasList,
  addSiswaKelas,
  siswaDalamKelas,
  deleteSiswaKelas,
} from "../../service/kelasAPI";
import type { addSiswaPayload, KelasPayload, KelasResponse, messageResponse, SiswaResponse } from "../../service/payload";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseKelasApiReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadKelas: () => Promise<KelasResponse[]>;
  submitCreateKelas: (payload: KelasPayload) => Promise<KelasResponse | null>;
  submitUpdateKelas: (id: string, payload: KelasPayload) => Promise<KelasResponse | null>;
  submitDeleteKelas: (id: string) => Promise<boolean>;
  loadSiswaKelas: (kelasId: string) => Promise<SiswaResponse[] | null>;
  addSiswa: (kelasId: string, payload: addSiswaPayload) => Promise<messageResponse | null>;
  submitDeleteSiswaKelas: (kelasId: string, siswaId: string) => Promise<boolean>;
  resetStatus: () => void;
}

export function useKelasApi(): UseKelasApiReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadKelas = useCallback(async (): Promise<KelasResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchKelasList();
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  const submitCreateKelas = useCallback(
    async (payload: KelasPayload): Promise<KelasResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await createKelas(payload);
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

  const submitUpdateKelas = useCallback(
    async (id: string, payload: KelasPayload): Promise<KelasResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await updateKelas(id, payload);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal mengupdate kelas";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitDeleteKelas = useCallback(async (id: string): Promise<boolean> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      await deleteKelasApi(id);
      setStatus("success");
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal menghapus kelas";
      setStatus("error");
      setErrorMsg(msg);
      return false;
    }
  }, []);

  const loadSiswaKelas = useCallback(
    async (kelasId: string): Promise<SiswaResponse[] | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await siswaDalamKelas(kelasId);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal memuat siswa";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const addSiswa = useCallback(
    async (kelasId: string, payload: addSiswaPayload): Promise<messageResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await addSiswaKelas(kelasId, payload);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal menambahkan siswa";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitDeleteSiswaKelas = useCallback(async (kelasId: string, siswaId: string): Promise<boolean> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      await deleteSiswaKelas(kelasId, siswaId);
      setStatus("success");
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal menghapus siswa";
      setStatus("error");
      setErrorMsg(msg);
      return false;
    }
  }, []);

  // interface UseSiswaApiReturn {
  //   siswaStatus: ApiStatus;
  //   siswaErrorMsg: string | null;
  //   loadSiswa: (kelasId: string) => Promise<SiswaResponse[]>;
  //   submitCreateSiswa: (kelasId: string, payload: SiswaPayload) => Promise<SiswaResponse | null>;
  //   submitUpdateSiswa: (siswaId: string, payload: SiswaPayload) => Promise<SiswaResponse | null>;
  //   submitDeleteSiswa: (siswaId: string) => Promise<boolean>;
  // }
 
// export function useSiswaApi(): UseSiswaApiReturn {
//   const [siswaStatus, setSiswaStatus] = useState<ApiStatus>("idle");
//   const [siswaErrorMsg, setSiswaErrorMsg] = useState<string | null>(null);
 
//   const loadSiswa = useCallback(async (kelasId: string): Promise<SiswaResponse[]> => {
//     setSiswaStatus("loading");
//     setSiswaErrorMsg(null);
//     try {
//       const data = await fetchSiswaByKelas(kelasId);
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
//     async (kelasId: string, payload: SiswaPayload): Promise<SiswaResponse | null> => {
//       setSiswaStatus("loading");
//       setSiswaErrorMsg(null);
//       try {
//         const data = await createSiswa(kelasId, payload);
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
 


  return {
    status,
    errorMsg,
    loadKelas,
    submitCreateKelas,
    submitUpdateKelas,
    submitDeleteKelas,
    loadSiswaKelas,
    addSiswa,
    submitDeleteSiswaKelas,
    resetStatus,
  };
}