from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.topik_service import tambah_prasyarat

router = APIRouter(prefix="/api/v1/topik", tags=["Topik"])

@router.post("/{topik_id}/prasyarat/{prasyarat_id}")
def endpoint_tambah_prasyarat(
    topik_id: str,
    prasyarat_id: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint untuk menambahkan relasi prasyarat pada sebuah topik.

    Path Parameter:
    - topik_id: ID topik utama
    - prasyarat_id: ID topik yang akan dijadikan prasyarat

    Dependency:
    - db: Session database yang di-inject oleh FastAPI

    Proses:
    - Memanggil service `tambah_prasyarat`
    - Service akan melakukan validasi:
        1. Topik harus ada
        2. Tidak boleh self-dependency
        3. Tidak boleh terjadi cyclic dependency (menggunakan DFS)

    Return:
    - Response sukses jika prasyarat berhasil ditambahkan

    Error:
    - 400: Jika terjadi validasi gagal (self atau siklus)
    - 404: Jika topik tidak ditemukan
    """
    return tambah_prasyarat(db, topik_id, prasyarat_id)