"""
Schemas de Pydantic para Matricula.
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.matricula import EstadoMatricula


# ===== Base =====
class MatriculaBase(BaseModel):
    """Campos comunes de una matrícula."""
    estudiante_id: int = Field(..., gt=0)
    asignatura_id: int = Field(..., gt=0)
    periodo: str = Field(..., min_length=4, max_length=20, description="Ej: 2026-1")
    estado: EstadoMatricula = EstadoMatricula.PENDIENTE
    observaciones: str | None = None


# ===== Crear =====
class MatriculaCreate(MatriculaBase):
    """Schema para crear una matrícula."""
    pass


# ===== Actualizar =====
class MatriculaUpdate(BaseModel):
    """Schema para actualizar una matrícula."""
    nota_final: float | None = Field(None, ge=0, le=5)
    aprobada: bool | None = None
    estado: EstadoMatricula | None = None
    observaciones: str | None = None


# ===== Respuesta básica =====
class MatriculaResponse(MatriculaBase):
    """Schema para devolver una matrícula."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nota_final: float | None = None
    aprobada: bool | None = None
    fecha_matricula: date
    fecha_creacion: datetime
    fecha_actualizacion: datetime


# ===== Filtros =====
class MatriculaFiltros(BaseModel):
    """Filtros para listar matrículas."""
    estudiante_id: int | None = None
    asignatura_id: int | None = None
    periodo: str | None = None
    estado: EstadoMatricula | None = None
    aprobada: bool | None = None