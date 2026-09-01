from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.producto import Producto
from app.models.categoria_inventario import CategoriaInventario
from app.models.proveedor import Proveedor
from app.models.movimiento_inventario import MovimientoInventario
from app.models.movimiento_caja import MovimientoCaja
from app.models.orden import Orden

from app.schemas.producto_schema import ProductoCreate, ProductoResponse
from app.schemas.categoria_inventario_schema import CategoriaInventarioCreate, CategoriaInventarioResponse
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorResponse
from app.schemas.movimiento_inventario_schema import MovimientoInventarioCreate, MovimientoInventarioResponse


# --- Schemas para operaciones integradas ---

class CompraInventarioCreate(BaseModel):
    """Compra de producto: entrada en Kardex + egreso en caja."""
    producto_id: int
    cantidad: int
    valor_unitario: float
    metodo_pago: str = "Efectivo"
    descripcion: Optional[str] = None

class VentaMostradorCreate(BaseModel):
    """Venta de mostrador: salida en Kardex + ingreso en caja."""
    producto_id: int
    cantidad: int
    precio_venta: float
    metodo_pago: str = "Efectivo"
    descripcion: Optional[str] = None

router = APIRouter(
    prefix="/inventario",
    tags=["Inventario"],
    dependencies=[Depends(get_current_user)]
)

