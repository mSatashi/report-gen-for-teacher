"""
report_service.py
Service layer untuk Laporan Perkembangan Siswa.
F003, F005, F006, F007 — buat, edit, kirim, lihat, hapus laporan.
Termasuk: generate PDF, kirim email, dan Hybrid Rule-Based Fallback untuk AI.
"""
import logging
import os
import uuid
from datetime import datetime
from typing import List, Optional

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Laporan, Murid, LogPertemuan, KnowledgeState, MataPelajaran
from app.schemas.schemas import LaporanCreate, LaporanUpdate
from app.ai.ai_service import narrative_engine

logger = logging.getLogger(__name__)
os.makedirs(settings.UPLOAD_DIR + "pdf/", exist_ok=True)


# ── CRUD Laporan ──────────────────────────────────────────────────────────────

def get_laporan_by_id(db: Session, laporan_id: str) -> Optional[Laporan]:
    return db.query(Laporan).filter(Laporan.id == laporan_id).first()


def get_laporan_by_murid(
    db: Session, murid_id: str, skip: int = 0, limit: int = 50
) -> List[Laporan]:
    return (
        db.query(Laporan)
        .filter(Laporan.murid_id == murid_id)
        .order_by(Laporan.tanggal.desc())
        .offset(skip).limit(limit).all()
    )


def get_laporan_pending(db: Session, pengajar_id: str) -> List[Laporan]:
    from app.models.models import Kelas
    kelas_ids =[k.id for k in db.query(Kelas).filter(Kelas.pengajar_id == pengajar_id).all()]
    return (
        db.query(Laporan)
        .filter(Laporan.kelas_id.in_(kelas_ids), Laporan.status != "terkirim")
        .all()
    )


def update_laporan(db: Session, laporan_id: str, data: LaporanUpdate) -> Optional[Laporan]:
    lap = get_laporan_by_id(db, laporan_id)
    if not lap:
        return None
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(lap, field, val)
    db.commit()
    db.refresh(lap)
    return lap


def finalize_laporan(db: Session, laporan_id: str) -> Optional[Laporan]:
    return update_laporan(db, laporan_id, LaporanUpdate(status="final"))


def delete_laporan(db: Session, laporan_id: str) -> bool:
    """Hapus laporan dan file PDF yang terkait dari penyimpanan fisik."""
    lap = get_laporan_by_id(db, laporan_id)
    if not lap:
        return False
    
    # Hapus file fisik PDF jika ada
    if lap.pdf_path and os.path.exists(lap.pdf_path):
        try:
            os.remove(lap.pdf_path)
        except Exception as e:
            logger.warning(f"Gagal menghapus file PDF {lap.pdf_path}: {e}")
            
    db.delete(lap)
    db.commit()
    return True


# ── Rule-Based Fallback ───────────────────────────────────────────────────────

def generate_fallback_template(nama_murid: str, mata_pelajaran: str, log_data: list, pso_recommended_route: Optional[str]) -> str:
    """
    Template otomatis berbasis aturan (Rule-based). Digunakan HANYA JIKA 
    model AI mati, error, atau menghasilkan output yang kosong.
    """
    if not log_data:
        return (f"Halo Bapak/Ibu,\n\n"
                f"Belum ada data pertemuan atau aktivitas belajar yang tercatat untuk ananda {nama_murid} "
                f"pada mata pelajaran {mata_pelajaran} di periode ini. "
                f"Kami akan terus memantau perkembangan ananda ke depannya.")

    # Hitung rata-rata nilai dengan aman
    nilai_list = [l['nilai'] for l in log_data if l.get('nilai') is not None]
    rata_rata = sum(nilai_list) / len(nilai_list) if nilai_list else None
    
    topik_terakhir = log_data[-1].get('topik', 'materi terakhir')
    
    paragraf_1 = (f"Halo Bapak/Ibu,\n\n"
                  f"Berikut adalah ringkasan perkembangan belajar ananda {nama_murid} "
                  f"untuk mata pelajaran {mata_pelajaran}. Selama periode ini, ananda telah berpartisipasi aktif dalam kelas.")
    
    if rata_rata is not None:
        paragraf_1 += f" Rata-rata nilai evaluasi yang diperoleh pada periode ini adalah {rata_rata:.2f}."

    paragraf_2 = (f"Pada pertemuan terakhir, ananda mempelajari materi mengenai '{topik_terakhir}'. "
                  f"Berdasarkan catatan pengajar, secara umum tingkat pemahaman ananda berada pada tahap yang memadai.")
    
    paragraf_3 = "Untuk tahapan belajar selanjutnya, "
    if pso_recommended_route:
        paragraf_3 += f"kami merekomendasikan hal berikut: {pso_recommended_route}."
    else:
        paragraf_3 += "kami akan melanjutkan materi sesuai dengan rencana silabus kelas yang telah ditetapkan."
        
    penutup = "Demikian laporan singkat ini kami sampaikan. Terima kasih atas dukungan Bapak/Ibu dalam proses belajar ananda."

    return f"{paragraf_1}\n\n{paragraf_2}\n\n{paragraf_3}\n\n{penutup}"


