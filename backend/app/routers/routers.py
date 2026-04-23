"""
app/routers/routers.py
Semua endpoint FastAPI — diorganisir per fitur.
"""
import io
import json
import logging
from datetime import date
from typing import List, Optional

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException,
    Query, UploadFile, status
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.schemas.schemas import (
    LoginRequest, TokenResponse,
    MuridCreate, MuridResponse, MuridUpdate,
    PengajarCreate, PengajarResponse,
    KelasCreate, KelasUpdate, KelasResponse, TambahMuridKeKelas,
    LogPertemuanCreate, LogPertemuanUpdate, LogPertemuanResponse, LogBatchResponse,
    GenerateRencanaRequest, RencanaStudiResponse,
    GenerateLaporanRequest, LaporanResponse, LaporanUpdate, SendLaporanRequest,
    KnowledgeStateResponse, DashboardSummaryResponse,
)
from app.services.services import (
    AuthService, MuridService, KelasService,
    LogPertemuanService, FileUploadService,
    LaporanService, RencanaStudiService,
    KnowledgeStateService, DashboardService,
)
from app.ai.llm_service import NarrativeEngine, PlannerEngine, get_llm_client

logger = logging.getLogger(__name__)


# ─── Helper: validasi ekstensi file upload ────────────────────
def _validate_upload(file: UploadFile, allowed: list = None):
    allowed = allowed or settings.ALLOWED_UPLOAD_EXTENSIONS
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Tipe file tidak didukung: {ext}. Gunakan: {', '.join(allowed)}"
        )
    return ext


# ═══════════════════════════════════════════════════════════════
#  AUTH ROUTER
# ═══════════════════════════════════════════════════════════════
auth_router = APIRouter(prefix="/auth", tags=["Autentikasi"])


@auth_router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login pengguna — kembalikan JWT access + refresh token."""
    result = await AuthService.login(db, payload.email_address, payload.password)
    if not result:
        raise HTTPException(status_code=401, detail="Email atau password salah")
    return result


# ═══════════════════════════════════════════════════════════════
#  MURID ROUTER
# ═══════════════════════════════════════════════════════════════
murid_router = APIRouter(prefix="/murid", tags=["Murid"])


@murid_router.post("/", response_model=MuridResponse, status_code=201)
async def create_murid(payload: MuridCreate, db: AsyncSession = Depends(get_db)):
    """Daftarkan murid baru."""
    murid = await MuridService.create_murid(db, payload)
    return murid


@murid_router.get("/", response_model=List[MuridResponse])
async def get_all_murid(
    kelas_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Ambil semua murid, opsional filter per kelas."""
    return await MuridService.get_all_murid(db, kelas_id=kelas_id, skip=skip, limit=limit)


@murid_router.get("/{murid_id}", response_model=MuridResponse)
async def get_murid(murid_id: str, db: AsyncSession = Depends(get_db)):
    """Ambil detail satu murid."""
    murid = await MuridService.get_murid_by_id(db, murid_id)
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
    return murid