# -- Categorías Inventario --
@router.post("/categorias", response_model=CategoriaInventarioResponse)
def crear_categoria_inventario(categoria: CategoriaInventarioCreate, db: Session = Depends(get_db)):
    nueva = CategoriaInventario(**categoria.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/categorias", response_model=List[CategoriaInventarioResponse])
def listar_categorias_inventario(db: Session = Depends(get_db)):
    return db.query(CategoriaInventario).order_by(CategoriaInventario.nombre).all()

# -- Proveedores --
@router.post("/proveedores", response_model=ProveedorResponse)
def crear_proveedor(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    nuevo = Proveedor(**proveedor.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/proveedores", response_model=List[ProveedorResponse])
def listar_proveedores(db: Session = Depends(get_db)):
    return db.query(Proveedor).order_by(Proveedor.nombre).all()

# -- Productos --
def _generar_sku(db: Session) -> str:
    """Genera un SKU secuencial tipo PROD-0001."""
    ultimo = (
        db.query(func.max(Producto.id)).scalar() or 0
    )
    return f"PROD-{ultimo + 1:04d}"

@router.post("/productos", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    datos = producto.dict()
    sku = (datos.get("codigo_sku") or "").strip()
    if not sku:
        datos["codigo_sku"] = _generar_sku(db)
    else:
        datos["codigo_sku"] = sku
    nuevo = Producto(**datos)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/productos", response_model=List[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    return db.query(Producto).order_by(Producto.nombre).all()

@router.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, datos: ProductoCreate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for key, value in datos.dict().items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Verificar si tiene movimientos
    tiene_movimientos = db.query(MovimientoInventario).filter(MovimientoInventario.producto_id == producto_id).first()
    if tiene_movimientos:
        raise HTTPException(status_code=400, detail="No se puede eliminar: el producto tiene movimientos de stock registrados.")

    db.delete(producto)
    db.commit()
    return {"message": "Producto eliminado"}

# -- Movimientos Inventario (Kardex) --
@router.post("/movimientos", response_model=MovimientoInventarioResponse)
def registrar_movimiento(movimiento: MovimientoInventarioCreate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == movimiento.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Validar stock para salidas
    if movimiento.tipo == 'salida' and producto.stock_actual < movimiento.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    # Validar que si es por orden, la orden exista
    if movimiento.orden_id:
        orden = db.query(Orden).filter(Orden.id == movimiento.orden_id).first()
        if not orden:
             raise HTTPException(status_code=404, detail="Orden no encontrada")

    # Actualizar stock
    if movimiento.tipo == 'entrada':
        producto.stock_actual += movimiento.cantidad
    elif movimiento.tipo in ['salida', 'merma']:
        producto.stock_actual -= movimiento.cantidad
    elif movimiento.tipo == 'ajuste':
        producto.stock_actual += movimiento.cantidad

    nuevo_movimiento = MovimientoInventario(**movimiento.dict())
    db.add(nuevo_movimiento)
    db.commit()
    db.refresh(nuevo_movimiento)
    db.refresh(producto)
    return nuevo_movimiento

@router.get("/movimientos", response_model=List[MovimientoInventarioResponse])
def listar_movimientos(producto_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MovimientoInventario)
    if producto_id:
        query = query.filter(MovimientoInventario.producto_id == producto_id)
    return query.order_by(MovimientoInventario.created_at.desc()).all()

@router.get("/productos/bajo_stock", response_model=List[ProductoResponse])
def listar_bajo_stock(db: Session = Depends(get_db)):
    return db.query(Producto).filter(Producto.stock_actual <= Producto.stock_minimo).all()


# ---------------------------------------------------------------
# Operaciones integradas: Inventario + Kardex + Finanzas (atómicas)
# ---------------------------------------------------------------

@router.post("/compras")
def registrar_compra(compra: CompraInventarioCreate, db: Session = Depends(get_db)):
    """
    Compra de producto (ej. compra de repuestos a proveedor).
    En una sola transacción:
      1. Aumenta stock del producto
      2. Crea movimiento de inventario tipo 'entrada' (Kardex)
      3. Crea movimiento de caja tipo 'egreso' (finanzas)
    """
    producto = db.query(Producto).filter(Producto.id == compra.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    total = compra.cantidad * compra.valor_unitario

    # 1. Aumentar stock
    producto.stock_actual += compra.cantidad

    # 2. Kardex — entrada
    mov_inventario = MovimientoInventario(
        producto_id=compra.producto_id,
        tipo="entrada",
        cantidad=compra.cantidad,
        valor_unitario=compra.valor_unitario,
        motivo=compra.descripcion or f"Compra de {producto.nombre}",
    )
    db.add(mov_inventario)

    # 3. Caja — egreso
    mov_caja = MovimientoCaja(
        tipo="egreso",
        categoria="compra_inventario",
        valor=total,
        metodo_pago=compra.metodo_pago,
        descripcion=f"Compra: {producto.nombre} x{compra.cantidad} @ ${compra.valor_unitario:.0f}",
    )
    db.add(mov_caja)

    db.commit()
    db.refresh(producto)

    return {
        "message": "Compra registrada",
        "producto": producto.nombre,
        "stock_actual": producto.stock_actual,
        "total_egreso": total,
    }


@router.post("/ventas")
def registrar_venta(venta: VentaMostradorCreate, db: Session = Depends(get_db)):
    """
    Venta de mostrador (producto sin orden de reparación).
    En una sola transacción:
      1. Valida y descuenta stock
      2. Crea movimiento de inventario tipo 'salida' (Kardex)
      3. Crea movimiento de caja tipo 'ingreso' (finanzas)
    """
    producto = db.query(Producto).filter(Producto.id == venta.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if producto.stock_actual < venta.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    total = venta.cantidad * venta.precio_venta

    # 1. Descontar stock
    producto.stock_actual -= venta.cantidad

    # 2. Kardex — salida
    mov_inventario = MovimientoInventario(
        producto_id=venta.producto_id,
        tipo="salida",
        cantidad=venta.cantidad,
        valor_unitario=venta.precio_venta,
        motivo=venta.descripcion or f"Venta mostrador: {producto.nombre}",
    )
    db.add(mov_inventario)

    # 3. Caja — ingreso
    mov_caja = MovimientoCaja(
        tipo="ingreso",
        categoria="venta_producto",
        valor=total,
        metodo_pago=venta.metodo_pago,
        descripcion=f"Venta: {producto.nombre} x{venta.cantidad} @ ${venta.precio_venta:.0f}",
    )
    db.add(mov_caja)

    db.commit()
    db.refresh(producto)

    return {
        "message": "Venta registrada",
        "producto": producto.nombre,
        "stock_actual": producto.stock_actual,
        "total_ingreso": total,
    }
