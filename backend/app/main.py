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
app = FastAPI()

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

@app.get("/")
def home():
    return {
        "message": "FixFast API funcionando 🚀"
    }
