from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class OrdenBase(BaseModel):
    cliente_id: int

    numero_orden: Optional[str] = None

    equipo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None

    problema: Optional[str] = None
    diagnostico: Optional[str] = None

    estado: Optional[str] = "recibido"

    valor: Optional[Decimal] = 0
    saldo: Optional[Decimal] = 0

    tecnico_id: Optional[int] = None

class OrdenCreate(OrdenBase):
    fecha_ingreso: Optional[datetime] = None

class OrdenResponse(OrdenBase):
    id: int
    fecha_ingreso: datetime

    class Config:
        from_attributes = True