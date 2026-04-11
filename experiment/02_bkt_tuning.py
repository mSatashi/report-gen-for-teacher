import os
import pandas as pd
import numpy as np

# =========================
# KONFIGURASI
# =========================
LOGS_PATH = "output/daily_logs_mock.csv"
EVALS_PATH = "output/evaluations_mock.csv"

# Output files (semua di folder 'models')
OUTPUT_KNOWLEDGE_HISTORY = "models/knowledge_state_history.csv"
OUTPUT_EVAL = "models/bkt_manual_evaluation.csv"
OUTPUT_GLOBAL_PARAMS = "models/bkt_global_params.csv"            # Untuk aturan main PSO
OUTPUT_STUDENT_MASTERY = "models/current_student_mastery.csv"    # Untuk start point PSO / Murid kembali belajar

CORRECT_THRESHOLD = 70
DEFAULT_LEARN = 0.15
DEFAULT_SLIP = 0.05
DEFAULT_GUESS = 0.1

# =========================
# BACA DATA
# =========================
if not os.path.exists(LOGS_PATH) or not os.path.exists(EVALS_PATH):
    raise FileNotFoundError("Dataset tidak lengkap. Jalankan 01_dataset_gen.py terlebih dahulu.")

df_logs = pd.read_csv(LOGS_PATH)
df_evals = pd.read_csv(EVALS_PATH)

df = pd.merge(df_evals, df_logs, left_on="lesson_log_id", right_on="id")
df["correct"] = (df["score"] >= CORRECT_THRESHOLD).astype(int)
df_bkt = df[["student_id", "actual_topic", "correct", "lesson_log_id"]].copy()

# Sort by time/order is CRITICAL for Knowledge Tracing
df_bkt = df_bkt.sort_values(['student_id', 'actual_topic', 'lesson_log_id'])
df_bkt.rename(columns={"student_id":"user_id","actual_topic":"skill_name"}, inplace=True)

# =========================
# INISIALISASI PARAMETER & KNOWLEDGE
# =========================
skills = df_bkt["skill_name"].unique()
params = {skill: {"learn": DEFAULT_LEARN, "slip": DEFAULT_SLIP, "guess": DEFAULT_GUESS} for skill in skills}
knowledge_state = {}  # key=(user_id, skill_name), value=p_known
history = []

# =========================
# FUNGSI UPDATE BKT
# =========================
def update_bkt(user, skill, correct):
    key = (user, skill)
    p_known = knowledge_state.get(key, 0.2)  # Prior baseline jika murid belum pernah belajar

    learn = params[skill]["learn"]
    slip = params[skill]["slip"]
    guess = params[skill]["guess"]

    # Teorema Bayes
    if correct == 1:
        p_known_post = (p_known * (1 - slip)) / ((p_known * (1 - slip)) + ((1 - p_known) * guess))
    else:
        p_known_post = (p_known * slip) / ((p_known * slip) + ((1 - p_known) * (1 - guess)))

    p_known_new = p_known_post + (1 - p_known_post) * learn
    p_known_new = np.clip(p_known_new, 0, 1)
    knowledge_state[key] = p_known_new

    p_correct_pred = p_known_new * (1 - slip) + (1 - p_known_new) * guess
    pred_correct = 1 if np.random.rand() < p_correct_pred else 0

    return p_known_new, pred_correct

# =========================
# UPDATE KNOWLEDGE PER ATTEMPT
# =========================
for idx, row in df_bkt.iterrows():
    user = row["user_id"]
    skill = row["skill_name"]
    correct = row["correct"]

    p_known_new, pred_correct = update_bkt(user, skill, correct)

    history.append({
        "user_id": user,
        "skill_name": skill,
        "correct": correct,
        "p_knowledge": p_known_new,
        "pred_correct": pred_correct
    })

df_history = pd.DataFrame(history)

# =========================
# PASTIKAN FOLDER MODELS ADA
# =========================
os.makedirs("models", exist_ok=True)

# =========================
# SIMPAN DATA UNTUK ALGORITMA PSO
# =========================
# 1. Simpan History (Log tracking)
df_history.to_csv(OUTPUT_KNOWLEDGE_HISTORY, index=False)

# 2. Simpan Global Parameters (Sebagai "Rules" di Algoritma PSO)
params_list = [{"skill_name": k, "learn": v["learn"], "slip": v["slip"], "guess": v["guess"]} for k, v in params.items()]
pd.DataFrame(params_list).to_csv(OUTPUT_GLOBAL_PARAMS, index=False)
print(f"File Parameter Global PSO disimpan ke {OUTPUT_GLOBAL_PARAMS}")

# 3. Simpan Current State Murid (Sebagai titik "Start" partikel PSO)
last_states = df_history.groupby(['user_id', 'skill_name']).last().reset_index()
last_states = last_states[['user_id', 'skill_name', 'p_knowledge']]
last_states.to_csv(OUTPUT_STUDENT_MASTERY, index=False)
print(f"File State Penguasaan Murid disimpan ke {OUTPUT_STUDENT_MASTERY}")

# =========================
# EVALUASI AKURASI & RMSE
# =========================
df_eval = df_history.copy()
df_eval["error"] = df_eval["correct"] - df_eval["pred_correct"]
accuracy_total = (df_eval["correct"] == df_eval["pred_correct"]).mean()
rmse_total = np.sqrt((df_eval["error"]**2).mean())

skill_metrics = []
for skill in skills:
    df_s = df_eval[df_eval["skill_name"] == skill]
    acc = (df_s["correct"] == df_s["pred_correct"]).mean()
    rmse = np.sqrt(((df_s["correct"] - df_s["pred_correct"])**2).mean())
    skill_metrics.append({"skill_name": skill, "accuracy": acc, "rmse": rmse})

df_skill_metrics = pd.DataFrame(skill_metrics)
df_skill_metrics.loc[len(df_skill_metrics)] = {"skill_name": "TOTAL", "accuracy": accuracy_total, "rmse": rmse_total}
df_skill_metrics.to_csv(OUTPUT_EVAL, index=False)

print(f"\nAkurasi total: {accuracy_total:.3f}, RMSE total: {rmse_total:.3f}")