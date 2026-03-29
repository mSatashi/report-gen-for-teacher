# Backend — Sistem Perencanaan Materi Adaptif & Pelaporan Otomatis
**Stack:** Python 3.10 · FastAPI · PostgreSQL · SQLAlchemy · Ollama (AI lokal)

---

## Struktur Folder

```
backend/
├── app/
│   ├── main.py                  ← Entry point FastAPI
│   ├── core/
│   │   ├── config.py            ← Semua konfigurasi dari .env
│   │   ├── database.py          ← Koneksi PostgreSQL
│   │   └── security.py          ← JWT & password hashing
│   ├── models/
│   │   └── models.py            ← SQLAlchemy ORM (semua tabel)
│   ├── schemas/
│   │   └── schemas.py           ← Pydantic request/response
│   ├── routers/
│   │   ├── auth.py              ← POST /auth/register, /auth/login
│   │   ├── dashboard.py         ← GET /dashboard
│   │   ├── kelas.py             ← CRUD kelas & murid
│   │   ├── log.py               ← Daily log (single & bulk)
│   │   ├── laporan.py           ← Generate, edit, kirim laporan
│   │   ├── plan.py              ← Rencana studi adaptif
│   │   └── diagnostic.py        ← Tes diagnostik awal
│   ├── services/
│   │   ├── auth_service.py      ← Logika register/login/JWT
│   │   ├── log_service.py       ← CRUD log + bulk upload CSV/Excel
│   │   ├── report_service.py    ← Generate laporan + PDF + email
│   │   ├── plan_service.py      ← BKT + generate rencana studi
│   │   └── dashboard_service.py ← Data ringkasan dashboard
│   └── ai/
│       ├── ollama_client.py     ← HTTP client ke Ollama
│       └── ai_service.py        ← NarrativeEngine + PlannerEngine
├── alembic/                     ← Database migrations
├── .env.example                 ← Template konfigurasi
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Cara Menjalankan (Development)

### 1. Siapkan environment
```bash
cp .env.example .env
# Edit .env dan isi nilai yang sesuai
```

### 2. Jalankan PostgreSQL + Ollama via Docker
```bash
docker-compose up postgres ollama -d
```

### 3. Pull model Ollama (lakukan sekali)
```bash
# Ganti 'llama3' dengan model yang kamu mau, misal: mistral, gemma2
docker exec adaptive_ollama ollama pull llama3
```

### 4. Install dependencies Python
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### 5. Jalankan backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Buka **http://localhost:8000/docs** untuk melihat dokumentasi API Swagger.

---

## Cara Menjalankan (Docker — semua sekaligus)
```bash
docker-compose up --build
```

---

## Daftar Endpoint Utama

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/v1/auth/register` | Registrasi pengajar/murid |
| POST | `/api/v1/auth/login` | Login, dapat JWT token |
| GET | `/api/v1/dashboard` | Data ringkasan dashboard |
| GET | `/api/v1/kelas` | List kelas pengajar |
| POST | `/api/v1/kelas` | Buat kelas baru |
| GET | `/api/v1/kelas/{id}/murid` | Daftar murid di kelas |
| POST | `/api/v1/logs` | Tambah log pertemuan (form) |
| POST | `/api/v1/logs/bulk/{kelas_id}` | Upload log massal CSV/Excel |
| GET | `/api/v1/logs/kelas/{kelas_id}` | Ambil semua log suatu kelas |
| POST | `/api/v1/laporan/generate` | Generate laporan via AI |
| PUT | `/api/v1/laporan/{id}` | Edit narasi laporan |
| PUT | `/api/v1/laporan/{id}/finalisasi` | Finalisasi laporan |
| POST | `/api/v1/laporan/{id}/kirim` | Kirim laporan via email |
| GET | `/api/v1/laporan/{id}/pdf` | Download laporan PDF |
| POST | `/api/v1/plan/generate/{kelas_id}` | Generate rencana studi adaptif |
| GET | `/api/v1/plan/knowledge-state/{murid_id}` | Lihat status BKT murid |
| POST | `/api/v1/diagnostic` | Simpan hasil tes diagnostik |

---

## Format File Bulk Upload (CSV/Excel)

Kolom yang dikenali (huruf kecil, spasi→underscore):

| Kolom | Wajib | Keterangan |
|-------|-------|------------|
| `tanggal` | ✅ | Format: YYYY-MM-DD |
| `topik` | ✅ | Nama topik yang diajarkan |
| `nilai` | ❌ | Angka 0–100 |
| `murid_id` | ❌ | ID murid jika per-murid |
| `tingkat_pemahaman` | ❌ | sangat_paham/paham/cukup/perlu_review |
| `tingkat_keterlibatan` | ❌ | sangat_aktif/aktif/kurang_fokus |
| `catatan` | ❌ | Catatan bebas pengajar |
| `durasi_menit` | ❌ | Durasi sesi dalam menit |
| `metode_belajar` | ❌ | Nama metode yang dipakai |

---

## Catatan Penting

- **Ollama model** — Pastikan model sudah di-pull sebelum pakai fitur AI. Default: `llama3`. Ganti di `.env` dengan `OLLAMA_MODEL_NAME`.
- **Email** — Isi `SMTP_*` di `.env` untuk fitur kirim laporan. Gunakan App Password jika pakai Gmail.
- **Production** — Ganti `SECRET_KEY` di `.env` dengan string acak panjang (min. 32 karakter).
- **Alembic** (migration production): `alembic upgrade head`
