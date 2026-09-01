from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MovimientoInventarioBase(BaseModel):
    producto_id: int
    tipo: str # entrada, salida, ajuste, merma
    cantidad: int
    valor_unitario: float
    motivo: Optional[str] = None
    orden_id: Optional[int] = None

class MovimientoInventarioCreate(MovimientoInventarioBase):
    pass

class ProductoMinimo(BaseModel):
    id: int
    nombre: str
    codigo_sku: Optional[str] = None

    class Config:
        from_attributes = True

class MovimientoInventarioResponse(MovimientoInventarioBase):
    id: int
    created_at: datetime
    producto: Optional[ProductoMinimo] = None

    class Config:
        from_attributes = True
