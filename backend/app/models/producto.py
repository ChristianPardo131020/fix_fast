from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship
from app.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(500), nullable=True)
    codigo_sku = Column(String(50), nullable=True, unique=True)
    precio_compra = Column(Float, nullable=False, default=0.0)
    precio_venta = Column(Float, nullable=False, default=0.0)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=0)
    categoria_id = Column(Integer, ForeignKey("categorias_inventario.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
