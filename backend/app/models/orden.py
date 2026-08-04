from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    TIMESTAMP,
    ForeignKey,
    text
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=False
    )

    numero_orden = Column(String(30), unique=True)

    equipo = Column(String(100))
    marca = Column(String(100))
    modelo = Column(String(100))

    problema = Column(Text)
    diagnostico = Column(Text)

    estado = Column(String(50), default="recibido")

    valor = Column(Numeric(12, 2), default=0)

    saldo = Column(Numeric(12, 2), default=0)

    fecha_ingreso = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    fecha_entrega = Column(TIMESTAMP)

    tecnico_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id")
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )