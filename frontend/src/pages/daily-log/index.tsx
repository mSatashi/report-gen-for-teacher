import React, { useEffect, useState } from "react";

import DailyLogIndex    from "./daily-log-index";
import DailyLogFormLog  from "./form";
import DailyLogFormMapel from "./form-makul";
import DailyListSiswa   from "./list-siswa";

import type { FormState, MakulEntry, MakulFormState } from "./components/types";
import {
  INITIAL_MAKUL_DATA,
} from "./components/constants";
import DailyLogDetailSiswa from "./detail-log-siswa";
import { useKelasApi } from "../master-kelas/useKelasApi";
import type { Kelas, Siswa } from "../../types";
import type { DailyLogPayload, DailyLogResponse, KelasResponse, ReportGeneratorPayload, Toast } from "../../service/payload";
import { useDailyLog } from "./useDailyLog";
import { createReportGenerator } from "../../service/reportAPI";

type ActiveView =
  | "index"         // Daftar semua log
  | "detailMapel"   // detail makul
  | "formLog"       // Tambah / edit log
  | "formMapel"     // Kelola mata pelajaran
  | "detailSiswa"   // detail siswa
  | "listSiswa"    // Daftar siswa
  | "reportEditor";

let toastId = 0;

interface DailyLogPageProps {
  onNavigate: (route: string) => void;
}

