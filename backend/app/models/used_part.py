from sqlalchemy import Column, Integer, ForeignKey, Float
from app.database import Base

class UsedPart(Base):
    __tablename__ = "used_parts"

    id = Column(Integer, primary_key=True, index=True)
    orden_id = Column(Integer, ForeignKey("ordenes.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_venta = Column(Float, nullable=False) # Precio al que se le vendió al cliente en esa orden
