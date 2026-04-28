import logging
import numpy as np

logger = logging.getLogger(__name__)

TARGET_MASTERY = 0.85
NUM_PARTICLES = 40
MAX_ITER = 100
W, C1, C2 = 0.5, 1.5, 1.5

def run_pso_algorithm(
    murid_id: str, 
    knowledge_state: dict, 
    skill_graph_dict: dict, 
    skill_params_dict: dict,
    heuristic_sequence: list,
    sisa_sesi: int
) -> dict:
    """
    Menjalankan algoritma Particle Swarm Optimization (PSO) untuk menentukan
    urutan pembelajaran optimal bagi siswa.

    Parameter:
    - murid_id: ID siswa
    - knowledge_state: dict {skill: probabilitas penguasaan saat ini}
    - skill_graph_dict: dict {skill: [prasyarat]}
    - skill_params_dict: dict {skill: learning rate}
    - heuristic_sequence: urutan awal (baseline) dari database (mudah → sulit)
    - sisa_sesi: jumlah sesi belajar yang tersedia

    Return:
    - rekomendasi_materi: list urutan topik optimal
    - jadwal_mingguan: distribusi topik per minggu
    - catatan_analisa: insight hasil optimasi
    - estimasi_selesai_minggu: jumlah minggu
    - prioritas_perhatian: topik awal yang perlu difokuskan

    Catatan:
    - Menggunakan pendekatan continuous PSO yang dipetakan ke urutan diskrit
      melalui sorting indeks.
    """

    logger.info(f"Memulai PSO di background process untuk murid {murid_id}")

    # Ambil skill yang belum mencapai target mastery
    unmastered_skills = [
        s for s in heuristic_sequence 
        if knowledge_state.get(s, 0.2) < TARGET_MASTERY
    ]
    
    # Jika semua sudah dikuasai → tidak perlu rekomendasi
    is_review_mode = False
    if not unmastered_skills:
        # Jika semua sudah dikuasai, gunakan semua topik yang ada untuk pengulangan
        unmastered_skills = heuristic_sequence
        is_review_mode = True

    # Jika benar-benar tidak ada topik sama sekali di kurikulum (Sequence Kosong)
    if not unmastered_skills:
        return {
            "rekomendasi_materi": [],
            "jadwal_mingguan": [],
            "catatan_analisa": "Tidak ada topik yang ditemukan dalam mata pelajaran ini.",
            "estimasi_selesai_minggu": 0,
            "prioritas_perhatian": []
        }

    # Asumsi: skill di luar daftar ini dianggap sudah dikuasai (ghost prerequisite)
    mastered_so_far_baseline = set(skill_graph_dict.keys()) - set(unmastered_skills)

    num_skills = len(unmastered_skills)

    def fitness_function(sequence):
        """
        Menghitung nilai fitness dari suatu urutan pembelajaran (sequence).

        Komponen penilaian:
        1. Penalti prasyarat:
          - Jika suatu topik dipelajari sebelum prasyaratnya dikuasai,
            akan dikenakan penalti besar.

        2. Total usaha belajar:
          - Mengukur jumlah iterasi (attempts) yang dibutuhkan untuk mencapai
            TARGET_MASTERY pada setiap skill.

        3. Cognitive Momentum (urutan belajar adaptif):
          - Jika skill sebelumnya adalah prasyarat langsung:
            → learning rate ditingkatkan (belajar lebih cepat)
          - Jika tidak berhubungan:
            → learning rate diturunkan (biaya pindah konteks)

        Tujuan:
        Menghasilkan urutan belajar yang efisien, logis, dan minim gangguan kognitif.

        Parameter:
        - sequence: list urutan skill/topik

        Return:
        - Nilai fitness (semakin kecil semakin baik)
        """

        penalty = 0
        total_attempts = 0

        # Inisialisasi probabilitas penguasaan awal setiap skill
        current_states = {
            s: knowledge_state.get(s, 0.2)
            for s in unmastered_skills
        }

        # Set skill yang sudah dianggap dikuasai
        mastered_so_far = set(mastered_so_far_baseline)
        
        previous_skill = None  # Menyimpan skill sebelumnya (untuk momentum)

        for skill in sequence:
            # Ambil daftar prasyarat skill saat ini
            prereqs = skill_graph_dict.get(skill, [])

            # Cek pelanggaran prasyarat
            for req in prereqs:
                if req not in mastered_so_far:
                    penalty += 1000  # penalti besar
                        
            # Ambil state awal dan learning rate dasar
            p_known = current_states[skill]
            learn_rate = skill_params_dict.get(skill, 0.15)
            
            # Penyesuaian learning rate berdasarkan urutan sebelumnya
            if previous_skill is not None:
                if previous_skill in prereqs:
                    # Bonus: urutan sesuai alur belajar (prasyarat → lanjutan)
                    learn_rate = min(learn_rate * 1.5, 0.99)
                else:
                    # Penalti: perpindahan konteks
                    learn_rate = learn_rate * 0.9
            
            # Simulasi proses belajar hingga mencapai target mastery
            attempts = 0
            while p_known < TARGET_MASTERY and attempts < 50:
                p_known = p_known + (1 - p_known) * learn_rate
                attempts += 1
                    
            total_attempts += attempts

            # Tandai skill sudah dikuasai
            mastered_so_far.add(skill)

            # Simpan skill sebagai referensi untuk iterasi berikutnya
            previous_skill = skill

        # Nilai fitness akhir
        return total_attempts + penalty

    # Inisialisasi partikel (posisi & kecepatan)
    particles_position = np.random.rand(NUM_PARTICLES, num_skills)
    particles_velocity = np.random.uniform(-1, 1, (NUM_PARTICLES, num_skills))
    
    # Inject solusi heuristik sebagai starting point (partikel pertama)
    particles_position[0] = np.arange(num_skills)

    # Personal best & global best
    pbest_position = particles_position.copy()
    pbest_value = np.full(NUM_PARTICLES, np.inf)
    gbest_position = np.zeros(num_skills)
    gbest_value = np.inf

    # Loop utama PSO
    for _ in range(MAX_ITER):
        for i in range(NUM_PARTICLES):
            # Ubah posisi → urutan diskrit
            sort_indices = np.argsort(particles_position[i])
            sequence = [unmastered_skills[idx] for idx in sort_indices]
            
            fit_value = fitness_function(sequence)
            
            # Update personal best
            if fit_value < pbest_value[i]:
                pbest_value[i] = fit_value
                pbest_position[i] = particles_position[i].copy()
                
            # Update global best
            if fit_value < gbest_value:
                gbest_value = fit_value
                gbest_position = particles_position[i].copy()
                
        # Update velocity & posisi
        r1 = np.random.rand(NUM_PARTICLES, num_skills)
        r2 = np.random.rand(NUM_PARTICLES, num_skills)

        particles_velocity = (
            W * particles_velocity + 
            C1 * r1 * (pbest_position - particles_position) + 
            C2 * r2 * (gbest_position - particles_position)
        )

        particles_position = particles_position + particles_velocity

    # Ambil solusi terbaik
    best_indices = np.argsort(gbest_position)
    best_sequence = [unmastered_skills[idx] for idx in best_indices]

    # Batasi sesuai jumlah sesi tersedia
    rute_rekomendasi = best_sequence[:sisa_sesi]
    
    # Generate jadwal mingguan (2 sesi/minggu)
    temp_jadwal = {}
    for i, topik in enumerate(rute_rekomendasi):
        minggu = f"Minggu {(i // 2) + 1}"
        temp_jadwal.setdefault(minggu,[]).append(topik)


    jadwal_mingguan =[{"minggu": k, "topik": v} for k, v in temp_jadwal.items()]

    # Insight hasil optimasi
    catatan = f"Rute dioptimasi dengan PSO. Estimasi latihan: {int(gbest_value)} iterasi kognitif."
    
    if gbest_value >= 1000:
        catatan += (
            " (Peringatan: Terdapat pelanggaran prasyarat akibat "
            "sisa sesi terlalu sedikit atau konflik kurikulum)."
        )

    if is_review_mode:
        catatan = "Siswa sudah menguasai seluruh target (≥85%). Jadwal di atas adalah sesi Review & Penguatan."

    return {
        "rekomendasi_materi": rute_rekomendasi,
        "jadwal_mingguan": jadwal_mingguan,
        "catatan_analisa": catatan,
        "estimasi_selesai_minggu": len(jadwal_mingguan),
        "prioritas_perhatian": rute_rekomendasi[:2]
    }