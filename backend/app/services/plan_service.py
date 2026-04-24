import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
 
import numpy as np
from sqlalchemy.orm import Session
import asyncio
from concurrent.futures import ProcessPoolExecutor

from app.models.models import (
    DraftAnalisis, KnowledgeState, LogPertemuan,
    RencanaStudi, Kelas, Murid, TopikPrasyarat, Topik
)
from app.ai.ai_service import narrative_engine, planner_engine
# [INTEGRASI] Pakai BKTEngine dengan parameter per-skill (dari bkt_engine.py)
from app.ai.bkt_engine import bkt_engine, PRIOR_KNOWLEDGE, CORRECT_THRESHOLD
from app.ai.pso_engine import run_pso_algorithm
 
logger = logging.getLogger(__name__)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# KNOWLEDGE STATE — Query & Update dari PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════
 
def update_knowledge_states(
    db: Session,
    murid_id: str,
    kelas_id: Optional[str] = None,
) -> None:
    """
    Hitung ulang knowledge_state untuk satu murid berdasarkan LogPertemuan di DB.
 
    [INTEGRASI] Menggunakan bkt_engine.batch_update() (per-skill params)
    yang logika Bayes-nya identik dengan update_bkt() di 02_bkt_tuning.py.
 
    Dipanggil setiap kali log baru ditambahkan (dari routers/log.py).
    Data disimpan ke tabel knowledge_state di PostgreSQL.
    """
    # 1. Ambil semua log dengan nilai (dari PostgreSQL, bukan CSV)
    q = db.query(LogPertemuan).filter(
        LogPertemuan.murid_id == murid_id,
        LogPertemuan.nilai.isnot(None),
    )
    if kelas_id:
        q = q.filter(LogPertemuan.kelas_id == kelas_id)
    logs = q.order_by(LogPertemuan.tanggal.asc()).all()
 
    # 2. Kelompokkan skor per topik (urutan kronologis penting untuk BKT)
    topik_scores: Dict[str, List[float]] = {}
    for log in logs:
        topik = log.topik.strip()
        topik_scores.setdefault(topik, []).append(float(log.nilai))
 
    # 3. Ambil P(L0) dari diagnostic_result jika ada
    from app.models.models import DiagnosticResult
    diag_rows = db.query(DiagnosticResult).filter(
        DiagnosticResult.murid_id == murid_id
    ).all()
    diag_map = {d.topik: d.diagnostic_score / 100.0 for d in diag_rows}
 
    # 4. Update per topik menggunakan BKTEngine
    for topik, scores in topik_scores.items():
        p0      = diag_map.get(topik, PRIOR_KNOWLEDGE)   # P(L0) dari diagnostik atau 0.2
        p_final = bkt_engine.batch_update(db, topik, p0, scores) 
 
        # Upsert ke tabel knowledge_state (PostgreSQL)
        ks = db.query(KnowledgeState).filter(
            KnowledgeState.murid_id == murid_id,
            KnowledgeState.topik    == topik,
        ).first()
 
        sp = bkt_engine._get_params(db, topik)  
 
        if ks:
            ks.p_knowledge = p_final
            ks.p_learn     = sp.learn
            ks.p_guess     = sp.guess
            ks.p_slip      = sp.slip
            ks.updated_at  = datetime.utcnow()
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
    
    state_terbaru = get_knowledge_state(db, murid_id)
    cek_rencana_kadaluarsa(db, murid_id, kelas_id, state_terbaru)
    logger.debug(f"Knowledge state diperbarui untuk murid {murid_id}: {len(topik_scores)} topik")

