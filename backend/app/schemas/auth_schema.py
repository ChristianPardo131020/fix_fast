from typing import Union
from uuid import UUID

from pydantic import BaseModel

class UsuarioMeResponse(BaseModel):
    id: Union[UUID, int, str]
    nombre: str
    email: str
    rol: str
    activo: bool

    class Config:
        from_attributes = True
