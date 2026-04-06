import json
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

DATA_FILE = Path("reports.json")
if not DATA_FILE.exists():
    DATA_FILE.write_text("{}", encoding="utf-8")

app = FastAPI(
    title="Teacher Report Generator API",
    description="Backend API for generating student academic progress reports",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# [BARU] Menambahkan field untuk BKT dan PSO
class ReportInput(BaseModel):
    student_name: str = Field(..., example="Alea")
    grade_level: str = Field(..., example="Kelas 6 / Ilmu Pengetahuan Alam")
    academic_performance: str = Field(..., example="Nilai rata-rata 85, sangat baik di teori.")
    behavioral_observations: str = Field(..., example="Sangat aktif bertanya, namun kurang teliti saat ujian.")
    bkt_understanding_level: str = Field("Probabilitas pemahaman 0.85 (Tinggi)", example="Probabilitas pemahaman 0.85")
    pso_recommended_route: str = Field("Lanjut ke materi Ekosistem Darat", example="Lanjut ke materi Ekosistem Darat")
    report_style: str = Field("Konstruktif dan Memotivasi", example="Konstruktif")
    use_ai: bool = Field(False, example=False, description="Whether to produce report text with ML model.")
    attachments: Optional[List[str]] = Field(None, example=["student_project.pdf"])

class ReportOutput(BaseModel):
    id: str
    student_name: str
    grade_level: str
    report_style: str
    generated_text: str
    use_ai: bool
    attachments: Optional[List[str]]

def _load_reports() -> Dict[str, dict]:
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8") or "{}")
    except Exception:
        return {}

def _save_reports(reports: Dict[str, dict]) -> None:
    DATA_FILE.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")

def _template_report(data: ReportInput) -> str:
    return (
        f"Laporan Perkembangan Akademik\n"
        f"Nama Siswa: {data.student_name}\n"
        f"Kelas/Mata Pelajaran: {data.grade_level}\n\n"
        f"Performa Akademik:\n{data.academic_performance.strip()}\n\n"
        f"Observasi Sikap:\n{data.behavioral_observations.strip()}\n\n"
        f"Status Pemahaman (BKT): {data.bkt_understanding_level}\n"
        f"Rencana Belajar Berikutnya (PSO): {data.pso_recommended_route}\n\n"
        "Ringkasan: Siswa menunjukkan perkembangan positif. Fokus selanjutnya adalah pada rekomendasi materi di atas."        
    )

def _generate_ai_report(data: ReportInput) -> str:
    try:
        from transformers import pipeline
        from transformers import GenerationConfig

        # [DIUBAH] Menggunakan model <8B yang optimal untuk instruksi (7B parameter)
        model_name = "Qwen/Qwen2.5-3B-Instruct"

        # [DIUBAH] Konfigurasi tuning ditambahkan temperature, top_p, dan do_sample
        generation_config = GenerationConfig(
            model=model_name,
            max_new_tokens=1024,
            temperature=0.6,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True,
            tie_word_embeddings=False,
        )

        qwen = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=model_name,
            device_map="auto" # Membantu membagi beban memori
        )

        # [DIUBAH] Prompt terstruktur menggunakan Few-Shot dan memuat data BKT/PSO
        prompt = (
            f"Tuliskan laporan perkembangan siswa dalam Bahasa Indonesia yang formal, empatik, dan mudah dipahami oleh orang tua.\n\n"
            f"Contoh Format:\n"
            f"Ananda telah mengikuti kelas dengan sangat baik. Secara akademik, penguasaan materinya memuaskan. "
            f"Berdasarkan analisis sistem kami, tingkat pemahaman ananda sudah matang. Oleh karena itu, untuk pertemuan berikutnya, "
            f"rencana pembelajaran akan difokuskan pada pengayaan materi lanjutan. Terus pertahankan semangat belajarnya!\n\n"
            f"Data Siswa Saat Ini:\n"
            f"- Nama: {data.student_name}\n"
            f"- Mata Pelajaran: {data.grade_level}\n"
            f"- Performa Akademik: {data.academic_performance}\n"
            f"- Observasi Sikap: {data.behavioral_observations}\n"
            f"- Tingkat Pemahaman (BKT): {data.bkt_understanding_level}\n"
            f"- Rekomendasi Rute Belajar (PSO): {data.pso_recommended_route}\n\n"
            f"Buat laporan untuk data siswa di atas berdasarkan contoh format:"
        )

        output = qwen(
            prompt,
            generation_config=generation_config,
        )
        text = output[0]["generated_text"]

        if prompt in text:
            text = text.replace(prompt, "", 1).strip()

        if not text:
            raise ValueError("AI model returned empty report")

        return text
    except Exception as exc:
        print(f"Error AI: {exc}")
        return _template_report(data) + "\n\n(Catatan: Generasi AI gagal, menggunakan draf template.)"



@app.post("/api/reports", response_model=ReportOutput)
def create_report(payload: ReportInput):
    if not payload.student_name.strip():
        raise HTTPException(status_code=400, detail="student_name is required")

    report_id = str(uuid4())
    generated = _generate_ai_report(payload) if payload.use_ai else _template_report(payload)

    reports = _load_reports()
    reports[report_id] = {
        "id": report_id,
        "student_name": payload.student_name,
        "grade_level": payload.grade_level,
        "report_style": payload.report_style,
        "generated_text": generated,
        "use_ai": payload.use_ai,
        "attachments": payload.attachments or [],
    }
    _save_reports(reports)

    return reports[report_id]


@app.get("/api/reports", response_model=List[ReportOutput])
def list_reports():
    reports = _load_reports()
    return list(reports.values())


@app.get("/api/reports/{report_id}", response_model=ReportOutput)
def get_report(report_id: str):
    reports = _load_reports()
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")
    return reports[report_id]


@app.delete("/api/reports/{report_id}")
def delete_report(report_id: str):
    reports = _load_reports()
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="Report not found")
    deleted = reports.pop(report_id)
    _save_reports(reports)
    return {"deleted": report_id, "student_name": deleted.get("student_name")}


@app.get("/")
def root():
    return {"message": "Teacher Report Generator Backend is running", "endpoints": ["/api/reports"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
