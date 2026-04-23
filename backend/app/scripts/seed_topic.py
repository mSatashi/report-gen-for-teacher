import sys
import uuid
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root))

from app.core.database import SessionLocal
from app.models.models import MataPelajaran, Topik, TopikPrasyarat

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
        mapel = db.query(MataPelajaran).filter(MataPelajaran.nama == "Matematika Dasar").first()
        if not mapel:
            mapel = MataPelajaran(id=str(uuid.uuid4()), nama="Matematika Dasar", kredit=40)
            db.add(mapel)
            db.commit()
            db.refresh(mapel)

        skills = list(skill_graph.keys())
        difficulty_map = {s: 0.2 + 0.8*(i/len(skills)) for i, s in enumerate(skills)}
        topik_dict = {}

        for skill in skills:
            existing = db.query(Topik).filter(Topik.nama == skill).first()
            if not existing:
                baru = Topik(
                    id=str(uuid.uuid4()),
                    mata_pelajaran_id=mapel.id,
                    nama=skill,
                    difficulty_index=difficulty_map[skill]
                )
                db.add(baru)
                topik_dict[skill] = baru
            else:
                topik_dict[skill] = existing
        db.commit()

        for skill, prereqs in skill_graph.items():
            topik_utama = db.query(Topik).filter(Topik.nama == skill).first()
            
            for req in prereqs:
                prasyarat = db.query(Topik).filter(Topik.nama == req).first()
                
                if not prasyarat:
                    prasyarat = Topik(
                        id=str(uuid.uuid4()),
                        mata_pelajaran_id=mapel.id,
                        nama=req,
                        difficulty_index=0.2
                    )
                    db.add(prasyarat)
                    db.commit()
                    db.refresh(prasyarat)

                relasi_ada = db.query(TopikPrasyarat).filter(
                    TopikPrasyarat.topik_id == topik_utama.id,
                    TopikPrasyarat.prasyarat_id == prasyarat.id
                ).first()

                if not relasi_ada:
                    relasi = TopikPrasyarat(
                        topik_id=topik_utama.id,
                        prasyarat_id=prasyarat.id
                    )
                    db.add(relasi)
        
        db.commit()
        print("Seeding Topik dan Prasyarat berhasil!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_topik()