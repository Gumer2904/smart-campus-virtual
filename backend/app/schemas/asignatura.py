"""
Schemas de Pydantic para Asignatura.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ===== Base =====
class AsignaturaBase(BaseModel):
    """Campos comunes de una asignatura."""
    codigo: str = Field(..., min_length=1, max_length=20, description="Código único de la asignatura")
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: str | None = Field(None, description="Descripción opcional")
    creditos: int = Field(..., ge=0, le=20, description="Créditos ECTS")
    semestre: int = Field(..., ge=1, le=10, description="Semestre (1-10)")
    carrera: str | None = Field(None, max_length=150)
    facultad: str | None = Field(None, max_length=150)
    prerrequisitos: str | None = Field(None, description="Códigos separados por coma")
    activa: bool = True


# ===== Crear =====
class AsignaturaCreate(AsignaturaBase):
    """Schema para crear una asignatura."""
    pass


# ===== Actualizar =====
class AsignaturaUpdate(BaseModel):
    """Schema para actualizar (todos opcionales)."""
    codigo: str | None = Field(None, min_length=1, max_length=20)
    nombre: str | None = Field(None, min_length=1, max_length=200)
    descripcion: str | None = None
    creditos: int | None = Field(None, ge=0, le=20)
    semestre: int | None = Field(None, ge=1, le=10)
    carrera: str | None = Field(None, max_length=150)
    facultad: str | None = Field(None, max_length=150)
    prerrequisitos: str | None = None
    activa: bool | None = None


# ===== Respuesta =====
class AsignaturaResponse(AsignaturaBase):
    """Schema para devolver una asignatura."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# ===== Filtros de búsqueda =====
class AsignaturaFiltros(BaseModel):
    """Filtros para listar asignaturas."""
    search: str | None = Field(None, description="Buscar por código o nombre")
    carrera: str | None = None
    facultad: str | None = None
    semestre: int | None = Field(None, ge=1, le=10)
    activa: bool | None = None