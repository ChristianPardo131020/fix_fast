from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(...) # 'ingreso' o 'egreso'

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None)

class CategoriaResponse(CategoriaBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
