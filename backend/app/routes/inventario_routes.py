from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.producto import Producto
from app.models.categoria_inventario import CategoriaInventario
from app.models.proveedor import Proveedor
from app.models.movimiento_inventario import MovimientoInventario
from app.models.orden import Orden

from app.schemas.producto_schema import ProductoCreate, ProductoResponse
from app.schemas.categoria_inventario_schema import CategoriaInventarioCreate, CategoriaInventarioResponse
from app.schemas.proveedor_schema import ProveedorCreate, ProveedorResponse
from app.schemas.movimiento_inventario_schema import MovimientoInventarioCreate, MovimientoInventarioResponse

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
    if not datos.get("codigo_sku"):
        datos["codigo_sku"] = _generar_sku(db)
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
