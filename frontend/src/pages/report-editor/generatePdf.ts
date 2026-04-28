// generatePdf.ts
import jsPDF from "jspdf";
import type { ReportGeneratorResponse } from "../../service/payload";

export function generateReportPdf(
  reportData: ReportGeneratorResponse,
  namaSiswa: string,
  konten: string
): jsPDF {
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentW = pageW - margin * 2;

  // ── Header strip ──────────────────────────────────────────────────────────
  doc.setFillColor(17, 24, 39); // #111827
  doc.rect(0, 0, pageW, 32, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.setTextColor(255, 255, 255);
  doc.text("Laporan Perkembangan Siswa", margin, 14);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(180, 180, 180);
  doc.text("Digenerate oleh sistem AI", margin, 22);

  

  // ── Info card ─────────────────────────────────────────────────────────────
  let y = 42;
  doc.setFillColor(248, 249, 251);
  doc.roundedRect(margin, y, contentW, 38, 4, 4, "F");
  doc.setDrawColor(229, 231, 235);
  doc.roundedRect(margin, y, contentW, 38, 4, 4, "S");

  const fields = [
    { label: "Nama Siswa", value: namaSiswa || "-" },
    { label: "Tanggal", value: reportData.tanggal?.split("T")[0] ?? "-" },
    { label: "Tipe Laporan", value: reportData.tipe_laporan ?? "-" },
    { label: "Status", value: "Selesai" },
  ];

  const colW = contentW / fields.length;
  fields.forEach((f, i) => {
    const x = margin + i * colW + 8;
    doc.setFont("helvetica", "bold");
    doc.setFontSize(7);
    doc.setTextColor(156, 163, 175);
    doc.text(f.label.toUpperCase(), x, y + 10);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.setTextColor(17, 24, 39);
    doc.text(f.value, x, y + 20);
  });

  // ── Divider ───────────────────────────────────────────────────────────────
  y += 46;
  doc.setDrawColor(229, 231, 235);
  doc.line(margin, y, pageW - margin, y);

  // ── Konten label ──────────────────────────────────────────────────────────
  y += 10;
  doc.setFillColor(59, 130, 246, 0.1);
  doc.setDrawColor(59, 130, 246);
  doc.setLineWidth(0.8);
  doc.line(margin, y - 2, margin, y + 6);
  doc.setLineWidth(0.2);

  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(59, 130, 246);
  doc.text("LAPORAN PERKEMBANGAN", margin + 4, y + 4);

  // ── Konten body ───────────────────────────────────────────────────────────
  y += 14;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(55, 65, 81);

  const lines = doc.splitTextToSize(konten || "-", contentW);
  const lineH = 6;

  lines.forEach((line: string) => {
    if (y + lineH > pageH - margin) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += lineH;
  });

  // ── Footer ────────────────────────────────────────────────────────────────
  const totalPages = doc.getNumberOfPages();
  for (let p = 1; p <= totalPages; p++) {
    doc.setPage(p);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(156, 163, 175);
    doc.text(
      `Halaman ${p} dari ${totalPages}`,
      pageW / 2,
      pageH - 10,
      { align: "center" }
    );
    doc.text(
      `Dicetak: ${new Date().toLocaleDateString("id-ID")}`,
      pageW - margin,
      pageH - 10,
      { align: "right" }
    );
  }

  return doc;
}