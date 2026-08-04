from uuid import UUID

from pydantic import BaseModel

class UsuarioMeResponse(BaseModel):
    id: UUID
    nombre: str
    email: str
    rol: str
    activo: bool

    class Config:
        from_attributes = True
