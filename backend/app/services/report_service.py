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
from app.models.models import Laporan, Murid, LogPertemuan, KnowledgeState
from app.schemas.schemas import LaporanCreate, LaporanUpdate
from app.ai.ai_service import narrative_engine

logger = logging.getLogger(__name__)

os.makedirs(settings.UPLOAD_DIR + "pdf/", exist_ok=True)


# ── CRUD Laporan ─────────────────────────────────────────────────────────────

def get_laporan_by_id(db: Session, laporan_id: str) -> Optional[Laporan]:
    return db.query(Laporan).filter(Laporan.id == laporan_id).first()


def get_laporan_by_murid(
    db: Session,
    murid_id: str,
    skip: int = 0,
    limit: int = 50,
) -> List[Laporan]:
    return (
        db.query(Laporan)
        .filter(Laporan.murid_id == murid_id)
        .order_by(Laporan.tanggal.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_laporan_pending(db: Session, pengajar_id: str) -> List[Laporan]:
    """Ambil laporan berstatus 'draft' atau 'final' yang belum dikirim."""
    from app.models.models import Kelas
    kelas_ids = [k.id for k in db.query(Kelas).filter(Kelas.pengajar_id == pengajar_id).all()]
    return (
        db.query(Laporan)
        .filter(Laporan.kelas_id.in_(kelas_ids), Laporan.status != "terkirim")
        .all()
    )


def update_laporan(db: Session, laporan_id: str, data: LaporanUpdate) -> Optional[Laporan]:
    """F005 — Edit/override laporan yang sudah di-generate."""
    lap = get_laporan_by_id(db, laporan_id)
    if not lap:
        return None
    for field, val in data.model_dump(exclude_none=True).items():
        setattr(lap, field, val)
    db.commit()
    db.refresh(lap)
    return lap


def finalize_laporan(db: Session, laporan_id: str) -> Optional[Laporan]:
    """Set status laporan menjadi 'final'."""
    return update_laporan(db, laporan_id, LaporanUpdate(status="final"))


# ── Generate Laporan (AI) ─────────────────────────────────────────────────────

async def generate_laporan(
    db: Session,
    data: LaporanCreate,
) -> Laporan:
    """
    F003 — Generate laporan perkembangan otomatis via NarrativeEngine.
    Alur:
    1. Ambil data murid & log pertemuan dari DB
    2. Ambil knowledge state (BKT)
    3. Kirim ke NarrativeEngine untuk generate narasi
    4. Simpan hasilnya ke tabel laporan
    """
    # 1. Data murid
    murid = db.query(Murid).filter(Murid.id == data.murid_id).first()
    if not murid:
        raise ValueError(f"Murid dengan id {data.murid_id} tidak ditemukan")

    murid_pengguna = murid.pengguna
    nama_murid     = murid.nama or murid_pengguna.username

    # 2. Data kelas & mata pelajaran
    mata_pelajaran = "Umum"
    if data.kelas_id:
        from app.models.models import Kelas
        kelas = db.query(Kelas).filter(Kelas.id == data.kelas_id).first()
        if kelas:
            mata_pelajaran = kelas.mata_pelajaran or kelas.nama

    # 3. Ambil log pertemuan pada periode
    q = db.query(LogPertemuan).filter(LogPertemuan.murid_id == data.murid_id)
    if data.kelas_id:
        q = q.filter(LogPertemuan.kelas_id == data.kelas_id)
    if data.periode_mulai:
        q = q.filter(LogPertemuan.tanggal >= data.periode_mulai)
    if data.periode_selesai:
        q = q.filter(LogPertemuan.tanggal <= data.periode_selesai)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()

    log_data = [
        {
            "tanggal":              str(l.tanggal),
            "topik":                l.topik,
            "nilai":                float(l.nilai) if l.nilai else None,
            "tingkat_pemahaman":    l.tingkat_pemahaman,
            "tingkat_keterlibatan": l.tingkat_keterlibatan,
            "catatan":              l.catatan,
            "kompetensi_dicapai":   l.kompetensi_dicapai,
        }
        for l in logs
    ]

    # 4. Knowledge state dari BKT
    ks_rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == data.murid_id).all()
    knowledge_state = {ks.topik: float(ks.p_knowledge) for ks in ks_rows}

    # 5. Generate narasi via LLM
    konten = await narrative_engine.generate_report(
        nama_murid=nama_murid,
        mata_pelajaran=mata_pelajaran,
        log_data=log_data,
        periode_mulai=str(data.periode_mulai) if data.periode_mulai else None,
        periode_selesai=str(data.periode_selesai) if data.periode_selesai else None,
        knowledge_state=knowledge_state,
    )

    # 6. Simpan ke DB
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
        tanggal=datetime.utcnow(),
    )
    db.add(laporan)
    db.commit()
    db.refresh(laporan)
    return laporan


# ── Generate PDF ──────────────────────────────────────────────────────────────

def generate_pdf(laporan: Laporan) -> str:
    """
    Konversi konten laporan ke file PDF.
    Mengembalikan path file PDF yang disimpan.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.enums import TA_LEFT, TA_CENTER

        pdf_dir  = settings.UPLOAD_DIR + "pdf/"
        pdf_path = os.path.join(pdf_dir, f"laporan_{laporan.id}.pdf")

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm,   bottomMargin=2*cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            fontSize=14, alignment=TA_CENTER, spaceAfter=12
        )
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=11, leading=16, spaceAfter=8
        )

        story = []
        story.append(Paragraph("Laporan Perkembangan Belajar Siswa", title_style))
        story.append(Spacer(1, 0.5*cm))

        for paragraph in laporan.konten.split("\n"):
            if paragraph.strip():
                story.append(Paragraph(paragraph.strip(), body_style))
            else:
                story.append(Spacer(1, 0.3*cm))

        doc.build(story)
        return pdf_path

    except ImportError:
        logger.warning("reportlab tidak terinstall, PDF tidak dapat dibuat")
        return ""
    except Exception as e:
        logger.error(f"Gagal generate PDF: {e}")
        return ""


# ── Kirim Email ───────────────────────────────────────────────────────────────

async def kirim_laporan_email(
    laporan: Laporan,
    email_tujuan: str,
    nama_murid: str,
    catatan: Optional[str] = None,
    pdf_path: Optional[str] = None,
    db: Optional[Session] = None,
) -> bool:
    """
    F006 — Kirim laporan via email ke orang tua.
    Melampirkan PDF jika tersedia.
    """
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
            body += f"Catatan tambahan dari pengajar:\n{catatan}\n\n"
        body += "Hormat kami,\nTim Pengajar"

        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Lampirkan PDF jika ada
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename=laporan_{nama_murid}.pdf",
            )
            msg.attach(part)

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )

        # Update status laporan di DB
        if db:
            laporan.status          = "terkirim"
            laporan.tanggal_dikirim = datetime.utcnow()
            if pdf_path:
                laporan.pdf_path = pdf_path
            db.commit()

        logger.info(f"Laporan {laporan.id} berhasil dikirim ke {email_tujuan}")
        return True

    except Exception as e:
        logger.error(f"Gagal kirim email laporan {laporan.id}: {e}")
        return False
