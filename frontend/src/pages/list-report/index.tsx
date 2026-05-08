import { useEffect, useMemo, useState } from "react";
import { styles } from "./styles";
import {IconReport } from "../../icons";
import type { Siswa } from "../../types";
import { useSiswaApi } from "../master-siswa/useSiswaApi";
import type { SiswaResponse } from "../../service/payload";

type Props = {
  initialData?: Siswa[];
  onNavigate?: (route: string, params?: Record<string, unknown>) => void;
};

export default function ListReportGenerator({ onNavigate, initialData = [] }: Props) {
  const [siswaList, setSiswaList] = useState<Siswa[]>(initialData);
  const [keyword,] = useState("");

  const { loadSiswa } = useSiswaApi();


  const filteredSiswa = useMemo(() => {
    const q = keyword.trim().toLowerCase();

    return siswaList.filter((s) => {
      if (!q) return true;

      return (
        s.email_address.toLowerCase().includes(q) ||
        s.nama.toLowerCase().includes(q) ||
        s.jenis_kelamin.toLowerCase().includes(q) ||
        s.education_level.toLowerCase().includes(q)
      );
    });
  }, [siswaList, keyword]);

  
  const mapApiToSiswa = (data: SiswaResponse): Siswa => ({
    id: data.id,
    nama: data.nama,
    email_address: data.email_address,
    jenis_kelamin: data.jenis_kelamin,
    education_level: data.education_level,
    is_active: data.is_active,
  });

  useEffect(() => {
    loadSiswa().then((data) => {
      if (data.length) setSiswaList(data.map(mapApiToSiswa));
    });
  }, []);

  return (
    <div style={styles.root}>
      <div style={styles.header}>
        <h2 style={styles.title}>Data Siswa</h2>
        <p style={styles.subtitle}>Kelola report siswa yang digenerate</p>
      </div>

      <div
        style={styles.wrapperCard}
      >
          <div
            style={styles.toolbar}
          >
            <div>
              <div style={styles.labelCard}>
                Daftar Siswa
              </div>
              <div style={styles.subLabelCard}>
                {filteredSiswa.length} siswa ditemukan
              </div>
            </div>
          </div>

        {filteredSiswa.length === 0 ? (
          <div style={styles.emptyState}>
            <div style={{ fontSize: "28px", marginBottom: "10px" }}>👥</div>
            Belum ada siswa terdaftar.
          </div>
        ) : (
          <div style={styles.tableWrapper}>
            <table style={styles.mapelTable}>
              <thead>
                <tr>
                  <th style={{ ...styles.th, width: "50px"}}>#</th>
                  <th style={{ ...styles.th, width: "200px"}}>Nama Siswa</th>
                  <th style={{ ...styles.th, width: "300px"}}>Email Address</th>
                  <th style={{ ...styles.th, width: "250px"}}>Jenis Kelamin</th>
                  <th style={{ ...styles.th, width: "200px"}}>Level</th>
                </tr>
              </thead>
              <tbody>
                {filteredSiswa.map((s, i) => (
                  <tr key={s.id}>
                    <td style={styles.td}>{i + 1}</td>
                    <td style={styles.td}>{s.nama}</td>
                    <td style={styles.td}>{s.email_address}</td>
                    <td style={styles.td}>{s.jenis_kelamin || "-"}</td>
                    <td style={styles.td}>{s.education_level || "-"}</td>
                    <td style={styles.td}>
                      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); onNavigate?.('detailReport', { reportData: s, siswaId: s.id}); }}
                          style={styles.btnLihat}
                          title="Detail"
                        >
                          <IconReport />
                          Lihat
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}