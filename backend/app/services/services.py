"""
app/services/services.py

Business logic layer — semua operasi database (getter & setter)
dan orchestrasi antar modul.
"""
import io
import json
import logging
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.models import (
    Pengguna, Murid, Pengajar, Kelas, KelasMusrid,
    LogPertemuan, DraftAnalisis, RencanaStudi, Laporan,
    KnowledgeState, DiagnosticResult, StudentEvaluation, LessonPlan
)
from app.schemas.schemas import (
    MuridCreate, PengajarCreate, KelasCreate, KelasUpdate,
    LogPertemuanCreate, LogPertemuanUpdate, LogBatchRow,
    GenerateRencanaRequest, GenerateLaporanRequest, LaporanUpdate
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  AUTH SERVICE
# ═══════════════════════════════════════════════════════════════

class AuthService:

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> dict:
        """Autentikasi pengguna, kembalikan JWT token."""
        result = await db.execute(
            select(Pengguna).where(Pengguna.email_address == email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            raise ValueError("Akun tidak aktif.")

        token_data = {"sub": user.id, "role": user.tipe_pengguna}
        return {
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer",
            "user_id": user.id,
            "tipe_pengguna": user.tipe_pengguna,
        }


# ═══════════════════════════════════════════════════════════════
#  MURID SERVICE
# ═══════════════════════════════════════════════════════════════

class MuridService:

    # ── SETTER ────────────────────────────────────────────────
    @staticmethod
    async def create_murid(db: AsyncSession, data: MuridCreate) -> Murid:
        """Buat akun murid baru beserta entri di tabel pengguna."""
        new_id = str(uuid.uuid4())

        pengguna = Pengguna(
            id=new_id,
            username=data.username,
            email_address=data.email_address,
            hashed_password=hash_password(data.password),
            tipe_pengguna="murid",
        )
        db.add(pengguna)

        murid = Murid(
            id=new_id,
            nama=data.nama,
            tanggal_lahir=data.tanggal_lahir,
            usia=data.usia,
            level=data.level,
            credit_total=data.credit_total or 0,
        )
        db.add(murid)
        await db.flush()
        return murid

    @staticmethod
    async def update_murid(db: AsyncSession, murid_id: str, data: dict) -> Optional[Murid]:
        """Update data murid."""
        result = await db.execute(select(Murid).where(Murid.id == murid_id))
        murid = result.scalar_one_or_none()
        if not murid:
            return None
        for key, val in data.items():
            if val is not None and hasattr(murid, key):
                setattr(murid, key, val)
        await db.flush()
        return murid

    @staticmethod
    async def delete_murid(db: AsyncSession, murid_id: str) -> bool:
        """Soft delete / nonaktifkan akun murid."""
        result = await db.execute(select(Pengguna).where(Pengguna.id == murid_id))
        pengguna = result.scalar_one_or_none()
        if not pengguna:
            return False
        pengguna.is_active = False
        await db.flush()
        return True

    # ── GETTER ────────────────────────────────────────────────
    @staticmethod
    async def get_murid_by_id(db: AsyncSession, murid_id: str) -> Optional[Murid]:
        result = await db.execute(select(Murid).where(Murid.id == murid_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_murid(
        db: AsyncSession,
        kelas_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Murid]:
        """Ambil semua murid, opsional filter per kelas."""
        if kelas_id:
            result = await db.execute(
                select(Murid)
                .join(KelasMusrid, KelasMusrid.murid_id == Murid.id)
                .where(KelasMusrid.kelas_id == kelas_id)
                .offset(skip).limit(limit)
            )
        else:
            result = await db.execute(select(Murid).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_murid_by_pengajar(db: AsyncSession, pengajar_id: str) -> List[Murid]:
        """Ambil semua murid yang berada di kelas milik pengajar tertentu."""
        result = await db.execute(
            select(Murid)
            .join(KelasMusrid, KelasMusrid.murid_id == Murid.id)
            .join(Kelas, Kelas.id == KelasMusrid.kelas_id)
            .where(Kelas.pengajar_id == pengajar_id)
            .distinct()
        )
        return result.scalars().all()


# ═══════════════════════════════════════════════════════════════
#  KELAS SERVICE
# ═══════════════════════════════════════════════════════════════

class KelasService:

    # ── SETTER ────────────────────────────────────────────────
    @staticmethod
    async def create_kelas(db: AsyncSession, data: KelasCreate) -> Kelas:
        kelas = Kelas(
            id=str(uuid.uuid4()),
            nama=data.nama,
            mata_pelajaran=data.mata_pelajaran,
            subject=data.subject,
            meeting_day=data.meeting_day,
            schedule=data.schedule,
            credit=data.credit,
            class_type=data.class_type,
            pengajar_id=data.pengajar_id,
        )
        db.add(kelas)
        await db.flush()
        return kelas

    @staticmethod
    async def update_kelas(db: AsyncSession, kelas_id: str, data: KelasUpdate) -> Optional[Kelas]:
        result = await db.execute(select(Kelas).where(Kelas.id == kelas_id))
        kelas = result.scalar_one_or_none()
        if not kelas:
            return None
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(kelas, key, val)
        await db.flush()
        return kelas

    @staticmethod
    async def tambah_murid_ke_kelas(db: AsyncSession, kelas_id: str, murid_id: str) -> bool:
        existing = await db.execute(
            select(KelasMusrid).where(
                and_(KelasMusrid.kelas_id == kelas_id, KelasMusrid.murid_id == murid_id)
            )
        )
        if existing.scalar_one_or_none():
            return False  # sudah ada
        km = KelasMusrid(kelas_id=kelas_id, murid_id=murid_id)
        db.add(km)
        await db.flush()
        return True

    @staticmethod
    async def hapus_murid_dari_kelas(db: AsyncSession, kelas_id: str, murid_id: str) -> bool:
        result = await db.execute(
            select(KelasMusrid).where(
                and_(KelasMusrid.kelas_id == kelas_id, KelasMusrid.murid_id == murid_id)
            )
        )
        km = result.scalar_one_or_none()
        if not km:
            return False
        await db.delete(km)
        await db.flush()
        return True

    # ── GETTER ────────────────────────────────────────────────
    @staticmethod
    async def get_kelas_by_id(db: AsyncSession, kelas_id: str) -> Optional[Kelas]:
        result = await db.execute(select(Kelas).where(Kelas.id == kelas_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_kelas_by_pengajar(db: AsyncSession, pengajar_id: str) -> List[Kelas]:
        result = await db.execute(
            select(Kelas).where(
                and_(Kelas.pengajar_id == pengajar_id, Kelas.is_active == True)
            ).order_by(Kelas.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_kelas(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Kelas]:
        result = await db.execute(
            select(Kelas).where(Kelas.is_active == True).offset(skip).limit(limit)
        )
        return result.scalars().all()


# ═══════════════════════════════════════════════════════════════
#  LOG PERTEMUAN SERVICE
# ═══════════════════════════════════════════════════════════════

class LogPertemuanService:

    # ── SETTER ────────────────────────────────────────────────
    @staticmethod
    async def create_log(db: AsyncSession, data: LogPertemuanCreate) -> LogPertemuan:
        """Simpan satu log pertemuan (input tunggal via form)."""
        log = LogPertemuan(
            id=str(uuid.uuid4()),
            kelas_id=data.kelas_id,
            murid_id=data.murid_id,
            tanggal=data.tanggal,
            topik=data.topik,
            durasi_menit=data.durasi_menit,
            metode_belajar=data.metode_belajar,
            nilai=data.nilai,
            tingkat_pemahaman=data.tingkat_pemahaman,
            tingkat_keterlibatan=data.tingkat_keterlibatan,
            kompetensi_dicapai=data.kompetensi_dicapai,
            target_materi_berikutnya=data.target_materi_berikutnya,
            kendala=data.kendala,
            catatan=data.catatan,
            rekomendasi_tindak_lanjut=data.rekomendasi_tindak_lanjut,
            is_correct=data.is_correct,
        )
        db.add(log)
        await db.flush()
        return log

    @staticmethod
    async def create_log_batch(
        db: AsyncSession, rows: List[LogBatchRow]
    ) -> Dict[str, Any]:
        """Simpan banyak log sekaligus (dari upload CSV/Excel)."""
        berhasil = 0
        gagal = 0
        error_rows = []

        for i, row in enumerate(rows):
            try:
                log = LogPertemuan(
                    id=str(uuid.uuid4()),
                    kelas_id=row.kelas_id,
                    murid_id=row.murid_id,
                    tanggal=row.tanggal,
                    topik=row.topik,
                    nilai=row.nilai,
                    catatan=row.catatan,
                    tingkat_pemahaman=row.tingkat_pemahaman,
                )
                db.add(log)
                berhasil += 1
            except Exception as e:
                gagal += 1
                error_rows.append({"row": i + 2, "error": str(e)})

        await db.flush()
        return {
            "total_rows": len(rows),
            "berhasil": berhasil,
            "gagal": gagal,
            "error_rows": error_rows,
        }

    @staticmethod
    async def update_log(
        db: AsyncSession, log_id: str, data: LogPertemuanUpdate
    ) -> Optional[LogPertemuan]:
        result = await db.execute(select(LogPertemuan).where(LogPertemuan.id == log_id))
        log = result.scalar_one_or_none()
        if not log:
            return None
        for key, val in data.model_dump(exclude_unset=True).items():
            setattr(log, key, val)
        log.updated_at = datetime.utcnow()
        await db.flush()
        return log

    @staticmethod
    async def delete_log(db: AsyncSession, log_id: str) -> bool:
        result = await db.execute(select(LogPertemuan).where(LogPertemuan.id == log_id))
        log = result.scalar_one_or_none()
        if not log:
            return False
        await db.delete(log)
        await db.flush()
        return True

    # ── GETTER ────────────────────────────────────────────────
    @staticmethod
    async def get_log_by_id(db: AsyncSession, log_id: str) -> Optional[LogPertemuan]:
        result = await db.execute(select(LogPertemuan).where(LogPertemuan.id == log_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_logs_by_kelas(
        db: AsyncSession,
        kelas_id: str,
        murid_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[LogPertemuan]:
        """Ambil log pertemuan dengan berbagai filter."""
        query = select(LogPertemuan).where(LogPertemuan.kelas_id == kelas_id)
        if murid_id:
            query = query.where(LogPertemuan.murid_id == murid_id)
        if from_date:
            query = query.where(LogPertemuan.tanggal >= from_date)
        if to_date:
            query = query.where(LogPertemuan.tanggal <= to_date)
        query = query.order_by(desc(LogPertemuan.tanggal)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_logs_today_count(db: AsyncSession, pengajar_id: str) -> int:
        """Hitung log yang diinput hari ini oleh pengajar tertentu."""
        today = date.today()
        result = await db.execute(
            select(func.count(LogPertemuan.id))
            .join(Kelas, Kelas.id == LogPertemuan.kelas_id)
            .where(
                and_(
                    Kelas.pengajar_id == pengajar_id,
                    LogPertemuan.tanggal == today,
                )
            )
        )
        return result.scalar() or 0


# ═══════════════════════════════════════════════════════════════
#  FILE UPLOAD SERVICE
# ═══════════════════════════════════════════════════════════════

class FileUploadService:
    """
    Proses file CSV / Excel yang diupload oleh pengajar
    untuk input log pertemuan secara massal (F002).
    """

    REQUIRED_COLUMNS = {"kelas_id", "tanggal", "topik"}

    @staticmethod
    def parse_csv(file_bytes: bytes) -> List[Dict]:
        """Parse file CSV menjadi list of dict."""
        df = pd.read_csv(io.BytesIO(file_bytes))
        return FileUploadService._validate_and_clean(df)

    @staticmethod
    def parse_excel(file_bytes: bytes) -> List[Dict]:
        """Parse file Excel (.xlsx / .xls) menjadi list of dict."""
        df = pd.read_excel(io.BytesIO(file_bytes))
        return FileUploadService._validate_and_clean(df)

    @staticmethod
    def _validate_and_clean(df: pd.DataFrame) -> List[Dict]:
        """Validasi kolom wajib dan bersihkan data."""
        # Normalisasi nama kolom (lowercase, trim)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        missing = FileUploadService.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")

        # Hapus baris yang semua kolomnya kosong
        df = df.dropna(how="all")

        # Konversi tanggal
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce").dt.date

        # Hapus baris dengan tanggal atau topik kosong
        df = df.dropna(subset=["tanggal", "topik"])

        return df.to_dict(orient="records")

    @staticmethod
    def rows_to_schema(raw_rows: List[Dict]) -> List[LogBatchRow]:
        """Konversi list dict ke list LogBatchRow (Pydantic)."""
        result = []
        for row in raw_rows:
            try:
                result.append(LogBatchRow(
                    kelas_id=str(row.get("kelas_id", "")),
                    murid_id=str(row.get("murid_id", "")) if row.get("murid_id") else None,
                    tanggal=row["tanggal"],
                    topik=str(row["topik"]),
                    nilai=float(row["nilai"]) if row.get("nilai") not in (None, "") else None,
                    catatan=str(row.get("catatan", "")) or None,
                    tingkat_pemahaman=str(row.get("tingkat_pemahaman", "")) or None,
                ))
            except Exception as e:
                logger.warning("Baris dilewati karena error: %s — %s", row, e)
        return result


# ═══════════════════════════════════════════════════════════════
#  LAPORAN SERVICE
# ═══════════════════════════════════════════════════════════════

class LaporanService:

    # ── SETTER ────────────────────────────────────────────────
    @staticmethod
    async def create_laporan(
        db: AsyncSession,
        murid_id: str,
        pengajar_id: str,
        konten: str,
        report_type: str = "progress",
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
        model_used: Optional[str] = None,
        source: str = "ai",
    ) -> Laporan:
        laporan = Laporan(
            id=str(uuid.uuid4()),
            murid_id=murid_id,
            pengajar_id=pengajar_id,
            konten=konten,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            model_used=model_used,
            source=source,
            generated_at=datetime.utcnow(),
        )
        db.add(laporan)
        await db.flush()
        return laporan

    @staticmethod
    async def update_laporan(
        db: AsyncSession, laporan_id: str, data: LaporanUpdate
    ) -> Optional[Laporan]:
        """Update konten laporan oleh pengajar (F005)."""
        result = await db.execute(select(Laporan).where(Laporan.id == laporan_id))
        laporan = result.scalar_one_or_none()
        if not laporan:
            return None
        if data.konten is not None:
            laporan.konten = data.konten
        if data.is_finalized is not None:
            laporan.is_finalized = data.is_finalized
        laporan.updated_at = datetime.utcnow()
        await db.flush()
        return laporan

    @staticmethod
    async def mark_as_sent(db: AsyncSession, laporan_id: str) -> Optional[Laporan]:
        """Tandai laporan sebagai sudah dikirim."""
        result = await db.execute(select(Laporan).where(Laporan.id == laporan_id))
        laporan = result.scalar_one_or_none()
        if not laporan:
            return None
        laporan.is_sent = True
        laporan.sent_at = datetime.utcnow()
        await db.flush()
        return laporan

    @staticmethod
    async def set_pdf_url(db: AsyncSession, laporan_id: str, pdf_url: str) -> None:
        result = await db.execute(select(Laporan).where(Laporan.id == laporan_id))
        laporan = result.scalar_one_or_none()
        if laporan:
            laporan.pdf_url = pdf_url
            await db.flush()

    # ── GETTER ────────────────────────────────────────────────
    @staticmethod
    async def get_laporan_by_id(db: AsyncSession, laporan_id: str) -> Optional[Laporan]:
        result = await db.execute(select(Laporan).where(Laporan.id == laporan_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_laporan_by_murid(
        db: AsyncSession, murid_id: str, limit: int = 10
    ) -> List[Laporan]:
        result = await db.execute(
            select(Laporan)
            .where(Laporan.murid_id == murid_id)
            .order_by(desc(Laporan.tanggal))
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_laporan_pending(db: AsyncSession, pengajar_id: str) -> List[Laporan]:
        """Laporan yang sudah digenerate tapi belum dikirim."""
        result = await db.execute(
            select(Laporan)
            .join(Murid, Murid.id == Laporan.murid_id)
            .join(KelasMusrid, KelasMusrid.murid_id == Murid.id)
            .join(Kelas, Kelas.id == KelasMusrid.kelas_id)
            .where(
                and_(
                    Kelas.pengajar_id == pengajar_id,
                    Laporan.is_sent == False,
                    Laporan.is_finalized == True,
                )
            )
            .order_by(desc(Laporan.tanggal))
        )
        return result.scalars().all()

    @staticmethod
    async def count_pending_laporan(db: AsyncSession, pengajar_id: str) -> int:
        result = await db.execute(
            select(func.count(Laporan.id))
            .join(Murid, Murid.id == Laporan.murid_id)
            .join(KelasMusrid, KelasMusrid.murid_id == Murid.id)
            .join(Kelas, Kelas.id == KelasMusrid.kelas_id)
            .where(
                and_(
                    Kelas.pengajar_id == pengajar_id,
                    Laporan.is_sent == False,
                )
            )
        )
        return result.scalar() or 0


# ═══════════════════════════════════════════════════════════════
#  RENCANA STUDI SERVICE
# ═══════════════════════════════════════════════════════════════

class RencanaStudiService:

    @staticmethod
    async def create_rencana(
        db: AsyncSession,
        kelas_id: str,
        murid_id: Optional[str],
        rekomendasi_json: str,
        catatan: Optional[str] = None,
        model_used: Optional[str] = None,
    ) -> RencanaStudi:
        rencana = RencanaStudi(
            id=str(uuid.uuid4()),
            kelas_id=kelas_id,
            murid_id=murid_id,
            daftar_rekomendasi_materi=rekomendasi_json,
            catatan_analisa=catatan,
            model_used=model_used,
        )
        db.add(rencana)
        await db.flush()
        return rencana

    @staticmethod
    async def get_rencana_aktif(
        db: AsyncSession, kelas_id: str, murid_id: Optional[str] = None
    ) -> Optional[RencanaStudi]:
        query = select(RencanaStudi).where(
            and_(RencanaStudi.kelas_id == kelas_id, RencanaStudi.is_active == True)
        )
        if murid_id:
            query = query.where(RencanaStudi.murid_id == murid_id)
        query = query.order_by(desc(RencanaStudi.waktu)).limit(1)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def count_rencana_aktif(db: AsyncSession, pengajar_id: str) -> int:
        result = await db.execute(
            select(func.count(RencanaStudi.id))
            .join(Kelas, Kelas.id == RencanaStudi.kelas_id)
            .where(
                and_(
                    Kelas.pengajar_id == pengajar_id,
                    RencanaStudi.is_active == True,
                )
            )
        )
        return result.scalar() or 0


# ═══════════════════════════════════════════════════════════════
#  KNOWLEDGE STATE SERVICE  (BKT)
# ═══════════════════════════════════════════════════════════════

class KnowledgeStateService:

    @staticmethod
    def _update_bkt(
        p_ln: float,
        p_transit: float,
        p_guess: float,
        p_slip: float,
        is_correct: bool,
    ) -> float:
        """
        Hitung update probabilitas penguasaan P(L_n+1) menggunakan Bayesian Knowledge Tracing.

        Formula:
        P(L_n+1 | benar) = P(L_n)(1 - P(S)) / [P(L_n)(1 - P(S)) + (1 - P(L_n)) * P(G)]
        P(L_n+1 | salah) = P(L_n) * P(S) / [P(L_n) * P(S) + (1 - P(L_n)) * (1 - P(G))]
        Kemudian terapkan learning: P(L_n+1) = P(L|obs) + (1 - P(L|obs)) * P(T)
        """
        if is_correct:
            numerator = p_ln * (1 - p_slip)
            denominator = numerator + (1 - p_ln) * p_guess
        else:
            numerator = p_ln * p_slip
            denominator = numerator + (1 - p_ln) * (1 - p_guess)

        p_l_given_obs = numerator / denominator if denominator > 0 else p_ln

        # Terapkan learning transition
        p_l_new = p_l_given_obs + (1 - p_l_given_obs) * p_transit

        # Clamp ke [0, 1]
        return max(0.0, min(1.0, p_l_new))

    @staticmethod
    async def update_from_log(
        db: AsyncSession, log: LogPertemuan
    ) -> Optional[KnowledgeState]:
        """
        Update knowledge state berdasarkan log pertemuan yang baru diinput.
        Dipanggil otomatis setiap kali log baru disimpan.
        """
        if log.murid_id is None or log.is_correct is None:
            return None

        # Cek apakah sudah ada knowledge state untuk topik ini
        result = await db.execute(
            select(KnowledgeState).where(
                and_(
                    KnowledgeState.murid_id == log.murid_id,
                    KnowledgeState.topic == log.topik,
                )
            )
        )
        ks = result.scalar_one_or_none()

        if not ks:
            # Buat baru — P(L0) dari diagnosa_awal murid jika ada
            murid_result = await db.execute(select(Murid).where(Murid.id == log.murid_id))
            murid = murid_result.scalar_one_or_none()
            initial_p = (murid.diagnosa_awal or 50.0) / 100.0 if murid else 0.3

            ks = KnowledgeState(
                id=str(uuid.uuid4()),
                murid_id=log.murid_id,
                topic=log.topik,
                knowledge=initial_p,
            )
            db.add(ks)

        # Hitung nilai baru
        ks.knowledge = KnowledgeStateService._update_bkt(
            p_ln=ks.knowledge,
            p_transit=ks.p_transit,
            p_guess=ks.p_guess,
            p_slip=ks.p_slip,
            is_correct=log.is_correct,
        )
        ks.last_lesson_log_id = log.id
        ks.updated_at = datetime.utcnow()
        await db.flush()
        return ks

    @staticmethod
    async def get_knowledge_states_murid(
        db: AsyncSession, murid_id: str
    ) -> List[KnowledgeState]:
        result = await db.execute(
            select(KnowledgeState)
            .where(KnowledgeState.murid_id == murid_id)
            .order_by(KnowledgeState.knowledge.asc())
        )
        return result.scalars().all()


# ═══════════════════════════════════════════════════════════════
#  DASHBOARD SERVICE
# ═══════════════════════════════════════════════════════════════

class DashboardService:

    @staticmethod
    async def get_summary(db: AsyncSession, pengajar_id: str) -> dict:
        """Ambil semua data yang dibutuhkan halaman dashboard."""
        total_siswa_result = await db.execute(
            select(func.count(Murid.id))
            .join(KelasMusrid, KelasMusrid.murid_id == Murid.id)
            .join(Kelas, Kelas.id == KelasMusrid.kelas_id)
            .where(Kelas.pengajar_id == pengajar_id)
        )
        total_siswa = total_siswa_result.scalar() or 0

        log_hari_ini = await LogPertemuanService.get_logs_today_count(db, pengajar_id)
        plan_aktif = await RencanaStudiService.count_rencana_aktif(db, pengajar_id)
        laporan_pending = await LaporanService.count_pending_laporan(db, pengajar_id)

        # Progress siswa: ambil 5 murid terbaru beserta status
        murid_list = await MuridService.get_murid_by_pengajar(db, pengajar_id)
        progress_siswa = []
        for murid in murid_list[:5]:
            ks_list = await KnowledgeStateService.get_knowledge_states_murid(db, murid.id)
            avg_knowledge = (
                sum(ks.knowledge for ks in ks_list) / len(ks_list) * 100
                if ks_list else 0
            )
            progress_siswa.append({
                "murid_id": murid.id,
                "nama": murid.nama,
                "level": murid.level,
                "avg_penguasaan": round(avg_knowledge, 1),
                "status": "On Track" if avg_knowledge >= 70 else "Perlu Perhatian",
            })

        # Aktivitas terbaru: 5 log pertemuan terakhir
        recent_logs_result = await db.execute(
            select(LogPertemuan)
            .join(Kelas, Kelas.id == LogPertemuan.kelas_id)
            .where(Kelas.pengajar_id == pengajar_id)
            .order_by(desc(LogPertemuan.created_at))
            .limit(5)
        )
        recent_logs = recent_logs_result.scalars().all()
        aktivitas_terbaru = [
            {
                "id": log.id,
                "tanggal": str(log.tanggal),
                "topik": log.topik,
                "nilai": float(log.nilai) if log.nilai else None,
                "tingkat_pemahaman": log.tingkat_pemahaman,
            }
            for log in recent_logs
        ]

        return {
            "total_siswa": total_siswa,
            "log_hari_ini": log_hari_ini,
            "plan_aktif": plan_aktif,
            "laporan_pending": laporan_pending,
            "progress_siswa": progress_siswa,
            "aktivitas_terbaru": aktivitas_terbaru,
        }