@murid_router.put("/{murid_id}", response_model=MuridResponse)
async def update_murid(
    murid_id: str,
    payload: MuridUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update data murid."""
    murid = await MuridService.update_murid(db, murid_id, payload.model_dump(exclude_unset=True))
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
    return murid


@murid_router.delete("/{murid_id}", status_code=204)
async def delete_murid(murid_id: str, db: AsyncSession = Depends(get_db)):
    """Nonaktifkan akun murid."""
    ok = await MuridService.delete_murid(db, murid_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")


# ═══════════════════════════════════════════════════════════════
#  KELAS ROUTER
# ═══════════════════════════════════════════════════════════════
kelas_router = APIRouter(prefix="/kelas", tags=["Kelas"])


@kelas_router.post("/", response_model=KelasResponse, status_code=201)
async def create_kelas(payload: KelasCreate, db: AsyncSession = Depends(get_db)):
    return await KelasService.create_kelas(db, payload)


@kelas_router.get("/", response_model=List[KelasResponse])
async def get_all_kelas(
    pengajar_id: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    if pengajar_id:
        return await KelasService.get_kelas_by_pengajar(db, pengajar_id)
    return await KelasService.get_all_kelas(db, skip=skip, limit=limit)


@kelas_router.get("/{kelas_id}", response_model=KelasResponse)
async def get_kelas(kelas_id: str, db: AsyncSession = Depends(get_db)):
    kelas = await KelasService.get_kelas_by_id(db, kelas_id)
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    return kelas


@kelas_router.put("/{kelas_id}", response_model=KelasResponse)
async def update_kelas(
    kelas_id: str,
    payload: KelasUpdate,
    db: AsyncSession = Depends(get_db),
):
    kelas = await KelasService.update_kelas(db, kelas_id, payload)
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")
    return kelas


@kelas_router.post("/{kelas_id}/murid", status_code=201)
async def tambah_murid_ke_kelas(
    kelas_id: str,
    payload: TambahMuridKeKelas,
    db: AsyncSession = Depends(get_db),
):
    """Tambahkan murid ke dalam kelas."""
    ok = await KelasService.tambah_murid_ke_kelas(db, kelas_id, payload.murid_id)
    if not ok:
        raise HTTPException(status_code=409, detail="Murid sudah ada di kelas ini")
    return {"message": "Murid berhasil ditambahkan ke kelas"}


@kelas_router.delete("/{kelas_id}/murid/{murid_id}", status_code=204)
async def hapus_murid_dari_kelas(
    kelas_id: str,
    murid_id: str,
    db: AsyncSession = Depends(get_db),
):
    ok = await KelasService.hapus_murid_dari_kelas(db, kelas_id, murid_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Murid tidak ada di kelas ini")


# ═══════════════════════════════════════════════════════════════
#  LOG PERTEMUAN ROUTER
# ═══════════════════════════════════════════════════════════════
log_router = APIRouter(prefix="/log-pertemuan", tags=["Log Pertemuan"])


@log_router.post("/", response_model=LogPertemuanResponse, status_code=201)
async def create_log_single(
    payload: LogPertemuanCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Input log pertemuan tunggal via form (F001).
    Otomatis update knowledge state BKT setelah simpan.
    """
    log = await LogPertemuanService.create_log(db, payload)

    # Update BKT jika ada data is_correct
    if log.is_correct is not None:
        await KnowledgeStateService.update_from_log(db, log)

    return log


@log_router.post("/batch-upload", response_model=LogBatchResponse, status_code=201)
async def upload_log_batch(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload log pertemuan massal via file CSV atau Excel (F002).
    
    Format kolom yang dibutuhkan di file:
    - kelas_id (wajib)
    - tanggal   (wajib, format: YYYY-MM-DD)
    - topik     (wajib)
    - murid_id  (opsional)
    - nilai     (opsional, 0-100)
    - catatan   (opsional)
    - tingkat_pemahaman (opsional)
    """
    ext = _validate_upload(file, [".csv", ".xlsx", ".xls"])
    file_bytes = await file.read()

    try:
        if ext == ".csv":
            raw_rows = FileUploadService.parse_csv(file_bytes)
        else:
            raw_rows = FileUploadService.parse_excel(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    schema_rows = FileUploadService.rows_to_schema(raw_rows)
    result = await LogPertemuanService.create_log_batch(db, schema_rows)
    return result


@log_router.get("/", response_model=List[LogPertemuanResponse])
async def get_logs(
    kelas_id: str = Query(...),
    murid_id: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Ambil log pertemuan dengan filter."""
    return await LogPertemuanService.get_logs_by_kelas(
        db, kelas_id, murid_id=murid_id,
        from_date=from_date, to_date=to_date,
        skip=skip, limit=limit,
    )


@log_router.get("/{log_id}", response_model=LogPertemuanResponse)
async def get_log_by_id(log_id: str, db: AsyncSession = Depends(get_db)):
    log = await LogPertemuanService.get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
    return log


@log_router.put("/{log_id}", response_model=LogPertemuanResponse)
async def update_log(
    log_id: str,
    payload: LogPertemuanUpdate,
    db: AsyncSession = Depends(get_db),
):
    log = await LogPertemuanService.update_log(db, log_id, payload)
    if not log:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
    return log


@log_router.delete("/{log_id}", status_code=204)
async def delete_log(log_id: str, db: AsyncSession = Depends(get_db)):
    ok = await LogPertemuanService.delete_log(db, log_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")


# ═══════════════════════════════════════════════════════════════
#  RENCANA STUDI ROUTER  (Plan Viewer)
# ═══════════════════════════════════════════════════════════════
plan_router = APIRouter(prefix="/rencana-studi", tags=["Rencana Studi"])


@plan_router.post("/generate", response_model=RencanaStudiResponse, status_code=201)
async def generate_rencana_studi(
    payload: GenerateRencanaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate rencana studi adaptif baru menggunakan PlannerEngine + LLM (F004).
    Menggunakan data knowledge state (BKT) siswa dan sisa kredit kelas.
    """
    # Ambil data yang dibutuhkan
    kelas = await KelasService.get_kelas_by_id(db, payload.kelas_id)
    if not kelas:
        raise HTTPException(status_code=404, detail="Kelas tidak ditemukan")

    logs = await LogPertemuanService.get_logs_by_kelas(
        db, payload.kelas_id, murid_id=payload.murid_id
    )
    log_dicts = [
        {"topik": l.topik, "nilai": float(l.nilai) if l.nilai else None, "catatan": l.catatan}
        for l in logs
    ]

    ks_list = []
    if payload.murid_id:
        ks_objs = await KnowledgeStateService.get_knowledge_states_murid(db, payload.murid_id)
        ks_list = [{"topic": ks.topic, "knowledge": ks.knowledge} for ks in ks_objs]

    # Hitung sisa kredit
    sisa_kredit = max(0, kelas.credit - len(logs))

    # Jalankan NarrativeEngine untuk buat draft analisis
    narrative = NarrativeEngine()
    draft_konten = await narrative.analisa_data_pertemuan(payload.kelas_id, log_dicts)

    # Jalankan PlannerEngine untuk buat rencana
    planner = PlannerEngine()
    rencana_dict = await planner.generate_rencana_studi(
        draft_analisis=draft_konten,
        knowledge_states=ks_list,
        sisa_kredit=sisa_kredit,
    )

    # Simpan ke database
    rencana = await RencanaStudiService.create_rencana(
        db=db,
        kelas_id=payload.kelas_id,
        murid_id=payload.murid_id,
        rekomendasi_json=json.dumps(rencana_dict, ensure_ascii=False),
        catatan=rencana_dict.get("catatan_planner"),
        model_used=settings.LLM_PROVIDER,
    )
    return rencana


@plan_router.get("/", response_model=List[RencanaStudiResponse])
async def get_rencana(
    kelas_id: str = Query(...),
    murid_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    rencana = await RencanaStudiService.get_rencana_aktif(db, kelas_id, murid_id)
    return [rencana] if rencana else []


# ═══════════════════════════════════════════════════════════════
#  LAPORAN ROUTER  (Report Editor)
# ═══════════════════════════════════════════════════════════════
laporan_router = APIRouter(prefix="/laporan", tags=["Laporan"])


@laporan_router.post("/generate", response_model=LaporanResponse, status_code=201)
async def generate_laporan(
    payload: GenerateLaporanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate laporan perkembangan otomatis menggunakan NarrativeEngine + LLM (F003).
    """
    murid = await MuridService.get_murid_by_id(db, payload.murid_id)
    if not murid:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")

    # Ambil semua log dalam periode
    logs = await LogPertemuanService.get_logs_by_kelas(
        db,
        kelas_id="",   # ambil semua kelas murid ini
        murid_id=payload.murid_id,
        from_date=payload.period_start,
        to_date=payload.period_end,
        limit=200,
    )

    if not logs:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada log pertemuan dalam periode ini untuk murid tersebut."
        )

    log_dicts = [
        {
            "topik": l.topik,
            "nilai": float(l.nilai) if l.nilai else None,
            "catatan": l.catatan or "",
            "tanggal": str(l.tanggal),
        }
        for l in logs
    ]

    ks_objs = await KnowledgeStateService.get_knowledge_states_murid(db, payload.murid_id)
    ks_dicts = [{"topic": ks.topic, "knowledge": ks.knowledge} for ks in ks_objs]

    # Generate narasi via LLM
    engine = NarrativeEngine()
    konten = await engine.generate_laporan(
        data_siswa={"nama": murid.nama, "education_level": murid.education_level or ""},
        log_pertemuan=log_dicts,
        knowledge_states=ks_dicts,
        period_start=str(payload.period_start) if payload.period_start else None,
        period_end=str(payload.period_end) if payload.period_end else None,
    )

    laporan = await LaporanService.create_laporan(
        db=db,
        murid_id=payload.murid_id,
        pengajar_id=None,
        konten=konten,
        report_type=payload.report_type,
        period_start=payload.period_start,
        period_end=payload.period_end,
        model_used=settings.LLM_PROVIDER,
        source="ai",
    )
    return laporan


@laporan_router.get("/", response_model=List[LaporanResponse])
async def get_laporan_list(
    murid_id: Optional[str] = Query(None),
    pengajar_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Ambil daftar laporan."""
    if murid_id:
        return await LaporanService.get_laporan_by_murid(db, murid_id)
    if pengajar_id:
        return await LaporanService.get_laporan_pending(db, pengajar_id)
    return []


@laporan_router.get("/{laporan_id}", response_model=LaporanResponse)
async def get_laporan_by_id(laporan_id: str, db: AsyncSession = Depends(get_db)):
    laporan = await LaporanService.get_laporan_by_id(db, laporan_id)
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return laporan


@laporan_router.put("/{laporan_id}", response_model=LaporanResponse)
async def update_laporan(
    laporan_id: str,
    payload: LaporanUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Edit laporan oleh pengajar sebelum finalisasi (F005)."""
    laporan = await LaporanService.update_laporan(db, laporan_id, payload)
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    return laporan


@laporan_router.post("/{laporan_id}/kirim")
async def kirim_laporan(
    laporan_id: str,
    payload: SendLaporanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Kirim laporan ke orang tua via email (F006).
    [PLACEHOLDER: Implementasi SMTP / email service]
    """
    laporan = await LaporanService.get_laporan_by_id(db, laporan_id)
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")

    if not laporan.is_finalized:
        raise HTTPException(
            status_code=400,
            detail="Laporan belum difinalisasi. Finalisasi dulu sebelum kirim."
        )

    # [PLACEHOLDER: implementasi pengiriman email]
    # from app.services.email_service import send_laporan_email
    # await send_laporan_email(
    #     to=payload.email_penerima,
    #     laporan=laporan,
    #     pdf_url=laporan.pdf_url,
    # )

    laporan = await LaporanService.mark_as_sent(db, laporan_id)
    return {"message": "Laporan berhasil dikirim", "laporan_id": laporan_id}


@laporan_router.get("/{laporan_id}/pdf")
async def download_laporan_pdf(laporan_id: str, db: AsyncSession = Depends(get_db)):
    """
    Download laporan sebagai file PDF.
    [PLACEHOLDER: Implementasi PDF renderer menggunakan ReportLab / WeasyPrint]
    """
    laporan = await LaporanService.get_laporan_by_id(db, laporan_id)
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")

    # [PLACEHOLDER: generate PDF dari laporan.konten]
    # pdf_bytes = await generate_pdf(laporan.konten)
    # return StreamingResponse(
    #     io.BytesIO(pdf_bytes),
    #     media_type="application/pdf",
    #     headers={"Content-Disposition": f"attachment; filename=laporan_{laporan_id}.pdf"}
    # )

    return {"message": "[PLACEHOLDER] PDF generation belum diimplementasi", "laporan_id": laporan_id}


# ═══════════════════════════════════════════════════════════════
#  KNOWLEDGE STATE ROUTER
# ═══════════════════════════════════════════════════════════════
ks_router = APIRouter(prefix="/knowledge-state", tags=["Knowledge State (BKT)"])


@ks_router.get("/{murid_id}", response_model=List[KnowledgeStateResponse])
async def get_knowledge_states(murid_id: str, db: AsyncSession = Depends(get_db)):
    """Ambil probabilitas penguasaan per topik untuk satu murid."""
    return await KnowledgeStateService.get_knowledge_states_murid(db, murid_id)


# ═══════════════════════════════════════════════════════════════
#  DASHBOARD ROUTER
# ═══════════════════════════════════════════════════════════════
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/{pengajar_id}", response_model=DashboardSummaryResponse)
async def get_dashboard(pengajar_id: str, db: AsyncSession = Depends(get_db)):
    """Ambil data ringkasan untuk halaman dashboard pengajar."""
    return await DashboardService.get_summary(db, pengajar_id)


# ═══════════════════════════════════════════════════════════════
#  AI / LLM ROUTER  (Health check & utils)
# ═══════════════════════════════════════════════════════════════
ai_router = APIRouter(prefix="/ai", tags=["AI / LLM"])


@ai_router.get("/health")
async def llm_health_check():
    """Cek status koneksi ke model LLM yang aktif."""
    provider = settings.LLM_PROVIDER
    if provider == "ollama":
        from app.ai.llm_service import OllamaClient
        client = OllamaClient()
        is_up = await client.health_check()
        models = await client.list_models() if is_up else []
        return {
            "provider": "ollama",
            "status": "up" if is_up else "down",
            "base_url": settings.OLLAMA_BASE_URL,
            "active_model": settings.OLLAMA_MODEL,
            "available_models": models,
        }
    return {
        "provider": provider,
        "status": "unknown",
        "note": "Health check hanya tersedia untuk Ollama lokal.",
    }
