from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

# cargar .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# url postgres (Supabase: usar el connection string del Session Pooler,
# ver backend/.env.example)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no está definida. Copiá backend/.env.example a "
        "backend/.env y completá la connection string de Supabase."
    )

# engine conexión
# pool_pre_ping evita usar conexiones que Supabase ya cerró del lado del
# servidor; pool_recycle recicla conexiones viejas antes de que el pooler
# las tire.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800
)

# sesiones DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base modelos
Base = declarative_base()

# conexión db (dependency compartida por todos los routers)
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
