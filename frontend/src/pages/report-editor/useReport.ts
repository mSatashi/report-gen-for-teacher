import { useState, useCallback } from "react";

import type { MailPayload, ReportGeneratorPayload, ReportGeneratorResponse } from "../../service/payload";
import { createReportGenerator, loadReportSiswa, submitEmail, updateReport, updateStatus } from "../../service/reportAPI";

export type ApiStatus = "idle" | "loading" | "success" | "error";

interface ReportEditorReturn {
  status: ApiStatus;
  errorMsg: string | null;
  loadReportBySiswa: (kelasId: string) => Promise<ReportGeneratorResponse[]>;
  submitReportGenerator: (payload: ReportGeneratorPayload) => Promise<ReportGeneratorResponse | null>;
  submitUpdateReportSiswa: (id: string, konten: string) => void;
  submitUpdateStatusReport: (id: string) => void;
  submitSendReport: (id: string, payload: MailPayload) => Promise<MailPayload | null>;
  resetStatus: () => void; 
}

export function useReport(): ReportEditorReturn {
  const [status, setStatus] = useState<ApiStatus>("idle");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const resetStatus = () => {
    setStatus("idle");
    setErrorMsg(null);
  };

  const loadReportBySiswa = useCallback(async (siswaId: string): Promise<ReportGeneratorResponse[]> => {
    setStatus("loading");
    setErrorMsg(null);
    try {
      const data = await loadReportSiswa(siswaId);
      setStatus("success");
      return data;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan";
      setStatus("error");
      setErrorMsg(msg);
      return [];
    }
  }, []);

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

  const submitUpdateReportSiswa = useCallback(
    async (id: string, konten: string): Promise<ReportGeneratorResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await updateReport(id, konten);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal mengupdate Report";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitUpdateStatusReport = useCallback(
    async (id: string): Promise<ReportGeneratorResponse | null> => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const data = await updateStatus(id);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal mengupdate status";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );

  const submitSendReport = useCallback(async (id: string, payload: MailPayload) => {
      setStatus("loading");
      setErrorMsg(null);
      try {
        const payloadForm = {
          email_tujuan: payload.email_tujuan,
          catatan_tambahan: payload.catatan_tambahan,
        }
        const data = await submitEmail(id, payloadForm);
        setStatus("success");
        return data;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Gagal mengupdate status";
        setStatus("error");
        setErrorMsg(msg);
        return null;
      }
    },
    []
  );


  return {
    status,
    errorMsg,
    submitReportGenerator,
    loadReportBySiswa,
    submitUpdateReportSiswa,
    submitUpdateStatusReport,
    resetStatus,
    submitSendReport,
  };
}