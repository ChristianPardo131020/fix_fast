from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class PagoBase(BaseModel):
    orden_id: int

    valor: Decimal

    metodo_pago: Optional[str] = None

    referencia_pago: Optional[str] = None

    observaciones: Optional[str] = None

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True