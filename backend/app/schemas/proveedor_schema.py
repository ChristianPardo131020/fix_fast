from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProveedorBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    email: Optional[str] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorResponse(ProveedorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
