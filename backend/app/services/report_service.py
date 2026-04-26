"""
report_service.py
Service layer untuk Laporan Perkembangan Siswa.
F003, F005, F006, F007 — buat, edit, kirim, lihat laporan.
Termasuk: generate PDF, kirim email.
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
 
 
# ── Generate Laporan (F003) ───────────────────────────────────────────────────
 
# app/services/report_service.py

# ... (import lainnya tetap)

async def generate_laporan(db: Session, data: LaporanCreate) -> Laporan:
    # 1. Data murid
    murid = db.query(Murid).filter(Murid.id == data.murid_id).first()
    if not murid:
        raise ValueError(f"Murid dengan id {data.murid_id} tidak ditemukan")
 
    # Perbaikan logika pengambilan nama mata pelajaran
    nama_mapel = "Umum"
    if data.kelas_id:
        from app.models.models import Kelas
        kelas = db.query(Kelas).filter(Kelas.id == data.kelas_id).first()
        if kelas and kelas.mata_pelajaran_id:
            mp = db.query(MataPelajaran).filter(MataPelajaran.id == kelas.mata_pelajaran_id).first()    
            if mp:
                nama_mapel = mp.nama_mata_pelajaran

    # 2. Log pertemuan (Query tetap sama)
    q = db.query(LogPertemuan).filter(LogPertemuan.murid_id == data.murid_id)
    if data.kelas_id:
        q = q.filter(LogPertemuan.kelas_id == data.kelas_id)
    # ... (filter periode tetap sama)
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
 
    # 3. Knowledge state (tetap sama)
    ks_rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == data.murid_id).all()
    knowledge_state = {str(ks.topik): float(ks.p_knowledge) for ks in ks_rows}
 
    # 4. Ambil rekomendasi PSO (tetap sama)
    pso_recommended_route = None
    # ... (logika pso tetap sama)
 
    # 5. Generate narasi via AI
    # Jika AI gagal, baris ini akan melempar RuntimeError dan berhenti di sini (tidak commit ke DB)
    konten = await narrative_engine.generate_report(
        nama_murid=str(murid.nama),
        mata_pelajaran=nama_mapel,
        log_data=log_data,
        periode_mulai=str(data.periode_mulai) if data.periode_mulai else None,
        periode_selesai=str(data.periode_selesai) if data.periode_selesai else None,
        knowledge_state=knowledge_state,
        pso_recommended_route=pso_recommended_route,
        report_style=getattr(data, "report_style", "Konstruktif dan Memotivasi"),
    )
 
    # 6. Simpan ke PostgreSQL (Menggunakan datetime.now())
    laporan = Laporan(
        id=str(uuid.uuid4()),
        murid_id=data.murid_id,
        kelas_id=data.kelas_id,
        konten=konten,
        tipe_laporan=data.tipe_laporan,
        status="draft",
        is_ai_generated=True,
        periode_mulai=data.periode_mulai,
        periode_selesai=data.periode_selesai,
        tanggal=datetime.now(), # Konsisten dengan plan_service
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
        for para in laporan.konten.split("\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), b_style))
            else:
                story.append(Spacer(1, 0.3*cm))
        doc.build(story)
        return pdf_path
    except ImportError:
        logger.warning("reportlab tidak terinstall")
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
            f"Berikut kami sampaikan laporan perkembangan belajar {nama_murid}.\n\n"
            f"{laporan.konten}\n\n"
        )
        if catatan:
            body += f"Catatan tambahan:\n{catatan}\n\n"
        body += "Hormat kami,\nTim Pengajar"
        msg.attach(MIMEText(body, "plain", "utf-8"))
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition",
                            f"attachment; filename=laporan_{nama_murid}.pdf")
            msg.attach(part)
        await aiosmtplib.send(
            msg, hostname=settings.SMTP_HOST, port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME, password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
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