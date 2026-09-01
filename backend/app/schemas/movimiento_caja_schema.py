from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class MovimientoCajaBase(BaseModel):

    tipo: str

    categoria: Optional[str] = None

    valor: Decimal

    metodo_pago: Optional[str] = None

    descripcion: Optional[str] = None

    # La columna es UUID(as_uuid=True) con FK a usuarios.id — debe coincidir
    # con el tipo real de la DB para que la serialización de Pydantic v2 no
    # falle al listar filas que tengan un valor no nulo.
    usuario_id: Optional[UUID] = None

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