# Teacher Report Generator AI

This is a full-stack web application that uses AI (Large Language Models) to generate personalized student reports. It consists of a React frontend, FastAPI backend, PostgreSQL database, and Ollama for local AI models.

## Features

- **Frontend**: React + Vite web interface for inputting student data and viewing reports
- **Backend**: FastAPI server with AI-powered report generation
- **Database**: PostgreSQL for data storage
- **AI**: Ollama for running local language models
- **Docker**: Containerized deployment with docker-compose

## Project Structure

```
report-gen-for-teacher/
├── backend/          # FastAPI backend
├── src/             # React frontend source
├── public/          # Static assets
├── Dockerfile       # Frontend container
├── docker-compose.yml # Multi-service setup
├── requirements.txt # Python dependencies
└── package.json     # Node dependencies
```

## Setup with Docker (Recommended)

1. **Prerequisites**:
   - Docker and Docker Compose installed
   - At least 8GB RAM for AI models

2. **Clone and navigate to the project**:
   ```bash
   cd report-gen-for-teacher
   ```

3. **Environment Variables**:
   - Copy `.env.example` to `.env` and configure your settings
   - For Hugging Face token (if using external models): `HF_TOKEN=your_token`

4. **Run with Docker Compose**:
   - From project root (`report-gen-for-teacher`):
     ```bash
     docker-compose down
     docker-compose up --build -d
     ```
   - If you only need backend (plus dependencies):
     ```bash
     docker-compose up --build -d postgres ollama backend
     ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Database: localhost:5432

## Manual Setup (Development)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
npm install
npm run dev
```

## Usage

1. Open the frontend at http://localhost:3000
2. Input student information (name, grades, attendance, etc.)
3. Generate AI-powered reports
4. View and download reports

## API Endpoints

### Auth
- `POST /auth/register` : Register user
- `POST /auth/login` : Login and get JWT token

### Kelas & Murid
- `GET /kelas` : List kelas
- `POST /kelas` : Create kelas
- `GET /kelas/{kelas_id}` : Get kelas by ID
- `PUT /kelas/{kelas_id}` : Update kelas
- `DELETE /kelas/{kelas_id}` : Delete kelas
- `GET /kelas/{kelas_id}/murid` : List murid in kelas
- `POST /kelas/{kelas_id}/murid` : Add murid to kelas
- `DELETE /kelas/{kelas_id}/murid/{murid_id}` : Remove murid from kelas
- `POST /kelas/murid/tambah` : Add murid (global)
- `PUT /kelas/murid/{murid_id}` : Update murid

### Daily Log
- `GET /logs/hari-ini` : Get today logs
- `GET /logs/kelas/{kelas_id}` : Get logs by kelas
- `GET /logs/murid/{murid_id}` : Get logs by murid
- `GET /logs/{log_id}` : Get log by ID
- `POST /logs` : Create log pertemuan
- `POST /logs/bulk/{kelas_id}` : Bulk upload logs for kelas
- `PUT /logs/{log_id}` : Update log
- `DELETE /logs/{log_id}` : Delete log

### Rencana Studi
- `POST /rencana-studi/generate` : Generate rencana studi
- `GET /rencana-studi` : List rencana studi

### Laporan
- `POST /laporan/generate` : Generate laporan narasi
- `GET /laporan` : List laporan
- `GET /laporan/{laporan_id}` : Get one laporan by ID
- `PUT /laporan/{laporan_id}` : Update laporan
- `POST /laporan/{laporan_id}/kirim` : Kirim laporan
- `GET /laporan/{laporan_id}/pdf` : Download laporan PDF

### Knowledge State (BKT)
- `GET /knowledge-state/{murid_id}` : Get learning knowledge state for murid

### Dashboard
- `GET /dashboard/{pengajar_id}` : Dashboard summary for pengajar

### AI / LLM
- `GET /ai/health` : AI service health check

### Diagnostic
- `POST /diagnostic` : Create diagnostic entry
- `GET /diagnostic/murid/{murid_id}` : List diagnostics for murid

## Troubleshooting

- **Port conflicts**: Ensure ports 3000, 8000, 5432, 11434 are available
- **Memory issues**: AI models require significant RAM; consider using smaller models
- **Database connection**: Check PostgreSQL credentials in docker-compose.yml

## Requirements

- Docker & Docker Compose
- Node.js 18+ (for manual frontend setup)
- Python 3.10+ (for manual backend setup)
- 8GB+ RAM recommended
