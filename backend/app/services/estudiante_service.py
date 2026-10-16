"""
Servicios (lógica de negocio) para Estudiante.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.estudiante import Estudiante
from app.models.usuario import RolUsuario
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate
from app.services import usuario_service


def get_estudiante_by_id(db: Session, estudiante_id: int) -> Estudiante | None:
    """Obtiene un estudiante por su ID."""
    return db.get(Estudiante, estudiante_id)


def get_estudiante_by_expediente(db: Session, expediente: str) -> Estudiante | None:
    """Obtiene un estudiante por su número de expediente."""
    stmt = select(Estudiante).where(Estudiante.expediente == expediente)
    return db.execute(stmt).scalar_one_or_none()


def get_estudiantes(db: Session, skip: int = 0, limit: int = 100) -> list[Estudiante]:
    """Obtiene lista de estudiantes con paginación."""
    stmt = select(Estudiante).offset(skip).limit(limit).order_by(Estudiante.id)
    return list(db.execute(stmt).scalars().all())


def create_estudiante(db: Session, data: EstudianteCreate) -> Estudiante:
    """Crea un estudiante nuevo (también crea su Usuario asociado)."""
    # 1. Crear el Usuario base
    usuario_data = data.usuario.model_copy(update={"rol": RolUsuario.ESTUDIANTE})
    usuario = usuario_service.create_usuario(db, usuario_data)

    # 2. Crear el Estudiante asociado
    estudiante = Estudiante(
        id=usuario.id,
        expediente=data.expediente,
        cedula=data.cedula,
        fecha_nacimiento=data.fecha_nacimiento,
        carrera=data.carrera,
        facultad=data.facultad,
        año_ingreso=data.año_ingreso,
    )
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


def update_estudiante(
    db: Session, estudiante: Estudiante, data: EstudianteUpdate
) -> Estudiante:
    """Actualiza un estudiante existente."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(estudiante, field, value)
    db.commit()
    db.refresh(estudiante)
    return estudiante


def delete_estudiante(db: Session, estudiante: Estudiante) -> None:
    """Elimina un estudiante (y su Usuario asociado por CASCADE)."""
    db.delete(estudiante)
    db.commit()