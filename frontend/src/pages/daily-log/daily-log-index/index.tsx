import type { Kelas } from "../../../types";
import { styles } from "./styles";
import { fonts } from "../../../components/fontstyle";
import { table } from "../../../components/tablestyle";

interface DailyLogIndexProps {
  kelasList: Kelas[];
  onAddMakul: () => void;
  onDetail: (id: string) => void;
}

const DailyLogIndex: React.FC<DailyLogIndexProps> = ({ kelasList, onDetail }) => {

  /** Hitung ringkasan log per siswa */
  const getSiswaCounts = (idMapel: number) => {
    // const siswa = mapelList.filter((l) => l.idMapel === idMapel);
    // return { total: siswa.length };
    return { total: 0 };
  };

  return (
    <div style={styles.root}>

      {/* Page heading */}
      <div style={styles.headingContent}>
        <h2 style={fonts.h2}>
          Daily Log
        </h2>
        <p style={fonts.normalCoolGrey}>
          Catatan aktivitas belajar siswa
        </p>
      </div>

      {/* Card */}
      <div
        style={styles.card}
      >

        {/* Scrollable table */}
        <div style={table.tableWrapper}>
          <table style={table.table}>
            <thead>
              <tr style={table.tableHeaderRow}>
                {[
                  { label: "No", width: 50 },
                  { label: "Mata Pelajaran", width: "auto" },
                  { label: "Jumlah Siswa", width: "auto" },
                  // { label: "Deskripsi", width: "auto" },
                  { label: "Actions", width: 100 },
                ].map((h) => (
                  <th
                    key={h.label}
                    style={{ ...table.tableHeaderLabel, width: h.width }}
                  >
                    {h.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {kelasList.map((row, idx) => {
                // const { total } = getSiswaCounts(row.id);
                return (
                  <tr key={row.id} style={table.tdBorderBottom}>
                    <td style={table.tdNumber}>{idx + 1}</td>
                    <td style={table.td}>{row.mata_pelajaran}</td>
                    <td style={table.td}>{0}</td>
                    {/* <td style={{ padding: "12px 14px", color: colors.darkNavy }}>{row.deskripsi}</td> */}
                    <td style={table.tdPadding}>
                      <button
                        onClick={() => onDetail(row.id)}
                        style={styles.btnDetail}>
                        Detail
                      </button>
                    </td>
                  </tr>
                );
              })}

              {kelasList.length === 0 && (
                <tr>
                  <td colSpan={7} style={table.tdNoData}>
                    Belum ada data log.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DailyLogIndex;