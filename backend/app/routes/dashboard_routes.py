from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal

from app.models.cliente import Cliente
from app.models.orden import Orden
from app.models.pago import Pago

from app.schemas.dashboard_schema import (
    DashboardResponse
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# conexión db
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

@router.get("/",
            response_model=DashboardResponse)

def obtener_dashboard(
    db: Session = Depends(get_db)
):

    total_clientes = db.query(
        Cliente
    ).count()

    total_ordenes = db.query(
        Orden
    ).count()

    ordenes_activas = db.query(
        Orden
    ).filter(
        Orden.estado != "entregado"
    ).count()

    ordenes_entregadas = db.query(
        Orden
    ).filter(
        Orden.estado == "entregado"
    ).count()

    ingresos_totales = db.query(
        func.coalesce(
            func.sum(Pago.valor),
            0
        )
    ).scalar()

    saldo_pendiente = db.query(
        func.coalesce(
            func.sum(Orden.saldo),
            0
        )
    ).scalar()

    total_pagos = db.query(
        Pago
    ).count()

    return {
        "total_clientes": total_clientes,
        "total_ordenes": total_ordenes,
        "ordenes_activas": ordenes_activas,
        "ordenes_entregadas": ordenes_entregadas,
        "ingresos_totales": ingresos_totales,
        "saldo_pendiente": saldo_pendiente,
        "total_pagos": total_pagos
    }