def cek_rencana_kadaluarsa(db: Session, murid_id: str, kelas_id: str, knowledge_state: dict):
    """
    Mengecek apakah rencana studi sudah tidak relevan (outdated).

    Rencana dianggap kadaluarsa jika:
    - Ada materi dalam rencana yang sudah dikuasai (≥ 0.85)
    """

    # Ambil rencana terbaru yang masih aktif
    rencana = db.query(RencanaStudi).filter(
        RencanaStudi.murid_id == murid_id,
        RencanaStudi.kelas_id == kelas_id,
        RencanaStudi.is_outdated == False
    ).order_by(RencanaStudi.waktu.desc()).first()

    # Jika tidak ada rencana atau kosong → tidak perlu dicek
    if not rencana or not rencana.daftar_rekomendasi_materi:
        return

    # Cek apakah ada topik yang sudah dikuasai
    for topik in rencana.daftar_rekomendasi_materi:
        if knowledge_state.get(topik, 0.0) >= 0.85:
            # Tandai rencana sebagai usang
            rencana.is_outdated = True
            rencana.catatan_analisa += (
                "\n\n[SISTEM] Rencana usang. "
                "Siswa berkembang lebih cepat dari prediksi."
            )
            db.commit()
            break
 
 
def get_knowledge_state(db: Session, murid_id: str) -> Dict[str, float]:
    """
    Mengambil knowledge state (tingkat penguasaan) seorang murid dari database,
    dengan mempertimbangkan efek pelupaan (forgetting/decay) seiring waktu.

    Parameter:
    - db: Session database
    - murid_id: ID murid

    Return:
    - Dictionary {topik: probabilitas_penguasaan}

    Mekanisme:
    1. Ambil nilai probabilitas penguasaan (p_knowledge) dari database
    2. Jika ada timestamp terakhir update:
       - Hitung selisih hari dari sekarang
       - Jika ≥ 30 hari → terapkan decay bulanan
    3. Gunakan exponential decay:
       p = p * (0.95 ^ jumlah_bulan)
    4. Batasi nilai minimum di 0.2 (baseline pengetahuan awal)

    Tujuan:
    - Mensimulasikan efek lupa (mirip forgetting curve)
    - Menjaga sistem tetap realistis terhadap waktu
    """

    rows = db.query(KnowledgeState)\
             .filter(KnowledgeState.murid_id == murid_id)\
             .all()

    result = {}
    now = datetime.utcnow()
    
    for ks in rows:
        # Nilai awal penguasaan
        p_known = float(ks.p_knowledge)
        
        # Terapkan decay jika ada timestamp
        if ks.updated_at:
            days_passed = (now - ks.updated_at).days

            if days_passed >= 30:
                # Hitung jumlah bulan (dibulatkan ke bawah)
                months_passed = days_passed // 30

                # Exponential decay (5% penurunan per bulan)
                p_known = p_known * (0.95 ** months_passed)

                # Batas minimum (tidak boleh terlalu rendah)
                p_known = max(0.2, p_known)
        
        # Simpan hasil akhir
        result[ks.topik] = p_known
        
    return result
 

 
# ═══════════════════════════════════════════════════════════════════════════════
# PLAN CRUD
# ═══════════════════════════════════════════════════════════════════════════════
 
def get_rencana_by_id(db: Session, plan_id: str) -> Optional[RencanaStudi]:
    return db.query(RencanaStudi).filter(RencanaStudi.id == plan_id).first()
 
 
def get_rencana_by_kelas(
    db: Session,
    kelas_id: str,
    murid_id: Optional[str] = None,
) -> List[RencanaStudi]:
    q = db.query(RencanaStudi).filter(RencanaStudi.kelas_id == kelas_id)
    if murid_id:
        q = q.filter(RencanaStudi.murid_id == murid_id)
    return q.order_by(RencanaStudi.waktu.desc()).all()
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE RENCANA STUDI (F004)
# ═══════════════════════════════════════════════════════════════════════════════
pso_pool = ProcessPoolExecutor(max_workers=4)

