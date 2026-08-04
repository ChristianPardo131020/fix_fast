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

from app.database import Base

class MovimientoCaja(Base):
    __tablename__ = "movimientos_caja"

    id = Column(Integer, primary_key=True, index=True)

    tipo = Column(String(20), nullable=False)

    categoria = Column(String(100))

    valor = Column(
        Numeric(12, 2),
        nullable=False
    )

    metodo_pago = Column(String(50))

    descripcion = Column(Text)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id")
    )

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )