from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Pengguna
from app.services.auth_service import require_pengajar
from app.services.dashboard_service import get_dashboard_data
from app.schemas.schemas import DashboardSummary
from typing import Annotated

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardSummary)
async def dashboard(
    current_user: Annotated[Pengguna, Depends(require_pengajar)],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardSummary:
    """Ambil data ringkasan untuk dashboard pengajar."""
    return get_dashboard_data(db, current_user)
