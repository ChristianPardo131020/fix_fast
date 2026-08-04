from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    rol = Column(String(50), default="empleado")

    activo = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )