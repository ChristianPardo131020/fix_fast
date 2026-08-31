from sqlalchemy.orm import Session
from app.models.categoria import Categoria

def seed_categorias(db: Session):
    CATEGORIAS_INICIALES = [
        # Ingresos
        ("venta", "ingreso"),
        ("accesorio", "ingreso"),
        ("pila", "ingreso"),
        ("servicio_rapido", "ingreso"),
        ("otros_ingreso", "ingreso"),
        # Egresos
        ("arriendo", "egreso"),
        ("empleado", "egreso"),
        ("servicios", "egreso"),
        ("herramientas", "egreso"),
        ("transporte", "egreso"),
        ("compra", "egreso"),
        ("prestamo", "egreso"),
        ("otros_egreso", "egreso"),
    ]

    existentes = db.query(Categoria.nombre).all()
    existentes_set = set(nombre for (nombre,) in existentes)

    for nombre, tipo in CATEGORIAS_INICIALES:
        if nombre not in existentes_set:
            db.add(Categoria(nombre=nombre, tipo=tipo))

    db.commit()
