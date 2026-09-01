from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo_sku: Optional[str] = None
    precio_compra: float
    precio_venta: float
    stock_actual: int
    stock_minimo: int
    categoria_id: int
    proveedor_id: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
