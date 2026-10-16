"""
Schemas de Pydantic para Estudiante.
"""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.usuario import UsuarioCreate, UsuarioResponse


# ===== Base =====
class EstudianteBase(BaseModel):
    """Campos comunes del estudiante."""
    expediente: str = Field(..., min_length=1, max_length=20)
    cedula: str | None = Field(None, max_length=20)
    fecha_nacimiento: date | None = None
    carrera: str | None = Field(None, max_length=150)
    facultad: str | None = Field(None, max_length=150)
    año_ingreso: int | None = Field(None, ge=1900, le=2100)


# ===== Crear =====
class EstudianteCreate(EstudianteBase):
    """Schema para crear un estudiante (incluye datos de Usuario)."""
    usuario: UsuarioCreate


# ===== Actualizar =====
class EstudianteUpdate(BaseModel):
    """Schema para actualizar un estudiante."""
    cedula: str | None = Field(None, max_length=20)
    fecha_nacimiento: date | None = None
    carrera: str | None = Field(None, max_length=150)
    facultad: str | None = Field(None, max_length=150)
    año_ingreso: int | None = Field(None, ge=1900, le=2100)


# ===== Respuesta =====
class EstudianteResponse(EstudianteBase):
    """Schema para devolver un estudiante (incluye datos de Usuario)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario: UsuarioResponse