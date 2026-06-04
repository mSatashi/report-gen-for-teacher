import React, { useEffect } from "react";
import { adminDashboardStyles } from "./styles";
import { usePenggunaApi } from "../list-account/usePenggunaApi";
import { useSiswaApi } from "../../master-siswa/useSiswaApi";

export interface AdminDashboardProps {
  namaLengkap: string;
}

// const STATS: StatCard[] = [
//   {
//     label: "Total Pengguna",
//     value: "124",
//     sub: "↑ +8 bulan ini",
//     positive: true,
//     icon: "ti-users",
//     iconColor: "#4493f8",
//     iconBg: "#dbeafe",
//   },
//   {
//     label: "Total Siswa",
//     value: "892",
//     sub: "↑ +23 bulan ini",
//     positive: true,
//     icon: "ti-user-check",
//     iconColor: "#16a34a",
//     iconBg: "#dcfce7",
//   },
//   {
//     label: "Laporan Dibuat",
//     value: "3.471",
//     sub: "↑ +412 bulan ini",
//     positive: true,
//     icon: "ti-file-analytics",
//     iconColor: "#7c3aed",
//     iconBg: "#ede9fe",
//   },
//   {
//     label: "Kelas Aktif",
//     value: "34",
//     sub: "↓ -2 dari bulan lalu",
//     positive: false,
//     icon: "ti-door",
//     iconColor: "#b45309",
//     iconBg: "#fef3c7",
//   },
// ];


const AdminDashboard: React.FC<AdminDashboardProps> = ({ namaLengkap }) => {
  const [value, setValue] = React.useState({
    pengguna: 0,
    siswa: 0,
    laporan: 0,
    kelas: 0,
  });
  const { loadPengguna } = usePenggunaApi();
  const { loadSiswa} = useSiswaApi();

  useEffect(() => {
    loadPengguna().then((data) => {
      if (data?.length) setValue(prevState => ({
        ...prevState,
        pengguna: data.length,
      }));
    });

    loadSiswa().then((data) => {
      if (data.length) setValue(prevState => ({
        ...prevState,
        siswa: data.length,
      }));
    });
  }, []);

  const today = new Date().toLocaleDateString("id-ID", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <>
      <style>{adminDashboardStyles}</style>

      {/* Header */}
      <div className="adm-content-header">
        <h2>Selamat datang, {namaLengkap}</h2>
        <p>{today}</p>
      </div>

      {/* Stat Cards */}
      <div className="adm-stats">
        <div className="adm-stat">
          <div className="adm-stat-top">
            <div className="adm-stat-label">Total Pengguna</div>
            <div className="adm-stat-icon" style={{ background: '#dbeafe' }}>
              <i className={`ti ti-users`} style={{ color: "#4493f8" }} aria-hidden="true" />
            </div>
          </div>
          <div className="adm-stat-val">{value.pengguna}</div>
          <div className="adm-stat-sub" style={{ color: "#16a34a" }}>
            Total pengguna terdaftar.
          </div>
        </div>
        <div className="adm-stat">
          <div className="adm-stat-top">
            <div className="adm-stat-label">Total Siswa</div>
            <div className="adm-stat-icon" style={{ background: '#dbeafe' }}>
              <i className={`ti ti-user-check`} style={{ color: "#16a34a" }} aria-hidden="true" />
            </div>
          </div>
          <div className="adm-stat-val">{value.siswa}</div>
          <div className="adm-stat-sub" style={{ color: "#16a34a" }}>
            Total siswa terdaftar.
          </div>
        </div>
        {/* {STATS.map((s) => (
          <div className="adm-stat" key={s.label}>
            <div className="adm-stat-top">
              <div className="adm-stat-label">{s.label}</div>
              <div className="adm-stat-icon" style={{ background: s.iconBg }}>
                <i className={`ti ${s.icon}`} style={{ color: s.iconColor }} aria-hidden="true" />
              </div>
            </div>
            <div className="adm-stat-val">{s.value}</div>
            <div className="adm-stat-sub" style={{ color: s.positive ? "#16a34a" : "#b91c1c" }}>
              {s.sub}
            </div>
          </div>
        ))} */}
      </div>
    </>
  );
};

export default AdminDashboard;