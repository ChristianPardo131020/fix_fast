from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historial_estado import HistorialEstado
from app.models.orden import Orden
from app.models.pago import Pago
from app.models.usuario import Usuario
from app.schemas.orden_schema import (
    OrdenCreate,
    OrdenResponse
)
from app.schemas.historial_estado_schema import HistorialEstadoResponse
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
    # Mas nueva primero. fecha_ingreso es la fecha de negocio (la que se
    # ve en la tarjeta); id de desempate para ordenes cargadas el mismo
    # dia, para que el orden no salte entre refrescos.
    return db.query(Orden).order_by(Orden.fecha_ingreso.desc(), Orden.id.desc()).all()

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

# historial de estados de una orden (traza: cuando cambio de pendiente a
# listo, a entregado, etc. -- se llena solo, ver actualizar_orden)
@router.get("/{orden_id}/historial", response_model=list[HistorialEstadoResponse])

def historial_orden(
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

    return (
        db.query(HistorialEstado)
        .filter(HistorialEstado.orden_id == orden_id)
        .order_by(HistorialEstado.created_at.asc())
        .all()
    )

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

    # pagos e historial_estados apuntan a esta orden por foreign key sin
    # CASCADE -- borrar la orden directamente violaba esa FK y tiraba un
    # 500 en cualquier orden que ya tuviera un pago o un cambio de
    # estado registrado (con la traza nueva, eso ya es casi cualquier
    # orden). Se borran primero, en la misma transaccion.
    db.query(Pago).filter(Pago.orden_id == orden_id).delete()
    db.query(HistorialEstado).filter(HistorialEstado.orden_id == orden_id).delete()

    db.delete(orden)

    db.commit()

    return {
        "message": "Orden eliminada"
    }