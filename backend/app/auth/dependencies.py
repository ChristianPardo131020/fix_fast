import json
import os
import time
import urllib.request

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario

SUPABASE_URL = os.getenv("SUPABASE_URL")
JWKS_URL = (
    f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    if SUPABASE_URL else None
)
JWKS_TTL_SECONDS = 3600

bearer_scheme = HTTPBearer()

# Proyectos nuevos de Supabase firman los JWT con claves asimétricas
# (ES256) en vez de un secreto compartido HS256, así que verificamos
# contra el JWKS público del proyecto en vez de un SUPABASE_JWT_SECRET
# estático. Se cachea en memoria para no pegarle a Supabase en cada
# request.
_jwks_cache = {"keys": [], "fetched_at": 0.0}

def _fetch_jwks():
    with urllib.request.urlopen(JWKS_URL, timeout=5) as response:
        data = json.loads(response.read())

    _jwks_cache["keys"] = data.get("keys", [])
    _jwks_cache["fetched_at"] = time.time()

def _find_signing_key(kid: str):
    if not _jwks_cache["keys"] or (time.time() - _jwks_cache["fetched_at"]) > JWKS_TTL_SECONDS:
        _fetch_jwks()

    for key in _jwks_cache["keys"]:
        if key.get("kid") == kid:
            return key

    # kid no encontrado: puede ser rotación de claves, forzamos un refresh
    # antes de rendirnos.
    _fetch_jwks()

    for key in _jwks_cache["keys"]:
        if key.get("kid") == kid:
            return key

    return None

# valida el JWT que emite Supabase Auth y resuelve el perfil de negocio
# en la tabla usuarios.
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> Usuario:

    if not JWKS_URL:
        raise RuntimeError(
            "SUPABASE_URL no está definida. Completá backend/.env con la "
            "Project URL de Supabase (Settings → API)."
        )

    token = credentials.credentials

    try:
        header = jwt.get_unverified_header(token)
        signing_key = _find_signing_key(header.get("kid"))

        if not signing_key:
            raise JWTError("Clave de firma desconocida")

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[signing_key.get("alg", "ES256")],
            audience="authenticated"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return usuario
