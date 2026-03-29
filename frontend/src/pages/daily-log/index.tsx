import React, { useState } from "react";

// ── Sub-pages ─────────────────────────────────────────────────────────────────
import DailyLogIndex    from "./daily-log-index";
import DailyLogFormLog  from "./form";
import DailyLogFormMapel from "./form-makul";
import DailyListSiswa   from "./list-siswa";

// ── Types & constants ─────────────────────────────────────────────────────────
import type { LogEntry, FormState, MakulEntry, MakulFormState } from "./components/types";
import {
  INITIAL_LOG_DATA,
  INITIAL_MAKUL_DATA,
  INITIAL_SISWA_DATA,
  INITIAL_MAKUL_SISWA,
} from "./components/constants";
import DailyLogDetailSiswa from "./detail-log-siswa";

// ─── View names ───────────────────────────────────────────────────────────────
type ActiveView =
  | "index"         // Daftar semua log
  | "detailMapel"   // detail makul
  | "formLog"       // Tambah / edit log
  | "formMapel"     // Kelola mata pelajaran
  | "detailSiswa"   // detail siswa
  | "listSiswa";    // Daftar siswa

const DailyLogPage: React.FC = () => {
  const [view, setView] = useState<ActiveView>("index");

  // ── Data state ──────────────────────────────────────────────────────────────
  const [logData,   setLogData]   = useState<LogEntry[]>(INITIAL_LOG_DATA);
  const [mapelData, setmapelData] = useState<MakulEntry[]>(INITIAL_MAKUL_DATA);
  const [MapelSiswa] = useState(INITIAL_MAKUL_SISWA);
  const [siswaData]               = useState(INITIAL_SISWA_DATA);

  const [selectedMakulId, setSelectedMakulId] = useState<number | null>(null);
  const [selectedSiswaId, setSelectedSiswaId] = useState<number | null>(null);
  const [editLogId, setEditLogId] = useState<number | null>(null);

  // ── Derived: prefill form jika mode edit ────────────────────────────────────
  const selectedMakul = mapelData.find((m) => m.id === selectedMakulId) ?? null;

  const siswaUntukMapel = selectedMakulId !== null
    ? MapelSiswa
        .filter((ms) => ms.idMapel === selectedMakulId)
        .map((ms) => {
          const siswa = siswaData.find((s) => s.id === ms.idSiswa);
          return siswa
            ? { id: ms.id, idSiswa: ms.idSiswa, idMapel: ms.idMapel, nama: siswa.nama, kelas: siswa.kelas }
            : null;
        })
        .filter((s): s is NonNullable<typeof s> => s !== null)
    : [];

  const selectedSiswaEntry = siswaUntukMapel.find((s) => s.id === selectedSiswaId) ?? null;

  const editEntry = logData.find((d) => d.id === editLogId);
  const initialLogForm: Partial<FormState> | undefined = editEntry
    ? {
        siswa:        editEntry.siswa,
        mapel:        editEntry.mapel,
        topik:        editEntry.materi,
        catatanGuru:  editEntry.catatan,
        pemahaman:    editEntry.tingkat_penguasaan,
        tanggal:      editEntry.tanggal,
        durasi:       editEntry.durasi,
        metode:       editEntry.metode,
        keterlibatan: editEntry.keterlibatan,
      }
    : undefined;

  // ── Handlers: Log ───────────────────────────────────────────────────────────
  const handleOpenAdd    = () => { setEditLogId(null); setView("formMapel"); };
  const handleOpenDetail = (id: number) => { setSelectedMakulId(id); setView("listSiswa"); };

  const handleSaveLog = (form: FormState) => {
    if (editLogId !== null) {
      setLogData((prev) =>
        prev.map((d) =>
          d.id === editLogId
            ? {
                ...d,
                siswa:             form.siswa,
                idMapel:           form.idMapel,
                mapel:             form.mapel,
                materi:            form.topik || "—",
                catatan:           form.catatanGuru || "—",
                tingkat_penguasaan: form.pemahaman,
                tanggal:           form.tanggal,
                durasi:            form.durasi,
                metode:            form.metode,
                keterlibatan:      form.keterlibatan,
              }
            : d
        )
      );
    } else {
      setLogData((prev) => [
        ...prev,
        {
          id:                prev.length + 1,
          siswa:             form.siswa,
          idMapel:           form.idMapel,
          mapel:             form.mapel,
          materi:            form.topik || "—",
          catatan:           form.catatanGuru || "—",
          tingkat_penguasaan: form.pemahaman,
          tanggal:           form.tanggal,
          durasi:            form.durasi,
          metode:            form.metode,
          keterlibatan:      form.keterlibatan,
        },
      ]);
    }
    setView(selectedSiswaId !== null ? "detailSiswa" : selectedMakulId !== null ? "listSiswa" : "index");
  };

  // ── Handlers: Makul ─────────────────────────────────────────────────────────
  const handleSaveMapel = (form: MakulFormState) => {
    setmapelData((prev) => [
      ...prev,
      { id: prev.length + 1, nama: form.nama, deskripsi: form.deskripsi },
    ]);
  };

  const handleDeleteMapel = (id: number) => {
    setmapelData((prev) => prev.filter((m) => m.id !== id));
  };

  // ── Routing ───────────────────────────────────────────────────────────────── 
  if (view === "detailSiswa" && selectedSiswaEntry && selectedMakul) {
    return (
      <DailyLogDetailSiswa
        siswa={selectedSiswaEntry}
        namaMapel={selectedMakul.nama}
        logData={logData}
        onBack={() => setView("listSiswa")}
        onAddLog={() => { setEditLogId(null); setView("formLog"); }}
        onEditLog={(logId) => { setEditLogId(logId); setView("formLog"); }}
      />
    );
  }
  
  if (view === "formLog") {
    const isNewFromSiswa = editLogId === null && selectedSiswaEntry !== null;
    return (
      <DailyLogFormLog
        initialForm={initialLogForm}
        lockedSiswa={isNewFromSiswa ? selectedSiswaEntry?.nama : undefined}
        lockedMapel={isNewFromSiswa ? selectedMakul?.nama : undefined}
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
        siswaData={siswaUntukMapel}
        logData={logData}
        namaMapel={selectedMakul?.nama}
        onDetail={(makulSiswaId) => {
          setSelectedSiswaId(makulSiswaId);
          setView("detailSiswa");
        }}
        onAddSiswa={() => setView("formLog")}
        onBack={() => setView("index")}
      />
    );
  }

  // Default: index log
  return (
    <DailyLogIndex
      data={mapelData}
      onAddMakul={handleOpenAdd}
      onDetail={handleOpenDetail}
    />
  );
};

export default DailyLogPage;