import uuid

from sqlalchemy import Column, String, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # id espejo de auth.users.id (gestionado por Supabase Auth vía trigger,
    # ver backend/sql/supabase_trigger.sql) — ya no hay password_hash acá,
    # las credenciales viven en el esquema auth de Supabase.
    #
    # OJO: no se declara como ForeignKey de SQLAlchemy porque auth.users
    # vive en un esquema que Supabase gestiona (fuera de nuestro
    # Base.metadata) — create_all() no puede resolver esa referencia. La
    # constraint real se agrega por SQL directo en supabase_trigger.sql.
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    nombre = Column(String(100), nullable=False)

    email = Column(String(150), unique=True, nullable=False)

    rol = Column(String(50), default="empleado")

    activo = Column(Boolean, default=True)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
