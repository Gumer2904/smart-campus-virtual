"""
Modelo Asignatura.
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class Asignatura(Base):
    """
    Asignatura del plan de estudios.
    """
    __tablename__ = "asignaturas"

    # ===== Campos principales =====
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ===== Información académica =====
    creditos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    semestre: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # 1-10
    carrera: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    facultad: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # ===== Prerrequisitos (referencia simple por código) =====
    prerrequisitos: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Códigos de asignaturas prerrequisito (separados por coma)"
    )

    # ===== Estado =====
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    def __repr__(self) -> str:
        return f"<Asignatura(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"