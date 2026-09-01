from pydantic import BaseModel
from datetime import datetime

class CategoriaInventarioBase(BaseModel):
    nombre: str

class CategoriaInventarioCreate(CategoriaInventarioBase):
    pass

class CategoriaInventarioResponse(CategoriaInventarioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