async def generate_rencana_studi(
    db: Session,
    kelas_id: str,
    murid_id: str, # [REVISI] Hapus Optional, wajibkan murid_id sejak awal
) -> RencanaStudi:
    """
    F004 — Generate rencana studi adaptif menggunakan optimasi matematis PSO murni.
    """
    # [REVISI] Pindahkan validasi ke paling atas untuk menghemat resource
    if not murid_id:
        raise ValueError("Pembuatan rencana studi adaptif (PSO) membutuhkan spesifik murid_id.")

    # 1. Validasi kelas
    kelas = db.query(Kelas).filter(Kelas.id == kelas_id).first()
    if not kelas:
        raise ValueError(f"Kelas {kelas_id} tidak ditemukan")
 
    # 2. Ambil log pertemuan dari PostgreSQL
    logs = db.query(LogPertemuan).filter(
        LogPertemuan.kelas_id == kelas_id,
        LogPertemuan.murid_id == murid_id
    ).order_by(LogPertemuan.tanggal.asc()).all()
 
    log_data = [
        {
            "tanggal": str(l.tanggal),
            "topik":   l.topik,
            "nilai":   float(l.nilai) if l.nilai else None,
            "catatan": l.catatan,
        }
        for l in logs
    ]
 
    # 3. Analisis log → draft_analisis via LLM (Hanya menganalisis log masa lalu)
    # [REVISI] Perbaikan nama agar sesuai dengan murid tunggal
    murid = db.query(Murid).filter(Murid.id == murid_id).first()
    nama_murid = murid.nama if murid else "Siswa"
    
    draft_text = await narrative_engine.analyze_class_data(
        nama_kelas=f"Kelas {kelas.nama} - {nama_murid}",
        log_data=log_data,
    )
    draft = DraftAnalisis(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        konten=draft_text,
    )
    db.add(draft)
    db.flush()
 
    # 4. Update dan Ambil knowledge_state via BKTEngine
    update_knowledge_states(db, murid_id, kelas_id)
    knowledge_state = get_knowledge_state(db, murid_id) # Cukup panggil satu kali di sini
 
    # 5. Hitung sisa sesi
    sisa_sesi = max(1, (kelas.kredit or 20) - len(logs))
 
    # 6. Bangun Data untuk PSO (Murni Dictionary & List, Bebas Sesi DB)
    topik_list = db.query(Topik).filter(Topik.mata_pelajaran_id == kelas.mata_pelajaran_id).order_by(Topik.difficulty_index.asc()).all()
    semua_relasi = db.query(TopikPrasyarat).all()
    
    skill_graph_dict = {}
    skill_params_dict = {}
    heuristic_sequence = [] # Untuk inisialisasi Partikel ke-0
    
    for t in topik_list:
        skill_graph_dict[t.nama] = []
        heuristic_sequence.append(t.nama) # Sudah terurut dari termudah
        sp = bkt_engine._get_params(db, t.nama)
        skill_params_dict[t.nama] = sp.learn # Ambil learn_rate saja
        
    for relasi in semua_relasi:
        topik_anak = db.query(Topik).filter(Topik.id == relasi.topik_id).first()
        topik_syarat = db.query(Topik).filter(Topik.id == relasi.prasyarat_id).first()
        if topik_anak and topik_syarat:
            skill_graph_dict[topik_anak.nama].append(topik_syarat.nama)

    # 7. Eksekusi PSO di Background Process
    loop = asyncio.get_running_loop()
    rencana_data = await loop.run_in_executor(
        pso_pool, 
        run_pso_algorithm, 
        murid_id, 
        knowledge_state, 
        skill_graph_dict,
        skill_params_dict,
        heuristic_sequence,
        sisa_sesi
    )

    # [BARU] Minta LLM memberikan narasi humanis berdasarkan rute PSO
    catatan_humanis = await planner_engine.narrate_pso_plan(
        nama_murid=nama_murid,
        rencana_pso=rencana_data,
        draft_analisis=draft_text # Diambil dari DraftAnalisis yang dibuat sebelumnya
    )

    # 8. Simpan RencanaStudi ke PostgreSQL
    rencana = RencanaStudi(
        id=str(uuid.uuid4()),
        kelas_id=kelas_id,
        murid_id=murid_id,
        draft_analisis_id=draft.id,
        daftar_rekomendasi_materi=rencana_data.get("rekomendasi_materi", []),
        jadwal_mingguan=rencana_data.get("jadwal_mingguan", {}),
        # Gunakan catatan_humanis hasil LLM, bukan catatan teknis dari PSO
        catatan_analisa=catatan_humanis, 
        estimasi_waktu_selesai=datetime.utcnow() + timedelta(weeks=rencana_data.get("estimasi_selesai_minggu", 4)),
        version=versi,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana

