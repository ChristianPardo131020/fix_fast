from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.orden import Orden
from app.schemas.orden_schema import (
    OrdenCreate,
    OrdenResponse
)

router = APIRouter(
    prefix="/ordenes",
    tags=["Ordenes"]
)

# conexión db
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# crear orden
@router.post("/", response_model=OrdenResponse)

def crear_orden(
    orden: OrdenCreate,
    db: Session = Depends(get_db)
):
    nueva_orden = Orden(**orden.dict())

    db.add(nueva_orden)

    db.commit()

    db.refresh(nueva_orden)

    return nueva_orden

# listar órdenes
@router.get("/", response_model=list[OrdenResponse])

def listar_ordenes(
    db: Session = Depends(get_db)
):
    return db.query(Orden).all()

# obtener orden
@router.get("/{orden_id}",
            response_model=OrdenResponse)

def obtener_orden(
    orden_id: int,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(
        Orden.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )

    return orden

# actualizar orden
@router.put("/{orden_id}",
            response_model=OrdenResponse)

def actualizar_orden(
    orden_id: int,
    datos: OrdenCreate,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(
        Orden.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )

    for key, value in datos.dict().items():
        setattr(orden, key, value)

    db.commit()

    db.refresh(orden)

    return orden

# eliminar orden
@router.delete("/{orden_id}")

def eliminar_orden(
    orden_id: int,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(
        Orden.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )

    db.delete(orden)

    db.commit()

    return {
        "message": "Orden eliminada"
    }