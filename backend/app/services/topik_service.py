from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import TopikPrasyarat, Topik

def cek_siklus_prasyarat(db: Session, topik_id: str, prasyarat_id: str) -> bool:
    """
    Mengecek apakah penambahan relasi prasyarat akan menyebabkan siklus.

    Parameter:
    - db: Session database
    - topik_id: ID topik utama
    - prasyarat_id: ID topik yang akan dijadikan prasyarat

    Return:
    - True  -> jika terjadi siklus
    - False -> jika aman (tidak ada siklus)

    Cara kerja:
    Menggunakan Depth-First Search (DFS) untuk menelusuri graph prasyarat.
    Jika dalam traversal ditemukan kembali ke topik awal (topik_id),
    maka berarti terjadi siklus.
    """
    visited = set()

    def dfs(current_id: str) -> bool:
        """
        Fungsi rekursif DFS untuk menelusuri hubungan prasyarat.

        Parameter:
        - current_id: ID topik yang sedang ditelusuri

        Return:
        - True jika ditemukan siklus
        - False jika tidak
        """

        # Jika kembali ke topik awal → siklus terdeteksi
        if current_id == topik_id:
            return True

        # Hindari loop tak berujung dengan mengecek node yang sudah dikunjungi
        if current_id in visited:
            return False

        visited.add(current_id)

        # Ambil semua prasyarat dari topik saat ini
        prereqs = db.query(TopikPrasyarat)\
                    .filter(TopikPrasyarat.topik_id == current_id)\
                    .all()

        # Telusuri setiap prasyarat
        for req in prereqs:
            if dfs(req.prasyarat_id):
                return True

        return False

    # Mulai DFS dari prasyarat yang ingin ditambahkan
    return dfs(prasyarat_id)


def tambah_prasyarat(db: Session, topik_id: str, prasyarat_id: str):
    """
    Menambahkan relasi prasyarat antar topik dengan validasi lengkap.

    Validasi yang dilakukan:
    1. Memastikan kedua topik ada di database
    2. Mencegah topik menjadi prasyarat dirinya sendiri
    3. Mencegah terbentuknya siklus (circular dependency)

    Parameter:
    - db: Session database
    - topik_id: ID topik utama
    - prasyarat_id: ID topik yang akan dijadikan prasyarat

    Return:
    - Dictionary berisi pesan sukses jika berhasil

    Exception:
    - 404 jika topik tidak ditemukan
    - 400 jika invalid (self-reference atau siklus)
    """

    # 1. Pastikan kedua topik ada
    if not db.query(Topik).filter(Topik.id == topik_id).first() or \
       not db.query(Topik).filter(Topik.id == prasyarat_id).first():
        raise HTTPException(status_code=404, detail="Topik tidak ditemukan")

    # 2. Cegah self-dependency (topik jadi prasyarat dirinya sendiri)
    if topik_id == prasyarat_id:
        raise HTTPException(
            status_code=400,
            detail="Topik tidak bisa menjadi prasyarat untuk dirinya sendiri"
        )

    # 3. Validasi siklus menggunakan DFS
    if cek_siklus_prasyarat(db, topik_id, prasyarat_id):
        raise HTTPException(
            status_code=400,
            detail="Gagal: Penambahan ini akan menciptakan siklus prasyarat (Lingkaran Setan)"
        )

    # 4. Simpan relasi jika semua validasi lolos
    relasi_baru = TopikPrasyarat(
        topik_id=topik_id,
        prasyarat_id=prasyarat_id
    )
    db.add(relasi_baru)
    db.commit()

    return {"message": "Prasyarat berhasil ditambahkan"}