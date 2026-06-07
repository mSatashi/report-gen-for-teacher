import { useState, useCallback } from "react";
import type { MapelPayload, MapelResponse, MapelUpdatePayload, TopikResponse } from "../../service/payload";
import { createMapel, deleteMapelApi, fetchMapelList, fetchTopikList, updateMapel } from "../../service/mapelAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseMapelApiReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadMapelList: () => Promise<MapelResponse[]>;
  loadTopikList: (idMapel: string) => Promise<TopikResponse[]>;
  submitCreateMapel: (payload: MapelPayload) => Promise<MapelResponse | null>;
  submitUpdateMapel: (payload: MapelPayload, idMapel: string) => Promise<MapelResponse | null>;
  submitDeleteMapel: (mapelId: string) => Promise<boolean>;
  resetStatus: () => void;
}

export function useMapelApi(): UseMapelApiReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadMapelList = useCallback(async (): Promise<MapelResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchMapelList();
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  const submitCreateMapel = useCallback(
    async (payload: MapelPayload): Promise<MapelResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await createMapel(payload);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal membuat mata pelajaran";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitUpdateMapel = useCallback(
    async (payload: MapelUpdatePayload, idMapel: string): Promise<MapelResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await updateMapel(payload, idMapel);
        // console.log("Mapel updated:", data);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal memperbarui mata pelajaran";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitDeleteMapel = useCallback(async (mapelId: string): Promise<boolean> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      await deleteMapelApi(mapelId);
      setStatus("success");
      return true;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal menghapus mata pelajaran";
      setStatus("error");
      setErrorMsg(msg);
      return false;
    }
  }, []);

  const loadTopikList = useCallback(async (idMapel: string): Promise<TopikResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchTopikList(idMapel);
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
    loadMapelList,
    loadTopikList,
    submitCreateMapel,
    submitUpdateMapel,
    submitDeleteMapel,
    resetStatus,
  };
}