import sys
import uuid
from pathlib import Path

# Setup path agar bisa import app
root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from app.core.database import SessionLocal
from app.models.models import MataPelajaran, Topik, TopikPrasyarat

# Definisi Skill Graph (Prasyarat)
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

def seed_topik():
    db = SessionLocal()
    try:
        # 1. Cari atau buat Mata Pelajaran
        # PERBAIKAN: Menggunakan nama_mata_pelajaran sesuai models.py
        nama_mapel = "Matematika Dasar"
        mapel = db.query(MataPelajaran).filter(MataPelajaran.nama_mata_pelajaran == nama_mapel).first()
        
        if not mapel:
            print(f"Membuat mata pelajaran: {nama_mapel}")
            mapel = MataPelajaran(
                id=str(uuid.uuid4()), 
                nama_mata_pelajaran=nama_mapel, 
                kredit=40
            )
            db.add(mapel)
            db.commit()
            db.refresh(mapel)

        # 2. Buat semua Topik terlebih dahulu
        skills = list(skill_graph.keys())
        # Tambahkan juga skill yang ada di dalam list prasyarat tapi tidak ada di key utama
        all_skill_names = set(skills)
        for prereqs in skill_graph.values():
            for p in prereqs:
                all_skill_names.add(p)
        
        all_skill_names = list(all_skill_names)
        difficulty_map = {s: round(0.2 + 0.7*(i/len(all_skill_names)), 2) for i, s in enumerate(all_skill_names)}

        print(f"Menyisipkan {len(all_skill_names)} topik...")
        for skill_name in all_skill_names:
            existing = db.query(Topik).filter(Topik.nama == skill_name).first()
            if not existing:
                baru = Topik(
                    id=str(uuid.uuid4()),
                    mata_pelajaran_id=mapel.id,
                    nama=skill_name,
                    difficulty_index=difficulty_map.get(skill_name, 0.5)
                )
                db.add(baru)
        
        db.commit() # Commit agar ID topik tersedia untuk relasi prasyarat

        # 3. Buat Relasi Prasyarat (Self-referential)
        print("Membangun relasi prasyarat (Skill Graph)...")
        for skill, prereqs in skill_graph.items():
            topik_utama = db.query(Topik).filter(Topik.nama == skill).first()
            
            for req_name in prereqs:
                prasyarat_obj = db.query(Topik).filter(Topik.nama == req_name).first()
                
                if topik_utama and prasyarat_obj:
                    # Cek apakah relasi sudah ada
                    relasi_ada = db.query(TopikPrasyarat).filter(
                        TopikPrasyarat.topik_id == topik_utama.id,
                        TopikPrasyarat.prasyarat_id == prasyarat_obj.id
                    ).first()

                    if not relasi_ada:
                        relasi = TopikPrasyarat(
                            topik_id=topik_utama.id,
                            prasyarat_id=prasyarat_obj.id
                        )
                        db.add(relasi)
        
        db.commit()
        print("✅ Seeding Topik dan Prasyarat berhasil!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_topik()