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
# SKILL GRAPH (lebih panjang)
# =========================

skill_graph = {
    "penjumlahan": [],
    "pengurangan": [],
    "perkalian": ["penjumlahan"],
    "pembagian": ["perkalian"],
    "pecahan": ["pembagian"],
    "desimal": ["pecahan"],
    "aljabar": ["pecahan"],
    "persamaan_linear": ["aljabar"],
    "fungsi": ["persamaan_linear"],
    "limit": ["fungsi"],
    "turunan": ["limit"],
    "integral": ["turunan"],
}

skills = list(skill_graph.keys())

difficulty_map = {s: i/len(skills) for i, s in enumerate(skills)}

# =========================
# STUDENT PERSONA
# =========================

def generate_persona():
    persona_type = random.choice(["fast", "slow", "inconsistent", "guesser"])

    if persona_type == "fast":
        return 0.15, 0.05, 0.1
    elif persona_type == "slow":
        return 0.05, 0.1, 0.2
    elif persona_type == "inconsistent":
        return 0.1, 0.15, 0.25
    else:  # guesser
        return 0.08, 0.1, 0.35

# =========================
# GENERATE STUDENTS
# =========================

students = []
for i in range(1, NUM_STUDENTS + 1):
    learn_rate, slip, guess = generate_persona()

    students.append({
        "id": i,
        "teacher_id": random.randint(1, NUM_TEACHERS),
        "baseline": np.clip(np.random.normal(0.6, 0.2), 0.2, 0.95),
        "learn_rate": learn_rate,
        "slip": slip,
        "guess": guess,
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

    for skill in skills:

        # enforce dependency
        prereqs = skill_graph[skill]
        if prereqs:
            if random.random() > 0.7:
                continue

        P_L = max(0.05, student["baseline"] - difficulty_map[skill])
        knowledge = 1 if random.random() < P_L else 0

        attempts = random.randint(5, 9)

        for t in range(attempts):

            # dynamic behavior
            focus = np.clip(np.random.normal(0.7, 0.2), 0.2, 1.0)
            learn_rate = student["learn_rate"] * focus

            # learning
            if knowledge == 0 and random.random() < learn_rate:
                knowledge = 1

            # forgetting
            if knowledge == 1 and random.random() < 0.05:
                knowledge = 0

            # observation
            if knowledge == 1:
                correct = 1 if random.random() > student["slip"] else 0
            else:
                correct = 1 if random.random() < student["guess"] else 0

            # score
            base = 80 if correct else 50
            score = int(np.clip(np.random.normal(base, 10), 0, 100))

            # save lesson
            lessons.append({
                "id": lesson_id,
                "class_id": student["teacher_id"],
                "topic": skill,
                "scheduled_date": current_date
            })

            logs.append({
                "id": log_id,
                "lesson_id": lesson_id,
                "actual_topic": skill,
                "created_at": current_date
            })

            evals.append({
                "lesson_log_id": log_id,
                "student_id": student_id,
                "score": score,
                "understanding": score / 100,
                "focus": focus
            })

            knowledge_states.append({
                "student_id": student_id,
                "skill": skill,
                "p_knowledge_true": knowledge,
                "p_guess": student["guess"],
                "p_slip": student["slip"],
                "lesson_log_id": log_id,
                "timestamp": current_date
            })

            lesson_id += 1
            log_id += 1
            current_date += timedelta(days=random.randint(1, 3))

# =========================
# SAVE
# =========================

pd.DataFrame(students).to_csv("output/students_mock.csv", index=False)
pd.DataFrame(lessons).to_csv("output/lessons_mock.csv", index=False)
pd.DataFrame(logs).to_csv("output/daily_logs_mock.csv", index=False)
pd.DataFrame(evals).to_csv("output/evaluations_mock.csv", index=False)
pd.DataFrame(knowledge_states).to_csv("output/knowledge_states.csv", index=False)

print("Dataset generated successfully!")