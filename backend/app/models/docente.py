"""
Modelo Docente - hereda de Usuario.
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Docente(Base):
    """
    Datos específicos del docente.
    Hereda de Usuario mediante joined inheritance (FK a usuarios.id).
    """
    __tablename__ = "docentes"

    # ===== Clave primaria y foránea =====
    id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )

    # ===== Información profesional =====
    codigo_empleado: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    departamento: Mapped[str | None] = mapped_column(String(150), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(100), nullable=True)
    especialidad: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # ===== Relación con Usuario =====
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="docente")

    def __repr__(self) -> str:
        return f"<Docente(id={self.id}, codigo='{self.codigo_empleado}')>"