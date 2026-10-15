"""Sesión y motor de base de datos."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Motor de base de datos
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexión antes de usarla
    echo=settings.DEBUG,  # Muestra SQL en consola (útil en desarrollo)
)

# Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Dependencia FastAPI: proporciona una sesión de BD
    y la cierra al terminar la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()