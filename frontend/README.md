# Teacher Report Generator AI

This project uses AI (Large Language Models) to generate personalized student reports based on provided data.

## Features

- Generates detailed teacher reports from student information
- Uses GPT-2 model for text generation
- Supports customizable student data input
- Saves reports to file

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   - Create a `.env` file in the project root with your Hugging Face token:
     ```
     HF_TOKEN=your_hugging_face_token_here
     ```
   - Get a token from [Hugging Face](https://huggingface.co/settings/tokens)

3. **Run the Program**:
   ```bash
   python report_generator.py
   ```

## Usage

Run the backend API server:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000/docs` for interactive Swagger UI.

### Generate a report

POST `http://localhost:8000/api/reports`

JSON body example:

```json
{
  "student_name": "John Mare",
  "grade_level": "Grade 11 / Advanced Science",
  "academic_performance": "Grade A+ with good performance",
  "behavioral_observations": "Very polite and diligent student",
  "report_style": "Constructive",
  "use_ai": false
}
```

### Fetch all reports

GET `http://localhost:8000/api/reports`

### Fetch a report by ID

GET `http://localhost:8000/api/reports/{report_id}`

### Delete a report

DELETE `http://localhost:8000/api/reports/{report_id}`

## Troubleshooting

- **Model download**: First run may take time to download the GPT-2 model.
- **CUDA/GPU issues**: The code automatically falls back to CPU if GPU is unavailable.
- **Token issues**: Ensure your HF_TOKEN is valid for faster downloads.

## Requirements

- Python 3.8+
- Hugging Face account with token
- Internet connection for model download
