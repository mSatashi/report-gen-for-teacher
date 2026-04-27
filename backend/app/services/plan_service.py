import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
 
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ProcessPoolExecutor

from app.models.models import (
    KnowledgeState, LogPertemuan, RencanaStudi, Kelas, KelasMurid,
    TopikPrasyarat, Topik, DiagnosticResult
)
from app.ai.bkt_engine import bkt_engine, PRIOR_KNOWLEDGE
from app.ai.pso_engine import run_pso_algorithm
 
logger = logging.getLogger(__name__)
 

# ═══════════════════════════════════════════════════════════════════════════════
# 1. KNOWLEDGE STATE — UPDATE & GETTER
# ═══════════════════════════════════════════════════════════════════════════════
 
def update_knowledge_states(db: Session, murid_id: str, kelas_id: Optional[str] = None) -> None:
    """
    Dipanggil dari log_service.py setiap kali guru menyimpan Log Pertemuan baru.
    Murni memperbarui tabel knowledge_state berdasarkan hitungan BKT.
    """
    q = db.query(LogPertemuan).filter(
        LogPertemuan.murid_id == murid_id,
        LogPertemuan.nilai.isnot(None),
    )
    if kelas_id:
        q = q.filter(LogPertemuan.kelas_id == kelas_id)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()
 
    topik_scores: Dict[str, List[float]] = {}
    for log in logs:
        topik = log.topik.strip()
        topik_scores.setdefault(topik,[]).append(float(log.nilai))
 
    
    diag_rows = db.query(DiagnosticResult).filter(
        DiagnosticResult.murid_id == murid_id
    ).all()
    diag_map = {d.topik: d.diagnostic_score / 100.0 for d in diag_rows}
 
    for topik, scores in topik_scores.items():
        p0 = diag_map.get(topik, PRIOR_KNOWLEDGE)
        p_final = bkt_engine.batch_update(db, topik, p0, scores) 
 
        ks = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid_id,
            KnowledgeState.topik == topik,
        ).first()
 
        sp = bkt_engine._get_params(db, topik)  
 
        if ks:
            ks.p_knowledge = p_final
            ks.p_learn = sp.learn
            ks.p_guess = sp.guess
            ks.p_slip = sp.slip
            ks.updated_at = datetime.utcnow()
        else:
            ks = KnowledgeState(
                id=str(uuid.uuid4()),
                murid_id=murid_id,
                topik=topik,
                p_knowledge=p_final,
                p_learn=sp.learn,
                p_guess=sp.guess,
                p_slip=sp.slip,
            )
            db.add(ks)
 
    db.commit()
    logger.debug(f"BKT Ter-update untuk murid {murid_id}")


def get_knowledge_state(db: Session, murid_id: str) -> Dict[str, float]:
    """Mengambil pemahaman BKT satu murid dengan mempertimbangkan efek lupa (decay)."""
    rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id == murid_id).all()
    result = {}
    now = datetime.utcnow()
    
    for ks in rows:
        p_known = float(ks.p_knowledge)
        if ks.updated_at:
            days_passed = (now - ks.updated_at).days
            if days_passed >= 30:
                months_passed = days_passed // 30
                p_known = p_known * (0.95 ** months_passed)
                p_known = max(0.2, p_known) # Baseline minimal
        result[ks.topik] = p_known
        
    return result


def get_class_knowledge_state(db: Session, kelas_id: str) -> Dict[str, float]:
    """
    [OPTIMIZED] Mendapatkan nilai acuan kelas dengan metode "Rata-Rata Kelas".
    Menggunakan 1x Query massal agar terhindar dari N+1 Timeout Issue.
    """
    # 1. Ambil list ID murid
    murid_ids_query = db.query(KelasMurid.murid_id).filter(KelasMurid.kelas_id == kelas_id).all()
    murid_ids =[row.murid_id for row in murid_ids_query]
    
    if not murid_ids:
        return {}

    total_murid = len(murid_ids)
    
    # 2. Ambil semua KS sekaligus
    ks_rows = db.query(KnowledgeState).filter(KnowledgeState.murid_id.in_(murid_ids)).all()
    
    # 3. Proses di memori (Sangat Cepat)
    topic_sums = {}
    topic_counts = {}
    now = datetime.utcnow()
    
    for ks in ks_rows:
        p_known = float(ks.p_knowledge)
        # Kalkulasi decay (lupa)
        if ks.updated_at:
            days_passed = (now - ks.updated_at).days
            if days_passed >= 30:
                months_passed = days_passed // 30
                p_known = max(0.2, p_known * (0.95 ** months_passed))
                
        topic_sums[ks.topik] = topic_sums.get(ks.topik, 0.0) + p_known
        topic_counts[ks.topik] = topic_counts.get(ks.topik, 0) + 1
        
    # 4. Hitung rata-rata murni
    rata_rata_kelas = {}
    for topik in topic_sums:
        # Jika ada murid yang belum punya log di topik ini, anggap nilainya baseline (0.2)
        missing_students = total_murid - topic_counts[topik]
        total_value = topic_sums[topik] + (missing_students * 0.2)
        rata_rata_kelas[topik] = total_value / total_murid
        
    return rata_rata_kelas


