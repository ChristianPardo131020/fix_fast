from pydantic import BaseModel
from typing import Optional
from app.schemas.producto_schema import ProductoResponse

class UsedPartBase(BaseModel):
    producto_id: int
    cantidad: int
    precio_venta: float

class UsedPartCreate(UsedPartBase):
    pass

class UsedPartResponse(UsedPartBase):
    id: int
    orden_id: int
    producto: Optional[ProductoResponse] = None

    class Config:
        from_attributes = True
