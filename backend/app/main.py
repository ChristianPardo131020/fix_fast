from fastapi import FastAPI

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