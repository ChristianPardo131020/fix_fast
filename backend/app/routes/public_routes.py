import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cliente import Cliente
from app.models.orden import Orden
from app.schemas.public_schema import OrdenPublicaResponse

# Sin dependencies=[Depends(get_current_user)] a proposito: este router
# lo consulta el cliente final desde /seguimiento, sin haber iniciado
# sesion. El login del panel administrativo (auth_routes.py) sigue
# siendo el unico camino para el equipo del taller.
router = APIRouter(
    prefix="/publico",
    tags=["Seguimiento publico"]
)

MENSAJE_NO_ENCONTRADA = "No encontramos una orden con esos datos. Revisa el numero de orden y el telefono."


def _solo_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def _telefonos_coinciden(telefono_cliente: str, telefono_ingresado: str) -> bool:
    a = _solo_digitos(telefono_cliente)
    b = _solo_digitos(telefono_ingresado)

    if not a or not b:
        return False

    # Comparamos los ultimos 7 digitos en vez de exigir coincidencia
    # exacta: tolera que el cliente escriba o no el indicativo del pais
    # (+57) sin abrir la puerta a una coincidencia parcial demasiado floja.
    if len(a) >= 7 and len(b) >= 7:
        return a[-7:] == b[-7:]

    return a == b


@router.get("/seguimiento", response_model=OrdenPublicaResponse)
def consultar_orden(
    codigo: str = Query(..., min_length=1, description="Numero de orden, ej. FF-000123"),
    telefono: str = Query(..., min_length=4),
    db: Session = Depends(get_db)
):
    codigo_normalizado = codigo.strip().upper()

    orden = db.query(Orden).filter(
        Orden.numero_orden == codigo_normalizado
    ).first()

    # Compatibilidad con ordenes viejas creadas antes de que existiera
    # el numero_orden amigable: si el codigo ingresado es solo digitos,
    # tambien se prueba como id crudo.
    if not orden and codigo_normalizado.isdigit():
        orden = db.query(Orden).filter(
            Orden.id == int(codigo_normalizado)
        ).first()

    if not orden:
        raise HTTPException(status_code=404, detail=MENSAJE_NO_ENCONTRADA)

    cliente = db.query(Cliente).filter(
        Cliente.id == orden.cliente_id
    ).first()

    if not cliente or not _telefonos_coinciden(cliente.telefono, telefono):
        # Mismo mensaje que "orden no encontrada": no distinguimos si
        # fallo el codigo o el telefono, para no facilitar que alguien
        # pruebe telefonos contra un codigo que ya sabe que es valido.
        raise HTTPException(status_code=404, detail=MENSAJE_NO_ENCONTRADA)

    return OrdenPublicaResponse(
        numero_orden=orden.numero_orden or f"FF-{orden.id:06d}",
        equipo=orden.equipo,
        marca=orden.marca,
        modelo=orden.modelo,
        estado=orden.estado,
        fecha_ingreso=orden.fecha_ingreso,
        fecha_entrega=orden.fecha_entrega,
        valor=orden.valor,
        saldo=orden.saldo,
        cliente_nombre=cliente.nombre,
    )
