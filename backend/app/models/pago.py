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

class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)

    orden_id = Column(
        Integer,
        ForeignKey("ordenes.id"),
        nullable=False
    )

    valor = Column(
        Numeric(12, 2),
        nullable=False
    )

    metodo_pago = Column(String(50))

    referencia_pago = Column(String(100))

    observaciones = Column(Text)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )