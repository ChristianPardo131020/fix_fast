from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historial_estado import HistorialEstado
from app.models.orden import Orden
from app.models.pago import Pago
from app.models.usuario import Usuario
from app.models.used_part import UsedPart
from app.models.producto import Producto
from app.models.movimiento_inventario import MovimientoInventario
from app.schemas.orden_schema import (
    OrdenCreate,
    OrdenResponse
)
from app.schemas.historial_estado_schema import HistorialEstadoResponse
from app.schemas.used_part_schema import UsedPartCreate, UsedPartResponse
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/ordenes",
    tags=["Ordenes"],
    dependencies=[Depends(get_current_user)]
)

# siguiente numero de orden (para mostrarlo en el formulario antes de guardar)
@router.get("/siguiente-numero")
def siguiente_numero(db: Session = Depends(get_db)):
    last_order = db.query(Orden.numero_orden).order_by(Orden.id.desc()).first()
    if last_order and last_order[0] and last_order[0].isdigit():
        next_num = max(17761, int(last_order[0]) + 1)
    else:
        next_num = 17761
    return {"numero_orden": str(next_num)}


# crear orden
@router.post("/", response_model=OrdenResponse)

def crear_orden(
    orden: OrdenCreate,
    db: Session = Depends(get_db)
):
    datos = orden.dict()
    # Ignorar numero_orden del frontend — siempre se genera en el backend
    # para garantizar el consecutivo único incluso con concurrencia.
    datos.pop("numero_orden", None)
    nueva_orden = Orden(**datos)

    # Generar el numero de orden consecutivo
    last_order = db.query(Orden.numero_orden).order_by(Orden.id.desc()).first()
    if last_order and last_order[0] and last_order[0].isdigit():
        next_num = max(17761, int(last_order[0]) + 1)
    else:
        next_num = 17761
    nueva_orden.numero_orden = str(next_num)

    db.add(nueva_orden)

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

# obtener repuestos de una orden
@router.get("/{orden_id}/repuestos", response_model=list[UsedPartResponse])
def obtener_repuestos(
    orden_id: int,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )
    return db.query(UsedPart).filter(UsedPart.orden_id == orden_id).all()

# agregar repuesto a una orden
@router.post("/{orden_id}/repuestos", response_model=UsedPartResponse)
def agregar_repuesto(
    orden_id: int,
    payload: UsedPartCreate,
    db: Session = Depends(get_db)
):
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    if not orden:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )

    producto = db.query(Producto).filter(Producto.id == payload.producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    if producto.stock_actual < payload.cantidad:
        raise HTTPException(
            status_code=400,
            detail="Stock insuficiente en inventario"
        )

    # Modificar stock del producto
    producto.stock_actual -= payload.cantidad

    # Crear el registro de repuesto usado
    nuevo_repuesto = UsedPart(
        orden_id=orden_id,
        producto_id=payload.producto_id,
        cantidad=payload.cantidad,
        precio_venta=payload.precio_venta
    )
    db.add(nuevo_repuesto)

    # Crear movimiento de inventario (salida)
    movimiento = MovimientoInventario(
        producto_id=payload.producto_id,
        tipo="salida",
        cantidad=payload.cantidad,
        valor_unitario=payload.precio_venta,
        motivo=f"Repuesto usado en Orden #{orden.numero_orden or orden_id}",
        orden_id=orden_id
    )
    db.add(movimiento)

    db.commit()
    db.refresh(nuevo_repuesto)

    return nuevo_repuesto

# eliminar repuesto de una orden
@router.delete("/{orden_id}/repuestos/{repuesto_id}")
def eliminar_repuesto(
    orden_id: int,
    repuesto_id: int,
    db: Session = Depends(get_db)
):
    repuesto = db.query(UsedPart).filter(
        UsedPart.id == repuesto_id,
        UsedPart.orden_id == orden_id
    ).first()
    if not repuesto:
        raise HTTPException(
            status_code=404,
            detail="Repuesto no encontrado en esta orden"
        )

    producto = db.query(Producto).filter(Producto.id == repuesto.producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    # Devolver stock
    producto.stock_actual += repuesto.cantidad

    # Crear movimiento de inventario (entrada por devolucion)
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    movimiento = MovimientoInventario(
        producto_id=repuesto.producto_id,
        tipo="entrada",
        cantidad=repuesto.cantidad,
        valor_unitario=repuesto.precio_venta,
        motivo=f"Devolución de repuesto de Orden #{orden.numero_orden if orden else orden_id}",
        orden_id=orden_id
    )
    db.add(movimiento)

    db.delete(repuesto)
    db.commit()

    return {
        "message": "Repuesto eliminado e inventario actualizado"
    }