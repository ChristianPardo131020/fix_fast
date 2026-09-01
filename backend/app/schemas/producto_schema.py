from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    codigo_sku: Optional[str] = None
    precio_compra: float = 0.0
    precio_venta: float = 0.0
    stock_actual: int = 0
    stock_minimo: int = 0
    categoria_id: int
    proveedor_id: Optional[int] = None

    @validator('precio_compra', 'precio_venta', 'stock_actual', 'stock_minimo', pre=True, always=True)
    def coerce_numbers(cls, v):
        try:
            if v is None or v == '':
                return 0
            return int(float(v))
        except ValueError:
            raise ValueError('Invalid numeric value')

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
