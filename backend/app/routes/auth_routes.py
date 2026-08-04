from fastapi import APIRouter, Depends

from app.models.usuario import Usuario
from app.schemas.auth_schema import UsuarioMeResponse
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# El login/logout/signup ahora los maneja Supabase Auth directamente desde
# el frontend (supabase-js). Este endpoint solo expone el perfil de
# negocio del usuario ya autenticado.
@router.get("/me", response_model=UsuarioMeResponse)

def obtener_perfil(
    usuario: Usuario = Depends(get_current_user)
):
    return usuario
