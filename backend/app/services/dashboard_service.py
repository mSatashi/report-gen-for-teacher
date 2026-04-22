"""
dashboard_service.py
Menyediakan data ringkasan untuk halaman Dashboard.
"""
from datetime import date
from sqlalchemy import cast, Float
from sqlalchemy.orm import Session
from app.models.models import Kelas, KelasMurid, LogPertemuan, Laporan, RencanaStudi
from app.schemas.schemas import DashboardSummary

def get_dashboard_data(db: Session, pengajar_id: str) -> DashboardSummary:
    """Ambil semua data ringkasan untuk dashboard pengajar."""
    today = date.today()

    # Kelas-kelas milik pengajar ini
    kelas_list = db.query(Kelas).filter(Kelas.pengajar_id == pengajar_id).all()
    kelas_ids  = [k.id for k in kelas_list]

    # Total siswa (unik)
    total_siswa = (
        db.query(KelasMurid)
        .filter(KelasMurid.kelas_id.in_(kelas_ids))
        .distinct(KelasMurid.murid_id)
        .count()
    )

    # Log hari ini
    log_hari_ini = (
        db.query(LogPertemuan)
        .filter(LogPertemuan.kelas_id.in_(kelas_ids), LogPertemuan.tanggal == today)
        .count()
    )

    # Plan aktif (rencana studi terbaru per kelas)
    plan_aktif = (
        db.query(RencanaStudi)
        .filter(RencanaStudi.kelas_id.in_(kelas_ids))
        .count()
    )

    # Laporan pending (draft / final, belum terkirim)
    report_pending = (
        db.query(Laporan)
        .filter(Laporan.kelas_id.in_(kelas_ids), Laporan.status != "terkirim")
        .count()
    )

    # 10 aktivitas terbaru
    aktivitas = (
        db.query(LogPertemuan)
        .filter(LogPertemuan.kelas_id.in_(kelas_ids))
        .order_by(LogPertemuan.created_at.desc())
        .limit(10)
        .all()
    )
    aktivitas_terbaru = [
        {
            "tanggal": str(a.tanggal),
            "topik":   a.topik,
            "kelas_id": a.kelas_id,
            "murid_id": a.murid_id,
            "nilai":    cast(a.nilai, Float) if a.nilai is not None else None,
            "tingkat_pemahaman": a.tingkat_pemahaman,
        }
        for a in aktivitas
    ]

    # Progress per murid (simplifikasi: avg nilai dari log)
    from sqlalchemy import func
    from app.models.models import Murid
    progress_rows = (
        db.query(
            LogPertemuan.murid_id,
            func.avg(LogPertemuan.nilai).label("avg_nilai"),
            func.count(LogPertemuan.id).label("total_sesi"),
        )
        .filter(LogPertemuan.kelas_id.in_(kelas_ids), LogPertemuan.murid_id.isnot(None))
        .group_by(LogPertemuan.murid_id)
        .limit(10)
        .all()
    )
    progress_siswa = []
    for row in progress_rows:
        murid = db.query(Murid).filter(Murid.id == row.murid_id).first()
        nama  = murid.nama if murid else row.murid_id
        avg   = round(float(row.avg_nilai), 1) if row.avg_nilai else 0
        progress_siswa.append({
            "murid_id":   row.murid_id,
            "nama":       nama,
            "avg_nilai":  avg,
            "total_sesi": row.total_sesi,
            "status":     "On Track" if avg >= 70 else "Perlu Perhatian",
        })

    return DashboardSummary(
        total_siswa=total_siswa,
        log_hari_ini=log_hari_ini,
        plan_aktif=plan_aktif,
        report_pending=report_pending,
        aktivitas_terbaru=aktivitas_terbaru,
        progress_siswa=progress_siswa,
    )
