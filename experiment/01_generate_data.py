import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# =========================
# CONFIG
# =========================
NUM_STUDENTS = 500
NUM_TEACHERS = 20
START_DATE = datetime(2026, 1, 1)

# =========================
# SKILL GRAPH & DIFFICULTY
# =========================
skill_graph = {
    "bilangan_bulat": ["penjumlahan", "pengurangan"],
    "aljabar_dasar": ["bilangan_bulat", "perkalian"],
    "persamaan_linear_satu_variabel": ["aljabar_dasar"],
    "perbandingan": ["pecahan", "pembagian"],
    "aritmatika_sosial": ["persentase", "aljabar_dasar"],
    "himpunan": [],
    "teorema_pythagoras": ["keliling_luas", "aljabar_dasar"],
    "statistika_dasar": ["pengolahan_data_dasar"],
    "peluang_dasar": ["pecahan"],
    "bangun_ruang": ["keliling_luas"],
    "eksponen_logaritma": ["aljabar_dasar"],
    "fungsi_kuadrat": ["aljabar_dasar", "persamaan_linear_satu_variabel"],
    "sistem_persamaan_linear": ["persamaan_linear_satu_variabel"],
    "matriks": ["sistem_persamaan_linear", "aljabar_dasar"],
    "barisan_deret": ["aljabar_dasar"],
    "trigonometri": ["teorema_pythagoras", "perbandingan"],
    "limit": ["fungsi_kuadrat"],
    "turunan": ["limit"],
    "integral": ["turunan"]
}

skills = list(skill_graph.keys())
difficulty_map = {s: 0.2 + 0.8*(i/len(skills)) for i, s in enumerate(skills)}  # 0.2–1.0

# =========================
# STUDENT PERSONA
# =========================
def generate_persona():
    persona_type = random.choices(
        ["fast", "slow", "inconsistent", "guesser"], weights=[0.3,0.3,0.2,0.2]
    )[0]

    if persona_type == "fast":
        return 0.15, 0.05, 0.10
    elif persona_type == "slow":
        return 0.05, 0.10, 0.20
    elif persona_type == "inconsistent":
        return 0.10, 0.15, 0.25
    else:  
        return 0.08, 0.10, 0.35

students = []
for i in range(1, NUM_STUDENTS+1):
    learn_rate, slip, guess = generate_persona()
    students.append({
        "id": i,
        "teacher_id": random.randint(1, NUM_TEACHERS),
        "baseline": np.clip(np.random.normal(0.6, 0.2), 0.2, 0.95),
        "learn_rate": learn_rate,
        "slip": slip,
        "guess": guess,
        "fatigue": 0.0  
    })

df_students = pd.DataFrame(students)

# =========================
# GENERATE INTERACTIONS
# =========================
lessons, logs, evals, knowledge_states = [], [], [], []
lesson_id, log_id = 1, 1

for _, student in df_students.iterrows():
    current_date = START_DATE
    student_id = student["id"]
    fatigue = 0.0

    for skill in skills:
        prereqs = skill_graph[skill]
        if prereqs and random.random() > 0.7:
            continue  

        knowledge = student["baseline"] * (1 - difficulty_map[skill])
        attempts = random.randint(8, 12)
        
        for t in range(attempts):
            focus = np.clip(np.random.normal(0.7 - fatigue, 0.15), 0.3, 1.0)
            
            delta = student["learn_rate"] * focus * np.random.uniform(0.8, 1.2)
            knowledge = np.clip(knowledge + delta*(1-difficulty_map[skill]), 0, 1)
            
            p_slip = student["slip"] + difficulty_map[skill]*0.1
            p_guess = student["guess"] + (1-difficulty_map[skill])*0.1

            correct = 1 if (knowledge > random.random() and random.random() > p_slip) else 0
            if knowledge < 0.5 and random.random() < p_guess:
                correct = 1

            base_score = 45 + 50 * knowledge * (1 - difficulty_map[skill])
            score = int(np.clip(np.random.normal(base_score, 7), 0, 100))

            lessons.append({"id": lesson_id, "class_id": student["teacher_id"], "topic": skill, "scheduled_date": current_date})
            logs.append({"id": log_id, "lesson_id": lesson_id, "actual_topic": skill, "created_at": current_date})
            evals.append({"lesson_log_id": log_id, "student_id": student_id, "score": score, "understanding": knowledge, "focus": focus})
            knowledge_states.append({"student_id": student_id, "skill": skill, "p_knowledge_true": knowledge, "p_guess": p_guess, "p_slip": p_slip, "lesson_log_id": log_id, "timestamp": current_date})

            lesson_id += 1
            log_id += 1
            fatigue += 0.02  

            if random.random() > 0.6:
                hour_offset = random.choice([1,2,3,4,5,6,7,8])
                current_date += timedelta(hours=hour_offset)
            else:
                current_date += timedelta(hours=random.choice([20,21,22,23]))  
            if current_date.hour > 20:
                current_date = current_date.replace(hour=8) + timedelta(days=1)

# =========================
# SAVE
# =========================
os.makedirs("output", exist_ok=True)
pd.DataFrame(students).to_csv("output/students_mock.csv", index=False)
pd.DataFrame(lessons).to_csv("output/lessons_mock.csv", index=False)
pd.DataFrame(logs).to_csv("output/daily_logs_mock.csv", index=False)
pd.DataFrame(evals).to_csv("output/evaluations_mock.csv", index=False)
pd.DataFrame(knowledge_states).to_csv("output/knowledge_states.csv", index=False)
print("Dataset generated successfully!")