const DailyLogPage: React.FC<DailyLogPageProps> = ({ onNavigate }) => {
  const [view, setView] = useState<ActiveView>("index");

  const [mapelData, setmapelData] = useState<MakulEntry[]>(INITIAL_MAKUL_DATA);
  const [selectedKelasId, setSelectKelasId] = useState<string | null>(null);
  const [selectedSiswaId, setSelectedSiswaId] = useState<string | null>(null);
  const [editLogId, setEditLogId] = useState<number | null>(null);

  const [kelasList, setKelasList] = useState<Kelas[]>([]);
  const [kelasSiswa, setKelasSiswa] = useState<Siswa[]>([]);
  const [kelasSiswaMap, setKelasSiswaMap] = useState<Record<string, number>>({});
  const [selectedSiswa, setSelectedSiswa] = useState<Siswa | null>(null);
  const [logDataSiswa, setLogDataSiswa] = useState<DailyLogResponse[]>([]);
  const [, setToasts] = useState<Toast[]>([]);

  const { loadKelas } = useKelasApi();
  const { loadSiswaByKelas, loadLogSiswa, submitCreateLog } = useDailyLog();

  const mapApiToKelas = (data: KelasResponse): Kelas => ({
    id: data.id,
    nama: data.nama,
    mata_pelajaran: data.mata_pelajaran,
    pengajar_id: data.pengajar_id,
    kredit: data.kredit,
    jadwal: data.jadwal,
    created_at: data.created_at,
    siswa: [],
  });

  useEffect(() => {
    loadKelas().then(async (data) => {
      if (data.length) {
        const mapped = data.map(mapApiToKelas);
        setKelasList(mapped);

        // Fetch jumlah siswa per kelas secara paralel
        const counts = await Promise.all(
          mapped.map(async (kelas) => {
            const siswa = await loadSiswaByKelas(kelas.id);
            return { id: kelas.id, count: siswa?.length ?? 0 };
          })
        );

        const map: Record<string, number> = {};
        counts.forEach(({ id, count }) => { map[id] = count; });
        setKelasSiswaMap(map);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedKelasId === null) return;
    /** handle list siswa yang ada di dalam kelas/matapelajaran */
    loadSiswaByKelas(selectedKelasId).then((data) => {
      setKelasSiswa(data);
    });
  }, [selectedKelasId]);

  useEffect(() => {
    if (selectedSiswaId === null) return;
    /** handle log siswa yang dipilih */
    loadLogSiswa(selectedSiswaId).then((data) => {
      setLogDataSiswa(data);
    });
  }, [selectedSiswaId]);


  const selectKelasData = kelasList.find((m) => m.id === selectedKelasId) ?? null;

  // const siswaUntukMapel = selectedKelasId !== null
  //   ? mapelSiswa
  //       .filter((ms) => ms.idMapel === selectedKelasId)
  //       .map((ms) => {
  //         const siswa = siswaData.find((s) => s.id === ms.idSiswa);
  //         return siswa
  //           ? { id: ms.id, idSiswa: ms.idSiswa, idMapel: ms.idMapel, nama: siswa.nama, kelas: siswa.kelas }
  //           : null;
  //       })
  //       .filter((s): s is NonNullable<typeof s> => s !== null)
  //   : [];

  // const selectedSiswaEntry = siswaUntukMapel.find((s) => s.id === selectedSiswaId) ?? null;

  const buildInitialLogForm = (
    entry: DailyLogResponse | undefined
  ): Partial<FormState> | undefined => {
    if (!entry) return undefined;
    return {
      kelas_id: entry.kelas_id,
      murid_id: entry.murid_id,
      tanggal: entry.tanggal,
      topik: entry.topik ?? "—",
      nilai: entry.nilai,
      tingkat_pemahaman: entry.tingkat_pemahaman,
      tingkat_keterlibatan: entry.tingkat_keterlibatan,
      kompetensi_dicapai: entry.kompetensi_dicapai,
      target_materi_berikutnya: entry.target_materi_berikutnya,
      kendala: entry.kendala ?? "—",
      catatan: entry.catatan ?? "—",
      durasi_menit: entry.durasi_menit,
      metode_belajar: entry.metode_belajar,
    };
  };

  const initialLogForm = buildInitialLogForm(logDataSiswa.find((d) => d.id === editLogId));

  // ── Handlers: Log ───────────────────────────────────────────────────────────
  const handleOpenAdd    = () => { setEditLogId(null); setView("formMapel"); };
  const handleOpenDetail = (id: string) => { setSelectKelasId(id); setView("listSiswa"); };
  
  const handleSaveLog = async (form: FormState) => {
    if (!selectedSiswaId || !selectedKelasId) return;

    if (editLogId !== null) {
      setLogDataSiswa((prev) =>
        prev.map((d) =>
          d.id === editLogId
            ? {
                ...d,
                materi:             form.topik ?? "—",
                catatan:            form.catatan ?? "—",
                tingkat_penguasaan: form.tingkat_pemahaman,
                tanggal:            form.tanggal,
                durasi:             form.durasi_menit,
                metode:             form.metode_belajar,
                keterlibatan:       form.tingkat_keterlibatan,
              }
            : d
        )
      );
    } else {
      const payload: DailyLogPayload = {
        kelas_id: selectedSiswaId,
        murid_id: selectedSiswaId,
        tanggal: form.tanggal,
        topik: form.topik ?? "—",
        nilai: form.nilai,
        tingkat_pemahaman: form.tingkat_pemahaman,
        tingkat_keterlibatan: form.tingkat_keterlibatan,
        kompetensi_dicapai: form.kompetensi_dicapai,
        target_materi_berikutnya: form.target_materi_berikutnya,
        kendala: form.kendala ?? "—",
        catatan: form.catatan ?? "—",
        durasi_menit: form.durasi_menit,
        metode_belajar: form.metode_belajar,
      };

      const result = await submitCreateLog(payload);
      if (result) {
        setLogDataSiswa((prev) => [...prev, result]);
      } else {
        return; // gagal, jangan pindah view
      }
    }

    setView(selectedSiswaId !== null ? "detailSiswa" : selectedKelasId !== null ? "listSiswa" : "index");
  };
  
  const handleSaveMapel = (form: MakulFormState) => {
    setmapelData((prev) => [
      ...prev,
      { id: prev.length + 1, nama: form.nama, deskripsi: form.deskripsi },
    ]);
  };

  const handleDeleteMapel = (id: number) => {
    setmapelData((prev) => prev.filter((m) => m.id !== id));
  };

  
  const showToast = (message: string, type: "success" | "error") => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  };

  const handleGenerate = async (siswaId: string, kelasId: string) => {
    const payload: ReportGeneratorPayload = {
      murid_id: siswaId,
      kelas_id: kelasId,
    };

    const result = await createReportGenerator(payload);
    if (result) {
      showToast("Kelas berhasil diperbarui ✓", "success");
      onNavigate("reportEditor");
    } else {
      return;
    }
  }

  
  if (view === "detailSiswa") {
    if (!selectedSiswa) return null;
    return (
      <DailyLogDetailSiswa
        dataSiswa={selectedSiswa}
        dataKelas={selectKelasData}
        logDataSiswa={logDataSiswa}
        // onBack={() => setView("listSiswa")}
        // onAddLog={() => { setEditLogId(null); setView("formLog"); }}
        // onEditLog={(logId) => { setEditLogId(logId); setView("formLog"); }}
        onBack={() => setView("listSiswa")}
        onBackToIndex={() => setView("index")}   // ✅
        onAddLog={() => { setEditLogId(null); setView("formLog"); }}
        onEditLog={(logId) => { setEditLogId(logId); setView("formLog"); }}
      />
    );
  }
  
  if (view === "formLog") {
    const isNewFromSiswa = editLogId === null && selectedSiswa !== null;
    return (
      <DailyLogFormLog
        initialForm={initialLogForm}
        lockedSiswa={isNewFromSiswa ? selectedSiswa?.nama : undefined}
        lockedMapel={isNewFromSiswa ? selectKelasData?.mata_pelajaran : undefined}
        onBack={() => setView(selectedSiswaId !== null ? "detailSiswa" : "listSiswa")}
        onSave={handleSaveLog}
      />
    );
  }

  if (view === "formMapel") {
    return (
      <DailyLogFormMapel
        data={mapelData}
        onBack={() => setView("index")}
        onSave={handleSaveMapel}
        onDelete={handleDeleteMapel}
      />
    );
  }

  if (view === "listSiswa") {
    return (
      <DailyListSiswa
        kelasSiswa={kelasSiswa}
        logDataSiswa={logDataSiswa}
        dataKelas={selectKelasData}
        onDetail={(siswaId) => {          
          const siswa = kelasSiswa.find((s) => s.id === siswaId);
          console.log("siswa ditemukan:", siswa);
          
          setSelectedSiswa(siswa ?? null);
          setSelectedSiswaId(siswaId);
          setView("detailSiswa");
        }}
        onGenerate={handleGenerate}
        onAddSiswa={() => setView("formLog")}
        onBack={() => setView("index")}
      />
    );
  }

  // Default: index log
  return (
    <DailyLogIndex
      kelasList={kelasList}
      kelasSiswaMap={kelasSiswaMap}
      onAddMakul={handleOpenAdd}
      onDetail={handleOpenDetail}
    />
  );
};

export default DailyLogPage;