# ── Generate Laporan (F003) ───────────────────────────────────────────────────

async def generate_laporan(db: Session, data: LaporanCreate) -> Laporan:
    """
    F003 — Generate laporan perkembangan otomatis via NarrativeEngine.
    Terdapat Fallback Cadangan apabila AI Gagal merespon.
    """
    # 1. Data murid
    murid = db.query(Murid).filter(Murid.id == data.murid_id).first()
    if not murid:
        raise ValueError(f"Murid dengan id {data.murid_id} tidak ditemukan")
 
    # Fallback ke email jika nama murid kosong
    nama_murid = murid.nama or murid.email_address

    # Perbaikan logika pengambilan nama mata pelajaran (Aman dari NoneType)
    nama_mapel = "Umum"
    if data.kelas_id:
        from app.models.models import Kelas
        kelas = db.query(Kelas).filter(Kelas.id == data.kelas_id).first()
        if kelas and kelas.mata_pelajaran_id:
            mp = db.query(MataPelajaran).filter(MataPelajaran.id == kelas.mata_pelajaran_id).first()    
            if mp:
                nama_mapel = mp.nama_mata_pelajaran

    # 2. Log pertemuan dalam periode 
    q = db.query(LogPertemuan).filter(LogPertemuan.murid_id == data.murid_id)
    if data.kelas_id:
        q = q.filter(LogPertemuan.kelas_id == data.kelas_id)
    if data.periode_mulai:
        q = q.filter(LogPertemuan.tanggal >= data.periode_mulai)
    if data.periode_selesai:
        q = q.filter(LogPertemuan.tanggal <= data.periode_selesai)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()
 
    log_data =[
        {
            "tanggal": str(l.tanggal),
            "topik": l.topik,
            "nilai": float(l.nilai) if l.nilai else None,
            "tingkat_pemahaman": l.tingkat_pemahaman,
            "catatan": l.catatan,
        }
        for l in logs
    ]
 
    # 3. Knowledge state 
    ks_rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == data.murid_id).all()
    knowledge_state = {str(ks.topik): float(ks.p_knowledge) for ks in ks_rows}
 
    # 4. Ambil rekomendasi PSO dari RencanaStudi Kelas terbaru
    pso_recommended_route: Optional[str] = None
    if data.kelas_id:
        from app.models.models import RencanaStudi
        rencana = (
            db.query(RencanaStudi)
            .filter(
                RencanaStudi.kelas_id == data.kelas_id,
                # Mengambil rencana global kelas (murid_id is NULL)
                RencanaStudi.murid_id.is_(None) 
            )
            .order_by(RencanaStudi.waktu.desc())
            .first()
        )
        
        if rencana and rencana.daftar_rekomendasi_materi:
            materi = rencana.daftar_rekomendasi_materi
            if isinstance(materi, list) and materi:
                pso_recommended_route = f"Lanjut ke materi (Acuan Kelas): {', '.join(materi[:3])}"
            elif isinstance(materi, str):
                pso_recommended_route = f"(Acuan Kelas) {materi}"
 
    # 5. Generate narasi via AI (Menerapkan Hybrid AI + Rule-Based)
    konten = ""
    is_ai = True
    
    try:
        # Coba generate via AI
        konten = await narrative_engine.generate_report(
            nama_murid=nama_murid,
            mata_pelajaran=nama_mapel,
            log_data=log_data,
            periode_mulai=str(data.periode_mulai) if data.periode_mulai else None,
            periode_selesai=str(data.periode_selesai) if data.periode_selesai else None,
            knowledge_state=knowledge_state,
            pso_recommended_route=pso_recommended_route,
            report_style=getattr(data, "report_style", "Konstruktif dan Memotivasi"),
        )
        
        # Cegah hasil AI yang nge-blank atau cuma membalas "oke"
        if not konten or len(konten.strip()) < 50:
            raise ValueError("Hasil AI terlalu pendek, kosong, atau melantur.")
            
    except Exception as e:
        logger.error(f"Generate laporan AI Gagal ({e}). Sistem beralih ke Rule-Based Fallback Template.")
        # Jalankan fungsi cadangan (Template Python biasa)
        konten = generate_fallback_template(
            nama_murid=nama_murid,
            mata_pelajaran=nama_mapel,
            log_data=log_data,
            pso_recommended_route=pso_recommended_route
        )
        is_ai = False  # Set False agar pengajar tahu ini hasil format default, bukan racikan AI
 
    # 6. Simpan ke PostgreSQL
    laporan = Laporan(
        id=str(uuid.uuid4()),
        murid_id=data.murid_id,
        kelas_id=data.kelas_id,
        konten=konten,
        tipe_laporan=data.tipe_laporan,
        status="draft",
        is_ai_generated=is_ai, # Mengikuti hasil apakah AI berhasil atau gagal
        periode_mulai=data.periode_mulai,
        periode_selesai=data.periode_selesai,
        tanggal=datetime.utcnow(), 
    )
    db.add(laporan)
    db.commit()
    db.refresh(laporan)
    return laporan


