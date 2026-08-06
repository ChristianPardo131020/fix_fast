from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cliente import Cliente
from app.schemas.cliente_schema import (
    ClienteCreate,
    ClienteResponse
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)]
)

# crear cliente
@router.post("/", response_model=ClienteResponse)

def crear_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db)
):
    nuevo_cliente = Cliente(**cliente.dict())

    db.add(nuevo_cliente)

    db.commit()

    db.refresh(nuevo_cliente)

    return nuevo_cliente

# listar clientes
@router.get("/", response_model=list[ClienteResponse])

def listar_clientes(
    db: Session = Depends(get_db)
):
    return db.query(Cliente).all()

# obtener cliente por id
@router.get("/{cliente_id}",
            response_model=ClienteResponse)

def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    return cliente

# actualizar cliente
@router.put("/{cliente_id}",
            response_model=ClienteResponse)

def actualizar_cliente(
    cliente_id: int,
    datos: ClienteCreate,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    for key, value in datos.dict().items():
        setattr(cliente, key, value)

    db.commit()

    db.refresh(cliente)

    return cliente

# eliminar cliente
@router.delete("/{cliente_id}")

def eliminar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).first()

    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="Cliente no encontrado"
        )

    db.delete(cliente)

    db.commit()

    return {
        "message": "Cliente eliminado"
    }