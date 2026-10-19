"""
Modelo Matricula - relación entre Estudiante y Asignatura.
"""
from datetime import date, datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class EstadoMatricula(str, PyEnum):
    """Estados posibles de una matrícula."""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    ANULADA = "anulada"
    COMPLETADA = "completada"


class Matricula(Base):
    """
    Matrícula de un estudiante en una asignatura.
    
    Restricción: un estudiante no puede matricularse dos veces
    en la misma asignatura en el mismo período académico.
    """
    __tablename__ = "matriculas"
    __table_args__ = (
        UniqueConstraint(
            "estudiante_id", "asignatura_id", "periodo",
            name="uq_matricula_estudiante_asignatura_periodo",
        ),
    )

    # ===== Campos principales =====
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ===== Relaciones =====
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asignatura_id: Mapped[int] = mapped_column(
        ForeignKey("asignaturas.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # ===== Información académica =====
    periodo: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True,
        comment="Período académico, ej: 2026-1",
    )
    nota_final: Mapped[float | None] = mapped_column(nullable=True)
    aprobada: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    fecha_matricula: Mapped[date] = mapped_column(
        Date, server_default=func.current_date(), nullable=False
    )

    # ===== Estado =====
    estado: Mapped[EstadoMatricula] = mapped_column(
        Enum(EstadoMatricula, name="estado_matricula", native_enum=True),
        nullable=False,
        default=EstadoMatricula.PENDIENTE,
    )

    # ===== Observaciones =====
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    # ===== Relaciones ORM =====
    estudiante: Mapped["Estudiante"] = relationship(
        "Estudiante", back_populates="matriculas"
    )
    asignatura: Mapped["Asignatura"] = relationship(
        "Asignatura", back_populates="matriculas"
    )

    def __repr__(self) -> str:
        return (
            f"<Matricula(id={self.id}, estudiante_id={self.estudiante_id}, "
            f"asignatura_id={self.asignatura_id}, periodo='{self.periodo}')>"
        )