# ── Generate PDF ──────────────────────────────────────────────────────────────
 
def generate_pdf(laporan: Laporan) -> str:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_CENTER
 
        pdf_path = os.path.join(settings.UPLOAD_DIR + "pdf/", f"laporan_{laporan.id}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm,   bottomMargin=2*cm)
        styles    = getSampleStyleSheet()
        t_style   = ParagraphStyle("T", parent=styles["Title"],
                                   fontSize=14, alignment=TA_CENTER, spaceAfter=12)
        b_style   = ParagraphStyle("B", parent=styles["Normal"],
                                   fontSize=11, leading=16, spaceAfter=8)
        story =[Paragraph("Laporan Perkembangan Belajar Siswa", t_style), Spacer(1, 0.5*cm)]
        
        # Parsing enter / baris baru agar rapi di PDF
        for para in laporan.konten.split("\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), b_style))
            else:
                story.append(Spacer(1, 0.3*cm))
                
        doc.build(story)
        return pdf_path
        
    except ImportError:
        logger.warning("Package 'reportlab' tidak terinstall. Laporan PDF tidak dibuat.")
        return ""
    except Exception as e:
        logger.error(f"Gagal generate PDF: {e}")
        return ""
 
 
# ── Kirim Email (F006) ────────────────────────────────────────────────────────
 
async def kirim_laporan_email(
    laporan, email_tujuan, nama_murid, catatan=None, pdf_path=None, db=None
):
    try:
        msg = MIMEMultipart()
        msg["From"]    = settings.EMAIL_FROM
        msg["To"]      = email_tujuan
        msg["Subject"] = f"Laporan Perkembangan Belajar – {nama_murid}"
        
        body = (
            f"Yth. Orang Tua/Wali dari {nama_murid},\n\n"
            f"Berikut kami sampaikan laporan perkembangan belajar ananda {nama_murid}.\n\n"
            f"{laporan.konten}\n\n"
        )
        if catatan:
            body += f"Catatan tambahan dari pengajar:\n{catatan}\n\n"
            
        body += "Hormat kami,\nTim Pengajar"
        msg.attach(MIMEText(body, "plain", "utf-8"))
        
        # Pasang PDF sebagai attachment jika ada
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition",
                            f"attachment; filename=Laporan_Perkembangan_{nama_murid.replace(' ','_')}.pdf")
            msg.attach(part)
            
        # Proses pengiriman via SMTP
        await aiosmtplib.send(
            msg, hostname=settings.SMTP_HOST, port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME, password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        
        # Jika berhasil, perbarui status laporan
        if db:
            laporan.status = "terkirim"
            laporan.tanggal_dikirim = datetime.utcnow()
            if pdf_path:
                laporan.pdf_path = pdf_path
            db.commit()
            
        return True
        
    except Exception as e:
        logger.error(f"Gagal kirim email: {e}")
        return False