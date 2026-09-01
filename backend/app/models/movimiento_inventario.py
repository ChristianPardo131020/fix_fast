from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base

class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(20), nullable=False) # 'entrada', 'salida', 'ajuste', 'merma'
    cantidad = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    motivo = Column(String(255), nullable=True)
    orden_id = Column(Integer, ForeignKey("ordenes.id"), nullable=True) # Si es por reparación
    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    producto = relationship("Producto", lazy="joined")
