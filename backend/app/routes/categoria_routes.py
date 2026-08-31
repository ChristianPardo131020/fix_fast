from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.categoria import Categoria
from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse
)
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/categorias",
    tags=["Categorías"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=List[CategoriaResponse])
def listar_categorias(tipo: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Categoria)
    if tipo:
        query = query.filter(Categoria.tipo == tipo)
    return query.all()

@router.post("/", response_model=CategoriaResponse)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    if categoria.tipo not in ["ingreso", "egreso"]:
        raise HTTPException(status_code=400, detail="El tipo debe ser 'ingreso' o 'egreso'")

    # Verificar si ya existe una con el mismo nombre y tipo
    existente = db.query(Categoria).filter(
        Categoria.nombre == categoria.nombre.strip().lower(),
        Categoria.tipo == categoria.tipo
    ).first()

    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre para este tipo")

    nueva = Categoria(
        nombre=categoria.nombre.strip().lower(),
        tipo=categoria.tipo
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.delete("/{categoria_id}")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    db.delete(categoria)
    db.commit()
    return {"message": "Categoría eliminada correctamente"}
