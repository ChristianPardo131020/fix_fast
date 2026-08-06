from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard_schema import DashboardResponse
from app.services.dashboard_service import build_dashboard
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=DashboardResponse)
def obtener_dashboard(
    year: int = Query(default_factory=lambda: datetime.utcnow().year, ge=2000, le=2100),
    month: Optional[int] = Query(default=None, ge=1, le=12, description="1-12, o vacio para ver todo el año"),
    chart_granularity: Optional[str] = Query(
        default=None,
        pattern="^(day|week|month|year)$",
        description="Granularidad del grafico de flujo de caja. Por defecto: 'day' si hay mes elegido, 'month' si es todo el año.",
    ),
    db: Session = Depends(get_db),
):
    """
    Todo lo que necesita el dashboard en una sola llamada, ya agregado:
    kpis, cashflow, estados de ordenes, metodos de pago, alertas
    automaticas y KPIs secundarios. El frontend no calcula nada — solo
    pinta esta respuesta.
    """
    return build_dashboard(db, year=year, month=month, chart_granularity=chart_granularity)
