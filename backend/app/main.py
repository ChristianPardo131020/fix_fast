import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.cliente_routes import (
    router as cliente_router
)

from app.routes.orden_routes import (
    router as orden_router
)

from app.routes.pago_routes import (
    router as pago_router
)

from app.routes.dashboard_routes import (
    router as dashboard_router
)

from app.routes.auth_routes import (
    router as auth_router
)

from app.routes.movimiento_caja_routes import (
    router as movimiento_caja_router
)

from app.routes.categoria_routes import (
    router as categoria_router
)

from app.routes.public_routes import (
    router as public_router
)

from app.routes.inventario_routes import (
    router as inventario_router
)
app = FastAPI()


@app.on_event("startup")
def _auto_create_tables():
    """Crea tablas nuevas que aún no existan en Supabase (checkfirst=True
    por defecto).  Esto evita tener que correr init_db.py a mano cada vez
    que se agrega un modelo — el Dockerfile solo arranca uvicorn."""
    from app.database import Base, engine          # noqa: lazy import para no duplicar top-level
    # Importar todos los modelos para que Base.metadata los conozca
    import app.models.cliente           # noqa: F401
    import app.models.usuario           # noqa: F401
    import app.models.orden             # noqa: F401
    import app.models.pago              # noqa: F401
    import app.models.movimiento_caja   # noqa: F401
    import app.models.historial_estado  # noqa: F401
    import app.models.categoria         # noqa: F401
    import app.models.categoria_inventario  # noqa: F401
    import app.models.proveedor         # noqa: F401
    import app.models.producto          # noqa: F401
    import app.models.movimiento_inventario  # noqa: F401
    import app.models.used_part         # noqa: F401
    Base.metadata.create_all(bind=engine)

# CORS: orígenes permitidos vía env (csv), ej. "http://localhost:5173"
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cliente_router)
app.include_router(orden_router)
app.include_router(pago_router)
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(movimiento_caja_router)
app.include_router(categoria_router)
app.include_router(public_router)
app.include_router(inventario_router)

@app.get("/")
def home():
    return {
        "message": "FixFast API funcionando 🚀"
    }
