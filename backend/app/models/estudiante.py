"""
Modelo Estudiante - hereda de Usuario.
"""
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Estudiante(Base):
    """
    Datos específicos del estudiante.
    Hereda de Usuario mediante joined inheritance (FK a usuarios.id).
    """
    __tablename__ = "estudiantes"

    # ===== Clave primaria y foránea =====
    id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )

    # ===== Identificación académica =====
    expediente: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    cedula: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ===== Información académica =====
    carrera: Mapped[str | None] = mapped_column(String(150), nullable=True)
    facultad: Mapped[str | None] = mapped_column(String(150), nullable=True)
    año_ingreso: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ===== Relación con Usuario =====
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="estudiante")

    def __repr__(self) -> str:
        return f"<Estudiante(id={self.id}, expediente='{self.expediente}')>"