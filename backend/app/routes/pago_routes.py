from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.pago import Pago
from app.models.orden import Orden

from app.schemas.pago_schema import (
    PagoCreate,
    PagoResponse
)

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)

# conexión db
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

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

    # descontar saldo
    orden.saldo = orden.saldo - pago.valor

    # si saldo <= 0
    if orden.saldo <= 0:
        orden.saldo = 0
        orden.estado = "pagado"

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

    db.delete(pago)

    db.commit()

    return {
        "message": "Pago eliminado"
    }