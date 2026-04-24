import { useState, useCallback } from "react";
import type { DashboardResponse } from "../../service/payload";
import { fetchDashboard } from "../../service/dashboardAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseDashboardReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadDashboard: () => Promise<DashboardResponse | null>;
  resetStatus: () => void;
}

export function useDashboard(): UseDashboardReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadDashboard = useCallback(async (): Promise<DashboardResponse | null> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchDashboard();
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return null;
    }
  }, []);

  return {
    status,
    errorMsg,
    loadDashboard,
    resetStatus,
  };
}