import { useState, useCallback } from "react";
import type { GenerateplanResponse } from "../../service/payload";
import { createLearningPlan, fetchPlanList } from "../../service/planAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface UseLearningPlanReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadPlan: (kelasId: string) => Promise<GenerateplanResponse[]>;
  submitGeneratePlan: (kelasId: string) => Promise<GenerateplanResponse | null>;
  resetStatus: () => void;
}

export function useLearningPlan(): UseLearningPlanReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadPlan = useCallback(async (kelasId: string): Promise<GenerateplanResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await fetchPlanList(kelasId);
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

  const submitGeneratePlan = useCallback(
    async (kelasId: string): Promise<GenerateplanResponse | null> => {
      try {
        const data = await createLearningPlan(kelasId);
        return data;
      } catch (err) {
        console.error("[useLearningPlan] submitGeneratePlan error:", err);
        return null;
      }
    },
    []
  );

  return {
    status,
    errorMsg,
    loadPlan,
    submitGeneratePlan,
    resetStatus,
  };
}