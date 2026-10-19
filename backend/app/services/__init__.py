"""
Servicios del sistema.
"""
from app.services import (
    usuario_service,
    estudiante_service,
    docente_service,
    asignatura_service,
    matricula_service,
)

__all__ = [
    "usuario_service",
    "estudiante_service",
    "docente_service",
    "asignatura_service",
    "matricula_service",
]