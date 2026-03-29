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
   ```bash
   docker-compose up --build
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

- `POST /api/reports`: Generate a student report
- `GET /api/reports`: List saved reports
- `GET /api/reports/{report_id}`: Fetch a report by ID
- `DELETE /api/reports/{report_id}`: Delete a report

## Troubleshooting

- **Port conflicts**: Ensure ports 3000, 8000, 5432, 11434 are available
- **Memory issues**: AI models require significant RAM; consider using smaller models
- **Database connection**: Check PostgreSQL credentials in docker-compose.yml

## Requirements

- Docker & Docker Compose
- Node.js 18+ (for manual frontend setup)
- Python 3.10+ (for manual backend setup)
- 8GB+ RAM recommended
