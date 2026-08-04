from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    text
)

from app.database import Base

class HistorialEstado(Base):
    __tablename__ = "historial_estados"

    id = Column(Integer, primary_key=True, index=True)

    orden_id = Column(
        Integer,
        ForeignKey("ordenes.id")
    )

    estado_anterior = Column(String(50))

    estado_nuevo = Column(String(50))

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id")
    )

    comentario = Column(Text)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )