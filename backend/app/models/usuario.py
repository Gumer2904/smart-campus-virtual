"""
Modelo Usuario - base para todos los usuarios del sistema.
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class RolUsuario(str, PyEnum):
    """Roles disponibles en el sistema."""
    ADMINISTRADOR = "administrador"
    RECTOR = "rector"
    VICERRECTOR = "vicerrector"
    SECRETARIO = "secretario"
    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"
    PADRE = "padre"


class Usuario(Base):
    """
    Tabla de usuarios del sistema.
    Estudiante y Docente heredan de esta tabla (joined inheritance).
    """
    __tablename__ = "usuarios"

    # ===== Campos principales =====
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(150), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ===== Rol y estado =====
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario, name="rol_usuario", native_enum=True),
        nullable=False,
        default=RolUsuario.ESTUDIANTE,
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ===== Auditoría =====
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ===== Relaciones (joined inheritance) =====
    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante", back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    docente: Mapped["Docente"] = relationship(
        "Docente", back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, email='{self.email}', rol='{self.rol.value}')>"