import os
import pandas as pd
import numpy as np
from datetime import datetime

OUTPUT_GLOBAL_PARAMS = "models/bkt_global_params.csv"
OUTPUT_STUDENT_MASTERY = "models/current_student_mastery.csv"
OUTPUT_EVALUATION = "models/pso_evaluation_results.csv"

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

external_mastered = {"penjumlahan", "pengurangan", "perkalian", "pembagian", "pecahan", "persentase", "keliling_luas", "pengolahan_data_dasar"}

try:
    df_params = pd.read_csv(OUTPUT_GLOBAL_PARAMS)
    df_mastery = pd.read_csv(OUTPUT_STUDENT_MASTERY)
except FileNotFoundError:
    raise RuntimeError("File model BKT tidak ditemukan. Jalankan 02_bkt_tuning.py terlebih dahulu.")

params_dict = df_params.set_index('skill_name').to_dict('index')

TARGET_MASTERY = 0.90
NUM_PARTICLES = 40
MAX_ITER = 100
W = 0.5   
C1 = 1.5  
C2 = 1.5  

def get_unmastered_skills(student_id):
    student_data = df_mastery[df_mastery['user_id'] == student_id]
    state_dict = student_data.set_index('skill_name')['p_knowledge'].to_dict()
    
    unmastered = []
    initial_states = {}
    
    for skill in skill_graph.keys():
        p = state_dict.get(skill, 0.2) 
        initial_states[skill] = p
        if p < TARGET_MASTERY:
            unmastered.append(skill)
            
    return unmastered, initial_states

def fitness_function(sequence, unmastered_skills, initial_states):
    penalty = 0
    total_attempts = 0
    current_states = initial_states.copy()
    
    mastered_so_far = set([s for s in skill_graph.keys() if s not in unmastered_skills])
    mastered_so_far.update(external_mastered)
    
    previous_skill = None
    
    for skill in sequence:
        prereqs = skill_graph.get(skill, [])
        for req in prereqs:
            if req not in mastered_so_far:
                penalty += 1000 
                
        p_known = current_states[skill]
        learn_rate = params_dict.get(skill, {}).get('learn', 0.15)
        
        if previous_skill is not None:
            if previous_skill in prereqs:
                learn_rate = learn_rate * 1.5 
            else:
                learn_rate = learn_rate * 0.9 
                
        attempts = 0
        while p_known < TARGET_MASTERY and attempts < 50:
            p_known = p_known + (1 - p_known) * learn_rate
            attempts += 1
            
        total_attempts += attempts
        current_states[skill] = p_known
        mastered_so_far.add(skill)
        previous_skill = skill
        
    return total_attempts + penalty

def run_pso_for_student(student_id):
    unmastered_skills, initial_states = get_unmastered_skills(student_id)
    
    if not unmastered_skills:
        return 0, 0, [], 0
        
    num_skills = len(unmastered_skills)
    
    static_sequence = [s for s in skill_graph.keys() if s in unmastered_skills]
    baseline_attempts = fitness_function(static_sequence, unmastered_skills, initial_states)
    
    particles_position = np.random.rand(NUM_PARTICLES, num_skills)
    particles_velocity = np.random.uniform(-1, 1, (NUM_PARTICLES, num_skills))
    
    particles_position[0] = np.arange(num_skills)
    
    pbest_position = particles_position.copy()
    pbest_value = np.full(NUM_PARTICLES, np.inf)
    
    gbest_position = np.zeros(num_skills)
    gbest_value = np.inf
    
    for iteration in range(MAX_ITER):
        for i in range(NUM_PARTICLES):
            sort_indices = np.argsort(particles_position[i])
            sequence = [unmastered_skills[idx] for idx in sort_indices]
            
            fit_value = fitness_function(sequence, unmastered_skills, initial_states)
            
            if fit_value < pbest_value[i]:
                pbest_value[i] = fit_value
                pbest_position[i] = particles_position[i].copy()
                
            if fit_value < gbest_value:
                gbest_value = fit_value
                gbest_position = particles_position[i].copy()
                
        r1 = np.random.rand(NUM_PARTICLES, num_skills)
        r2 = np.random.rand(NUM_PARTICLES, num_skills)
        
        particles_velocity = (W * particles_velocity + 
                              C1 * r1 * (pbest_position - particles_position) + 
                              C2 * r2 * (gbest_position - particles_position))
        particles_position = particles_position + particles_velocity

    best_indices = np.argsort(gbest_position)
    best_sequence = [unmastered_skills[idx] for idx in best_indices]
    
    penalty_incurred = 1 if gbest_value >= 1000 else 0
    
    return gbest_value, baseline_attempts, best_sequence, penalty_incurred

def evaluate_all_students():
    print("Memulai Evaluasi PSO untuk semua student...")
    start_time = datetime.now()
    
    all_students = df_mastery['user_id'].unique()
    results = []
    
    for idx, student_id in enumerate(all_students, 1):
        pso_attempts, base_attempts, best_seq, is_penalized = run_pso_for_student(student_id)
        
        if len(best_seq) > 0:
            efficiency = ((base_attempts - pso_attempts) / base_attempts) * 100
            
            results.append({
                "student_id": student_id,
                "unmastered_count": len(best_seq),
                "baseline_attempts": base_attempts,
                "pso_attempts": pso_attempts,
                "efficiency_percent": round(efficiency, 2),
                "is_penalized": is_penalized,
                "recommended_path": " -> ".join(best_seq)
            })
            
        if idx % 50 == 0:
            print(f"Memproses {idx}/{len(all_students)} students...")
            
    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_EVALUATION, index=False)
    
    end_time = datetime.now()
    
    avg_baseline = df_results['baseline_attempts'].mean()
    avg_pso = df_results['pso_attempts'].mean()
    avg_efficiency = df_results['efficiency_percent'].mean()
    total_penalties = df_results['is_penalized'].sum()
    
    print("\n" + "="*40)
    print("HASIL EVALUASI PSO LEARNING PATH")
    print("="*40)
    print(f"Total Student Dievaluasi : {len(df_results)}")
    print(f"Rata-rata Latihan (Statis) : {avg_baseline:.1f} attempts")
    print(f"Rata-rata Latihan (PSO)    : {avg_pso:.1f} attempts")
    print(f"Peningkatan Efisiensi      : {avg_efficiency:.2f} %")
    print(f"Partikel Gagal (Kena Penalti): {total_penalties} student")
    print(f"Waktu Eksekusi             : {end_time - start_time}")
    print(f"Data lengkap disimpan di   : {OUTPUT_EVALUATION}")

if __name__ == "__main__":
    evaluate_all_students()