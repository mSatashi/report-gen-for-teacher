from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Pengguna
from app.services.auth_service import require_pengajar
from app.services.dashboard_service import get_dashboard_data
from app.schemas.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardSummary)
def dashboard(
    current_user: Pengguna = Depends(require_pengajar),
    db: Session = Depends(get_db),
):
    """Ambil data ringkasan untuk dashboard pengajar."""
    return get_dashboard_data(db, current_user.id)
