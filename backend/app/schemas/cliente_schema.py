from pydantic import BaseModel
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    observaciones: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True