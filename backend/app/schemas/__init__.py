"""
Schemas de Pydantic del sistema.
"""
from app.schemas.usuario import (
    UsuarioBase,
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
)
from app.schemas.estudiante import (
    EstudianteBase,
    EstudianteCreate,
    EstudianteUpdate,
    EstudianteResponse,
)
from app.schemas.docente import (
    DocenteBase,
    DocenteCreate,
    DocenteUpdate,
    DocenteResponse,
)

__all__ = [
    "UsuarioBase", "UsuarioCreate", "UsuarioUpdate", "UsuarioResponse",
    "EstudianteBase", "EstudianteCreate", "EstudianteUpdate", "EstudianteResponse",
    "DocenteBase", "DocenteCreate", "DocenteUpdate", "DocenteResponse",
]