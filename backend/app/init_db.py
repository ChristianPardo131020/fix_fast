from app.database import Base, engine
from app.database import SessionLocal

# importar modelos
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.models.orden import Orden
from app.models.pago import Pago
from app.models.movimiento_caja import MovimientoCaja
from app.models.historial_estado import HistorialEstado
from app.models.categoria import Categoria
from app.models.categoria_inventario import CategoriaInventario
from app.models.proveedor import Proveedor
from app.models.producto import Producto
from app.models.movimiento_inventario import MovimientoInventario
from app.models.used_part import UsedPart

print("Creando tablas...")

Base.metadata.create_all(bind=engine)

print("Tablas creadas correctamente 🚀")

print("Sembrando categorías iniciales...")
db = SessionLocal()
try:
    from app.seed_categorias import seed_categorias
    seed_categorias(db)
    print("Categorías listas.")
finally:
    db.close()