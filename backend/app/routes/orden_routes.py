from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historial_estado import HistorialEstado
from app.models.orden import Orden
from app.models.usuario import Usuario
from app.schemas.orden_schema import (
    OrdenCreate,
    OrdenResponse
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/ordenes",
    tags=["Ordenes"],
    dependencies=[Depends(get_current_user)]
)

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

    # Codigo de seguimiento amigable para que el cliente lo consulte en
    # /publico/seguimiento sin tener que usar el id crudo de la base de
    # datos. Se genera despues del insert porque depende del id asignado.
    if not nueva_orden.numero_orden:
        nueva_orden.numero_orden = f"FF-{nueva_orden.id:06d}"
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
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    orden = db.query(Orden).filter(
        Orden.id == orden_id
    ).first()

    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )

    estado_anterior = orden.estado

    for key, value in datos.dict().items():
        setattr(orden, key, value)

    # Registra el cambio en historial_estados solo cuando el estado
    # realmente cambio (un PUT que actualiza otros campos sin tocar el
    # estado no genera ruido en el historial). Esto habilita metricas
    # honestas como "tiempo promedio en cada estado" o "dias sin
    # movimiento" en el dashboard, en vez de aproximarlas con
    # fecha_ingreso para todo.
    if orden.estado != estado_anterior:
        db.add(HistorialEstado(
            orden_id=orden.id,
            estado_anterior=estado_anterior,
            estado_nuevo=orden.estado,
            usuario_id=usuario.id,
        ))

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