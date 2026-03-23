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


class ReportInput(BaseModel):
    student_name: str = Field(..., example="John Mare")
    grade_level: str = Field(..., example="Grade 11 / Advanced Science")
    academic_performance: str = Field(..., example="Grade A+ with good performance")
    behavioral_observations: str = Field(..., example="Very polite and diligence student")
    report_style: str = Field("Constructive", example="Constructive")
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
        f"Academic Progress Report\n"
        f"Student Name: {data.student_name}\n"
        f"Grade Level/Course: {data.grade_level}\n\n"
        f"Academic Performance:\n"
        f"{data.academic_performance.strip()}\n\n"
        f"Behavioral Observations:\n"
        f"{data.behavioral_observations.strip()}\n\n"
        f"Report Style: {data.report_style}\n\n"
        "Summary:\n"
        "This report highlights strengths and a path for continuing progress. "
        "The student is demonstrating positive effort, should maintain consistent focus, "
        "and benefit from targeted development activities."        
    )


def _generate_ai_report(data: ReportInput) -> str:
    try:
        from transformers import pipeline

        gpt2 = pipeline(
            "text-generation",
            model="gpt2",
            tokenizer="gpt2",
            max_new_tokens=240,
            top_p=0.92,
            temperature=0.8,
            repetition_penalty=1.1,
        )

        prompt = (
            f"Generate a polished academic progress report for a student using this data:"
            f" Student Name: {data.student_name}."
            f" Grade Level/Course: {data.grade_level}."
            f" Academic Performance: {data.academic_performance}."
            f" Behavioral Observations: {data.behavioral_observations}."
            f" Report Style: {data.report_style}."
        )

        output = gpt2(prompt, do_sample=True, num_return_sequences=1)
        text = output[0]["generated_text"]

        # Trim prompt echo when possible
        if prompt in text:
            text = text.replace(prompt, "", 1).strip()

        if not text:
            raise ValueError("AI model returned empty report")

        return text
    except Exception as exc:
        # If AI generation fails use template fallback
        return _template_report(data) + "\n\n(Note: AI generation failed, template fallback used.)"


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
