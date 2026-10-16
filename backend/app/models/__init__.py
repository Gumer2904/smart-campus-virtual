"""
Importar todos los modelos para que SQLAlchemy y Alembic los detecten.
"""
from app.models.usuario import Usuario, RolUsuario
from app.models.estudiante import Estudiante
from app.models.docente import Docente
from app.models.asignatura import Asignatura

__all__ = [
    "Usuario",
    "RolUsuario",
    "Estudiante",
    "Docente",
    "Asignatura",
]