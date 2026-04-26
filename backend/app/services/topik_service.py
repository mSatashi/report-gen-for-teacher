from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import TopikPrasyarat, Topik
from app.schemas.schemas import TopikUpdate

# --- LOGIKA VALIDASI GRAPH (DFS) ---
def cek_siklus_prasyarat(db: Session, topik_id: str, prasyarat_id: str) -> bool:
    visited = set()
    def dfs(current_id: str) -> bool:
        if current_id == topik_id: return True
        if current_id in visited: return False
        visited.add(current_id)
        prereqs = db.query(TopikPrasyarat).filter(TopikPrasyarat.topik_id == current_id).all()
        for req in prereqs:
            if dfs(req.prasyarat_id): return True
        return False
    return dfs(prasyarat_id)

# --- CRUD TOPIK ---

def update_topik(db: Session, topik_id: str, data: TopikUpdate):
    topik = db.query(Topik).filter(Topik.id == topik_id).first()
    if not topik:
        raise HTTPException(status_code=404, detail="Topik tidak ditemukan")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(topik, key, value)
    
    db.commit()
    db.refresh(topik)
    return topik

def delete_topik(db: Session, topik_id: str):
    topik = db.query(Topik).filter(Topik.id == topik_id).first()
    if not topik:
        raise HTTPException(status_code=404, detail="Topik tidak ditemukan")
    
    db.delete(topik)
    db.commit()
    return {"message": f"Topik '{topik.nama}' dan relasi terkait berhasil dihapus"}

# --- MANAJEMEN PRASYARAT ---

def tambah_prasyarat(db: Session, topik_id: str, prasyarat_id: str):
    if not db.query(Topik).filter(Topik.id == topik_id).first() or \
       not db.query(Topik).filter(Topik.id == prasyarat_id).first():
        raise HTTPException(status_code=404, detail="Topik tidak ditemukan")

    if topik_id == prasyarat_id:
        raise HTTPException(status_code=400, detail="Topik tidak bisa menjadi prasyarat dirinya sendiri")

    # Cek apakah sudah ada relasi yang sama
    existing = db.query(TopikPrasyarat).filter(
        TopikPrasyarat.topik_id == topik_id, 
        TopikPrasyarat.prasyarat_id == prasyarat_id
    ).first()
    if existing:
        return {"message": "Relasi prasyarat sudah ada"}

    if cek_siklus_prasyarat(db, topik_id, prasyarat_id):
        raise HTTPException(status_code=400, detail="Gagal: Penambahan ini akan menciptakan siklus (Circular Dependency)")

    relasi_baru = TopikPrasyarat(topik_id=topik_id, prasyarat_id=prasyarat_id)
    db.add(relasi_baru)
    db.commit()
    return {"message": "Prasyarat berhasil ditambahkan"}

def hapus_prasyarat(db: Session, topik_id: str, prasyarat_id: str):
    relasi = db.query(TopikPrasyarat).filter(
        TopikPrasyarat.topik_id == topik_id,
        TopikPrasyarat.prasyarat_id == prasyarat_id
    ).first()
    
    if not relasi:
        raise HTTPException(status_code=404, detail="Relasi prasyarat tidak ditemukan")
    
    db.delete(relasi)
    db.commit()
    return {"message": "Hubungan prasyarat berhasil dihapus"}