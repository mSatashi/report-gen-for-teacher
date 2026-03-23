import React, { useState } from "react";
import DailyLogIndex from "./dailyLogIndex";
import DailyLogForm  from "./dailyLogForm";
import { INITIAL_DATA } from "./constants";
import type { LogEntry, FormState } from "./types";

type ActiveView = "index" | "form";

const DailyLogPage: React.FC = () => {
  const [view,   setView]   = useState<ActiveView>("index");
  const [data,   setData]   = useState<LogEntry[]>(INITIAL_DATA);
  const [editId, setEditId] = useState<number | null>(null);

  const editEntry = data.find((d) => d.id === editId);
  const initialForm: Partial<FormState> | undefined = editEntry
    ? { mapel: editEntry.mapel, topik: editEntry.materi, catatanGuru: editEntry.catatan, pemahaman: editEntry.tingkat_penguasaan }
    : undefined;

  const handleOpenAdd    = ()           => { setEditId(null); setView("form"); };
  const handleOpenDetail = (id: number) => { setEditId(id);   setView("form"); };

  const handleSave = (form: FormState) => {
    if (editId !== null) {
      setData((prev) =>
        prev.map((d) =>
          d.id === editId
            ? { ...d, mapel: form.mapel, materi: form.topik || "—", catatan: form.catatanGuru || "—", tingkat_penguasaan: form.pemahaman }
            : d
        )
      );
    } else {
      setData((prev) => [...prev, {
        id: prev.length + 1,
        mapel: form.mapel,
        materi: form.topik || "—",
        catatan: form.catatanGuru || "—",
        tingkat_penguasaan: form.pemahaman,
      }]);
    }
    setView("index");
  };

  if (view === "form") {
    return <DailyLogForm initialForm={initialForm} onBack={() => setView("index")} onSave={handleSave} />;
  }

  return <DailyLogIndex data={data} onAdd={handleOpenAdd} onDetail={handleOpenDetail} />;
};

export default DailyLogPage;