# ═══════════════════════════════════════════════════════════════════════════════
# 2. GENERATE RENCANA STUDI KELAS (MANUAL TRIGGER OLEH GURU)
# ═══════════════════════════════════════════════════════════════════════════════
pso_pool = ProcessPoolExecutor(max_workers=4)

async def generate_rencana_studi_kelas(
    db: Session,
    kelas_id: str
) -> RencanaStudi:
    """
    Hanya dijalankan saat Guru menekan tombol "Generate Rencana Kelas".
    Tidak ada LLM yang dilibatkan. Murni perhitungan matematika (PSO).
    """
    kelas = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not kelas:
        raise ValueError(f"Kelas {kelas_id} tidak ditemukan")

    # 1. Ambil Pemahaman Kelas (Rata-rata)
    class_knowledge_state = get_class_knowledge_state(db, kelas_id)
    if not class_knowledge_state:
        raise ValueError("Gagal membuat rencana: Kelas belum memiliki murid atau log BKT.")

    # 2. Hitung Sisa Sesi Berdasarkan KREDIT di tabel KELAS
    murid_ids =[row.murid_id for row in db.query(KelasMurid.murid_id).filter(KelasMurid.kelas_id == kelas_id).all()]
    jumlah_murid_di_kelas = len(murid_ids)
    
    kredit_kelas = kelas.kredit if kelas.kredit else 20
    total_log_keseluruhan = db.query(LogPertemuan).filter(LogPertemuan.kelas_id == kelas_id).count()
    sesi_telah_berjalan = total_log_keseluruhan // max(1, jumlah_murid_di_kelas)
    sisa_sesi = max(1, kredit_kelas - sesi_telah_berjalan)

    # 3. Bangun Data Graph (Dioptimasi di memori untuk cegah N+1 Database Call)
    topik_list = db.query(Topik).filter(Topik.mata_pelajaran_id == kelas.mata_pelajaran_id).order_by(Topik.difficulty_index.asc()).all()
    
    # Bikin kamus untuk pemetaan cepat id -> nama
    topik_dict = {t.id: t.nama for t in topik_list}
    
    skill_graph_dict = {t.nama: [] for t in topik_list}
    heuristic_sequence =[t.nama for t in topik_list]
    skill_params_dict = {t.nama: bkt_engine._get_params(db, str(t.nama)).learn for t in topik_list}
    
    # Ambil semua relasi tanpa loop N+1
    semua_relasi = db.query(TopikPrasyarat).all()
    for relasi in semua_relasi:
        anak_nama = topik_dict.get(relasi.topik_id)
        syarat_nama = topik_dict.get(relasi.prasyarat_id)
        # Jika keduanya ada di mapel ini, hubungkan
        if anak_nama and syarat_nama:
            skill_graph_dict[anak_nama].append(syarat_nama)

    # 4. Eksekusi PSO di Background Process
    loop = asyncio.get_running_loop()
    rencana_data = await loop.run_in_executor(
        pso_pool, 
        run_pso_algorithm, 
        f"KELAS-{kelas_id}",      
        class_knowledge_state,    
        skill_graph_dict,
        skill_params_dict,
        heuristic_sequence,
        int(sisa_sesi)
    )

    # 5. Penentuan Versi 
    rencana_terakhir = db.query(RencanaStudi).filter(
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.murid_id.is_(None) 
    ).order_by(RencanaStudi.waktu.desc()).first()

    versi_baru = rencana_terakhir.version + 1 if rencana_terakhir else 1

    # 6. Simpan Hasil
    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        daftar_rekomendasi_materi=rencana_data.get("rekomendasi_materi",[]),
        jadwal_mingguan=rencana_data.get("jadwal_mingguan",[]), 
        catatan_analisa=rencana_data.get("catatan_analisa", "Rencana kelas berhasil dibuat."), 
        estimasi_waktu_selesai=datetime.utcnow() + timedelta(weeks=rencana_data.get("estimasi_selesai_minggu", 4)),
        version=versi_baru,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PLAN CRUD
# ═══════════════════════════════════════════════════════════════════════════════
 
def get_rencana_by_id(db: Session, plan_id: str) -> Optional[RencanaStudi]:
    return db.query(RencanaStudi).filter(RencanaStudi.id == plan_id).first()
 
 
def get_rencana_by_kelas(db: Session, kelas_id: str) -> List[RencanaStudi]:
    return db.query(RencanaStudi).filter(
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.murid_id.is_(None) 
    ).order_by(RencanaStudi.waktu.desc()).all()