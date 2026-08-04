from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.usuario import Usuario

from app.schemas.auth_schema import (
    LoginRequest,
    TokenResponse
)

from app.auth.auth import (
    verify_password,
    create_access_token,
    hash_password
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# db
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# login
@router.post("/login",
             response_model=TokenResponse)

def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    usuario = db.query(Usuario).filter(
        Usuario.email == data.email
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    if not verify_password(
        data.password,
        usuario.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    token = create_access_token({
        "sub": str(usuario.id),
        "email": usuario.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# crear usuario prueba
@router.post("/crear-admin")

def crear_admin(
    db: Session = Depends(get_db)
):

    existe = db.query(Usuario).filter(
        Usuario.email == "admin@fixfast.com"
    ).first()

    if existe:
        return {
            "message": "Admin ya existe"
        }

    admin = Usuario(
        nombre="Administrador",
        email="admin@fixfast.com",
        password_hash=hash_password("123456"),
        rol="admin"
    )

    db.add(admin)

    db.commit()

    return {
        "message": "Admin creado",
        "email": "admin@fixfast.com",
        "password": "123456"
    }