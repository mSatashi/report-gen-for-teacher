from fastapi import APIRouter, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import RegisterRequest, PenggunaResponse

from app.models.models import Pengguna
from typing import List, Annotated, Optional

from app.services.admin_service import create_pengajar, get_all_pengajar, require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/tambah-pengajar", status_code=201)
def tambah_pengajar(data: RegisterRequest, db: Annotated[Session, Depends(get_db)], current_user: Annotated[Pengguna, Depends(require_admin)]):
    """Registrasi pengguna baru (pengajar atau murid)."""
    user = create_pengajar(db, data)
    return {"message": "Pengajar berhasil ditambahkan", "user_id": user.id, "tipe": user.tipe_pengguna}


@router.get("/list-pengajar", response_model=List[PenggunaResponse], status_code=status.HTTP_200_OK)
def list_all_pengajar(
    skip: int = Query(0, ge=0, description="Offset paginasi"),
    limit: int = Query(100, ge=1, le=500, description="Jumlah maksimal data"),
    search: Optional[str] = Query(None, description="Filter nama siswa"),
    db: Session = Depends(get_db),
    current_user: Pengguna = Depends(require_admin)
):
    return get_all_pengajar(db, skip=skip, limit=limit, search=search)