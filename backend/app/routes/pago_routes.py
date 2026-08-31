from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pago import Pago
from app.models.orden import Orden

from app.schemas.pago_schema import (
    PagoCreate,
    PagoResponse
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
    dependencies=[Depends(get_current_user)]
)

# crear pago
@router.post("/", response_model=PagoResponse)

def crear_pago(
    pago: PagoCreate,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(
        Orden.id == pago.orden_id
    ).first()

    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )

    nuevo_pago = Pago(**pago.dict())

    db.add(nuevo_pago)

    # descontar saldo. NOTA: antes esto tambien forzaba
    # orden.estado = "pagado" cuando el saldo llegaba a 0, pero "pagado"
    # es un estado de COBRANZA, no del flujo operativo de la orden
    # (Pendiente/Diagnostico/.../Entregado) — un equipo puede estar
    # totalmente pagado y seguir en reparacion. Mezclar ambos rompia el
    # matching de estado en toda la UI (badges, donut, filtros). El saldo
    # ya alcanza para saber si esta pagada; el estado operativo se
    # cambia aparte, explicitamente, desde "Cambiar estado".
    orden.saldo = max(orden.saldo - pago.valor, 0)

    db.commit()

    db.refresh(nuevo_pago)

    return nuevo_pago

# listar pagos
@router.get("/", response_model=list[PagoResponse])

def listar_pagos(
    db: Session = Depends(get_db)
):
    return db.query(Pago).all()

# obtener pago
@router.get("/{pago_id}",
            response_model=PagoResponse)

def obtener_pago(
    pago_id: int,
    db: Session = Depends(get_db)
):
    pago = db.query(Pago).filter(
        Pago.id == pago_id
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    return pago

# eliminar pago
@router.delete("/{pago_id}")

def eliminar_pago(
    pago_id: int,
    db: Session = Depends(get_db)
):
    pago = db.query(Pago).filter(
        Pago.id == pago_id
    ).first()

    if not pago:
        raise HTTPException(
            status_code=404,
            detail="Pago no encontrado"
        )

    orden = db.query(Orden).filter(Orden.id == pago.orden_id).first()
    if orden:
        orden.saldo += pago.valor

    db.delete(pago)

    db.commit()

    return {
        "message": "Pago eliminado"
    }