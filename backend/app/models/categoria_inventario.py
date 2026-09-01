from sqlalchemy import Column, Integer, String, TIMESTAMP, text
from app.database import Base

class CategoriaInventario(Base):
    __tablename__ = "categorias_inventario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
