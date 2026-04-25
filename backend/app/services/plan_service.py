import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
 
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ProcessPoolExecutor

from app.models.models import (
    KnowledgeState, LogPertemuan, RencanaStudi, Kelas, KelasMurid,
    TopikPrasyarat, Topik
)
from app.ai.bkt_engine import bkt_engine, PRIOR_KNOWLEDGE
from app.ai.pso_engine import run_pso_algorithm
 
logger = logging.getLogger(__name__)
 

# ═══════════════════════════════════════════════════════════════════════════════
# 1. KNOWLEDGE STATE — UPDATE & GETTER (TRIGGER OTOMATIS OLEH LOG INPUT)
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
 
    from app.models.models import DiagnosticResult
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
                p_known = max(0.2, p_known)
        result[ks.topik] = p_known
        
    return result


def get_class_knowledge_state(db: Session, kelas_id: str) -> Dict[str, float]:
    """
    Mendapatkan nilai acuan kelas dengan metode "Rata-Rata Kelas".
    """
    murid_di_kelas = db.query(KelasMurid).filter(KelasMurid.kelas_id == kelas_id).all()
    
    if not murid_di_kelas:
        return {}

    total_states = {}
    jumlah_murid = len(murid_di_kelas)
    
    for km in murid_di_kelas:
        ks_individu = get_knowledge_state(db, km.murid_id)
        for topik, prob in ks_individu.items():
            total_states[topik] = total_states.get(topik, 0.0) + prob
            
    rata_rata_kelas = {topik: (total / jumlah_murid) for topik, total in total_states.items()}
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
        raise ValueError("Kelas tidak memiliki murid atau data pemahaman masih kosong.")

    # 2. Hitung Sisa Sesi
    total_log_pertemuan = db.query(LogPertemuan).filter(LogPertemuan.kelas_id == kelas_id).count()
    # (Asumsi: 1 pertemuan = 1 row log. Jika log murid banyak, baiknya hitung tanggal unik/distinct)
    # Untuk amannya kita berikan sisa sesi statis 10 atau dikurangi log unik
    sisa_sesi = max(1, (kelas.kredit or 20) - (total_log_pertemuan // max(1, len(class_knowledge_state))))

    # 3. Bangun Data Graph & Parameter PSO dari Kurikulum
    topik_list = db.query(Topik).filter(Topik.mata_pelajaran_id == kelas.mata_pelajaran_id).order_by(Topik.difficulty_index.asc()).all()
    semua_relasi = db.query(TopikPrasyarat).all()
    
    skill_graph_dict = {}
    skill_params_dict = {}
    heuristic_sequence = []
    
    for t in topik_list:
        skill_graph_dict[t.nama] =[]
        heuristic_sequence.append(t.nama) 
        sp = bkt_engine._get_params(db, t.nama)
        skill_params_dict[t.nama] = sp.learn 
        
    for relasi in semua_relasi:
        topik_anak = db.query(Topik).filter(Topik.id == relasi.topik_id).first()
        topik_syarat = db.query(Topik).filter(Topik.id == relasi.prasyarat_id).first()
        if topik_anak and topik_syarat:
            skill_graph_dict[topik_anak.nama].append(topik_syarat.nama)

    # 4. Eksekusi PSO di Background Process untuk Rata-Rata Kelas
    loop = asyncio.get_running_loop()
    rencana_data = await loop.run_in_executor(
        pso_pool, 
        run_pso_algorithm, 
        f"KELAS-{kelas_id}",      # ID diganti representasi Kelas
        class_knowledge_state,    # Pakai probabilitas rata-rata kelas
        skill_graph_dict,
        skill_params_dict,
        heuristic_sequence,
        sisa_sesi
    )

    # 5. Penentuan Versi (Increment jika Kelas sudah pernah punya rencana)
    rencana_terakhir = db.query(RencanaStudi).filter(
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.murid_id == None # None karena ini rencana global untuk kelas
    ).order_by(RencanaStudi.waktu.desc()).first()

    versi_baru = rencana_terakhir.version + 1 if rencana_terakhir else 1

    # 6. Simpan Hasil murni ke Database (Tanpa LLM)
    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=None, # Murid NULL artinya berlaku untuk seluruh kelas
        daftar_rekomendasi_materi=rencana_data.get("rekomendasi_materi",[]),
        jadwal_mingguan=rencana_data.get("jadwal_mingguan", {}),
        # Menggunakan output catatan asli dari PSO (tanpa dibungkus LLM)
        catatan_analisa=rencana_data.get("catatan_analisa", "Rencana kelas berhasil dibuat berdasarkan rata-rata pemahaman murid."), 
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
    """
    Mengambil daftar rencana studi milik sebuah kelas.
    Difilter khusus untuk rencana global (murid_id == None).
    """
    return db.query(RencanaStudi).filter(
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.murid_id.is_(None) 
    ).order_by(RencanaStudi.waktu.desc()).all()
