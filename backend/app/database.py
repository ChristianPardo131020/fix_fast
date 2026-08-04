from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

# cargar .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# url postgres
DATABASE_URL = os.getenv("DATABASE_URL")

# engine conexión
engine = create_engine(DATABASE_URL)

# sesiones DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base modelos
Base = declarative_base()