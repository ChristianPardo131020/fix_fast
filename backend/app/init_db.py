from app.database import Base, engine

# importar modelos
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.models.orden import Orden
from app.models.pago import Pago
from app.models.movimiento_caja import MovimientoCaja
from app.models.historial_estado import HistorialEstado

print("Creando tablas...")

Base.metadata.create_all(bind=engine)

print("Tablas creadas correctamente 🚀")