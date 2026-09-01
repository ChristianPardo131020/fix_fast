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

class MovimientoInventarioResponse(MovimientoInventarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
