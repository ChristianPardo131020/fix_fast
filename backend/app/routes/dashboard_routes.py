from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db

from app.models.cliente import Cliente
from app.models.orden import Orden
from app.models.pago import Pago
from app.models.movimiento_caja import MovimientoCaja

from app.schemas.dashboard_schema import (
    DashboardResponse
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(get_current_user)]
)

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

    # Ingresos totales = pagos facturados de ordenes + otros ingresos
    # sin factura (ventas de pilas, accesorios, etc. registrados en
    # movimientos_caja con tipo="ingreso").
    ingresos_pagos = db.query(
        func.coalesce(
            func.sum(Pago.valor),
            0
        )
    ).scalar()

    otros_ingresos = db.query(
        func.coalesce(
            func.sum(MovimientoCaja.valor),
            0
        )
    ).filter(
        MovimientoCaja.tipo == "ingreso"
    ).scalar()

    ingresos_totales = ingresos_pagos + otros_ingresos

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