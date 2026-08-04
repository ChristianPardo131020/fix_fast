from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class MovimientoCajaBase(BaseModel):

    tipo: str

    categoria: Optional[str] = None

    valor: Decimal

    metodo_pago: Optional[str] = None

    descripcion: Optional[str] = None

    usuario_id: Optional[int] = None

class MovimientoCajaCreate(
    MovimientoCajaBase
):
    pass

class MovimientoCajaResponse(
    MovimientoCajaBase
):
    id: int

    created_at: datetime

    class Config:
        from_attributes = True