"""
Smart Campus Virtual - API principal
TFG - Universidad Nacional de Guinea Ecuatorial (UNGE)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base


# ==========================================
# Ciclo de vida de la aplicación
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al arrancar y apagar la app.
    Al arrancar: crea las tablas (temporal, luego usaremos Alembic).
    """
    print("🚀 Iniciando Smart Campus Virtual API...")
    # Importar modelos para que SQLAlchemy los registre
    from app import models  # noqa: F401
    # Crear tablas (en desarrollo; en producción usar Alembic)
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos lista")
    yield
    print("🛑 Apagando Smart Campus Virtual API...")


# ==========================================
# Crear la aplicación FastAPI
# ==========================================
app = FastAPI(
    title=settings.APP_NAME,
    description="API del TFG Smart Campus Virtual - UNGE",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ==========================================
# Middleware CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Endpoints básicos
# ==========================================
@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raíz de bienvenida."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check para verificar que la API está viva."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


# ==========================================
# Routers (se irán añadiendo por módulo)
# ==========================================
# from app.api.v1 import auth, estudiantes, docentes
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
# app.include_router(estudiantes.router, prefix="/api/v1/estudiantes", tags=["Estudiantes"])
# app.include_router(docentes.router, prefix="/api/v1/docentes", tags=["Docentes"])