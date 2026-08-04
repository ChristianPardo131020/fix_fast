from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.movimiento_caja import (
    MovimientoCaja
)

from app.schemas.movimiento_caja_schema import (
    MovimientoCajaCreate,
    MovimientoCajaResponse
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/movimientos-caja",
    tags=["Movimientos Caja"],
    dependencies=[Depends(get_current_user)]
)

# crear movimiento
@router.post("/",
             response_model=MovimientoCajaResponse)

def crear_movimiento(
    movimiento: MovimientoCajaCreate,
    db: Session = Depends(get_db)
):

    nuevo_movimiento = MovimientoCaja(
        **movimiento.dict()
    )

    db.add(nuevo_movimiento)

    db.commit()

    db.refresh(nuevo_movimiento)

    return nuevo_movimiento

# listar movimientos
@router.get("/",
            response_model=list[
                MovimientoCajaResponse
            ])

def listar_movimientos(
    db: Session = Depends(get_db)
):

    return db.query(
        MovimientoCaja
    ).order_by(
        MovimientoCaja.created_at.desc()
    ).all()

# obtener movimiento
@router.get("/{movimiento_id}",
            response_model=
            MovimientoCajaResponse)

def obtener_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db)
):

    movimiento = db.query(
        MovimientoCaja
    ).filter(
        MovimientoCaja.id == movimiento_id
    ).first()

    if not movimiento:

        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado"
        )

    return movimiento

# eliminar movimiento
@router.delete("/{movimiento_id}")

def eliminar_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db)
):

    movimiento = db.query(
        MovimientoCaja
    ).filter(
        MovimientoCaja.id == movimiento_id
    ).first()

    if not movimiento:

        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado"
        )

    db.delete(movimiento)

    db.commit()

    return {
        "message": "Movimiento eliminado"
    }