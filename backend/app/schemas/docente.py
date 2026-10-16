"""
Schemas de Pydantic para Docente.
"""
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.usuario import UsuarioCreate, UsuarioResponse


# ===== Base =====
class DocenteBase(BaseModel):
    """Campos comunes del docente."""
    codigo_empleado: str = Field(..., min_length=1, max_length=20)
    departamento: str | None = Field(None, max_length=150)
    categoria: str | None = Field(None, max_length=100)
    especialidad: str | None = Field(None, max_length=150)


# ===== Crear =====
class DocenteCreate(DocenteBase):
    """Schema para crear un docente (incluye datos de Usuario)."""
    usuario: UsuarioCreate


# ===== Actualizar =====
class DocenteUpdate(BaseModel):
    """Schema para actualizar un docente."""
    departamento: str | None = Field(None, max_length=150)
    categoria: str | None = Field(None, max_length=100)
    especialidad: str | None = Field(None, max_length=150)


# ===== Respuesta =====
class DocenteResponse(DocenteBase):
    """Schema para devolver un docente (incluye datos de Usuario)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario: UsuarioResponse