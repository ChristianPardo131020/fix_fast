from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HistorialEstadoResponse(BaseModel):
    id: int
    orden_id: int
    estado_anterior: Optional[str] = None
    estado_nuevo: Optional[str] = None
    comentario: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
