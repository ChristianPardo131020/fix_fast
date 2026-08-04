from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class OrdenPublicaResponse(BaseModel):
    """
    Respuesta del seguimiento publico (sin autenticacion). A proposito
    expone menos campos que OrdenResponse: nada de diagnostico tecnico
    ni datos de contacto del cliente, solo lo que un cliente necesita
    para saber en que va su reparacion.
    """

    numero_orden: str
    equipo: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    estado: Optional[str] = None
    fecha_ingreso: datetime
    fecha_entrega: Optional[datetime] = None
    valor: Optional[Decimal] = 0
    saldo: Optional[Decimal] = 0
    cliente_nombre: str
