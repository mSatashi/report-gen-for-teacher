import { useState, useCallback } from "react";
import type { PenggunaPayload, PenggunaResponse } from "../../../service/payload";
import { createPengguna, deletePenggunaApi, fetchPenggunaList } from "../../../service/accountAPI";



export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UsePenggunaApiReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadPengguna: () => Promise<PenggunaResponse[]>;
  submitPengguna: (payload: PenggunaPayload) => Promise<PenggunaResponse | null>;
  sumbitDeletePengguna: (id: string) => Promise<boolean>;
  resetStatus: () => void; 
}

export function usePenggunaApi(): UsePenggunaApiReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadPengguna = useCallback(async (): Promise<PenggunaResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchPenggunaList();
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  const submitPengguna = useCallback(
    async (payload: PenggunaPayload): Promise<PenggunaResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await createPengguna(payload);
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

  const sumbitDeletePengguna = useCallback(async (id: string): Promise<boolean> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      await deletePenggunaApi(id);
      setStatus("success");
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal menghapus Pengguna";
      setStatus("error");
      setErrorMsg(msg);
      return false;
    }
  }, []);

  return {
    status,
    errorMsg,
    loadPengguna,
    submitPengguna,
    sumbitDeletePengguna,
    resetStatus,
  };
}