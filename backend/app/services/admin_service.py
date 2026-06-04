import uuid
from typing import List, Optional

from app.schemas.schemas import MuridResponse


from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token, blacklist_token, is_token_blacklisted
from app.models.models import Pengguna, Pengajar
from app.schemas.schemas import RegisterRequest, PenggunaResponse
from app.services.auth_service import get_current_user


def create_pengajar(db: Session, data: RegisterRequest) -> Pengguna:
    """Registrasi pengguna baru (pengajar)."""
    if db.query(Pengguna).filter(Pengguna.email_address == data.email_address).first():
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")
    if db.query(Pengguna).filter(Pengguna.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")

    user_id = str(uuid.uuid4())
    pengguna = Pengguna(
        id=user_id,
        username=data.username,
        email_address=data.email_address,
        hashed_password=hash_password(data.password),
        tipe_pengguna=data.tipe_pengguna,
    )
    db.add(pengguna)

    if data.tipe_pengguna == "pengajar":
        db.add(Pengajar(id=user_id))

    db.commit()
    db.refresh(pengguna)
    return pengguna

def get_all_pengajar(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
) -> List[PenggunaResponse]:
    query = db.query(Pengguna).filter(Pengguna.tipe_pengguna == "pengajar")
 
    if search:
        query = query.filter(Pengguna.username.ilike(f"%{search}%"))
 
    rows = query.offset(skip).limit(limit).all()
 
    result =[]
    for pengguna in rows:
        result.append(
            PenggunaResponse(
                id=str(pengguna.id),
                email_address=str(pengguna.email_address),
                username=str(pengguna.username),
                tipe_pengguna=str(pengguna.tipe_pengguna),
                is_active=bool(pengguna.is_active),
            )
        )
    return result

def get_pengajar_by_id(db: Session, pengajar_id: str) -> Optional[Pengguna]:
    return db.query(Pengguna).filter(Pengguna.id == pengajar_id, Pengguna.tipe_pengguna == "pengajar").first()

def delete_pengajar(db: Session, pengajar_id: str) -> bool:
    pengajar = get_pengajar_by_id(db, pengajar_id)
    if not pengajar:
        return False
    db.delete(pengajar)
    db.commit()
    return True

def require_admin(current_user: Pengguna = Depends(get_current_user)) -> Pengguna:
    """Dependency: hanya admin yang boleh akses endpoint ini."""
    if str(current_user.tipe_pengguna) != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat mengakses fitur ini")
    return current_user