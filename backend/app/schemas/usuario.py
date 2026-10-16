"""
Schemas de Pydantic para Usuario.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.usuario import RolUsuario


# ===== Base =====
class UsuarioBase(BaseModel):
    """Campos comunes a todos los schemas de Usuario."""
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: str = Field(..., min_length=1, max_length=100)
    apellidos: str = Field(..., min_length=1, max_length=150)
    telefono: str | None = Field(None, max_length=20)
    rol: RolUsuario = RolUsuario.ESTUDIANTE


# ===== Crear =====
class UsuarioCreate(UsuarioBase):
    """Schema para crear un usuario (incluye password en texto plano)."""
    password: str = Field(..., min_length=8, max_length=100)


# ===== Actualizar =====
class UsuarioUpdate(BaseModel):
    """Schema para actualizar un usuario (todos los campos opcionales)."""
    email: EmailStr | None = None
    nombre: str | None = Field(None, min_length=1, max_length=100)
    apellidos: str | None = Field(None, min_length=1, max_length=150)
    telefono: str | None = Field(None, max_length=20)
    rol: RolUsuario | None = None
    activo: bool | None = None
    password: str | None = Field(None, min_length=8, max_length=100)


# ===== Respuesta =====
class UsuarioResponse(UsuarioBase):
    """Schema para devolver un usuario (sin password_hash)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    ultimo_acceso: datetime | None = None