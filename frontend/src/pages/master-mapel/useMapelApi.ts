import { useState, useCallback } from "react";
import type { MapelPayload, MapelResponse } from "../../service/payload";
import { createMapel, deleteMapelApi, fetchMapelList, updateMapel } from "../../service/mapelAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseMapelApiReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadMapelList: () => Promise<MapelResponse[]>;
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
    async (payload: MapelPayload, idMapel: string): Promise<MapelResponse | null> => {
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

  return {
    status,
    errorMsg,
    loadMapelList,
    submitCreateMapel,
    submitUpdateMapel,
    submitDeleteMapel,
    resetStatus,
  };
}