"""
Servicios (lógica de negocio) para Asignatura.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.asignatura import Asignatura
from app.schemas.asignatura import (
    AsignaturaCreate,
    AsignaturaFiltros,
    AsignaturaUpdate,
)


def get_asignatura_by_id(db: Session, asignatura_id: int) -> Asignatura | None:
    """Obtiene una asignatura por ID."""
    return db.get(Asignatura, asignatura_id)


def get_asignatura_by_codigo(db: Session, codigo: str) -> Asignatura | None:
    """Obtiene una asignatura por código."""
    stmt = select(Asignatura).where(Asignatura.codigo == codigo)
    return db.execute(stmt).scalar_one_or_none()


def get_asignaturas(
    db: Session,
    filtros: AsignaturaFiltros,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Asignatura], int]:
    """
    Obtiene lista de asignaturas con filtros y paginación.
    
    Returns:
        Tupla (lista de asignaturas, total de resultados)
    """
    from sqlalchemy import func

    # Construir condiciones
    conditions = []

    if filtros.search:
        search_pattern = f"%{filtros.search}%"
        conditions.append(
            or_(
                Asignatura.codigo.ilike(search_pattern),
                Asignatura.nombre.ilike(search_pattern),
            )
        )

    if filtros.carrera:
        conditions.append(Asignatura.carrera == filtros.carrera)

    if filtros.facultad:
        conditions.append(Asignatura.facultad == filtros.facultad)

    if filtros.semestre is not None:
        conditions.append(Asignatura.semestre == filtros.semestre)

    if filtros.activa is not None:
        conditions.append(Asignatura.activa == filtros.activa)

    # Query base con filtros
    stmt = select(Asignatura)
    if conditions:
        stmt = stmt.where(*conditions)

    # Contar total (sin paginar)
    count_stmt = select(func.count()).select_from(Asignatura)
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = db.execute(count_stmt).scalar_one()

    # Ordenar y paginar
    stmt = stmt.order_by(Asignatura.semestre, Asignatura.codigo).offset(skip).limit(limit)
    asignaturas = list(db.execute(stmt).scalars().all())

    return asignaturas, total

def create_asignatura(db: Session, data: AsignaturaCreate) -> Asignatura:
    """Crea una asignatura nueva."""
    asignatura = Asignatura(**data.model_dump())
    db.add(asignatura)
    db.commit()
    db.refresh(asignatura)
    return asignatura


def update_asignatura(
    db: Session, asignatura: Asignatura, data: AsignaturaUpdate
) -> Asignatura:
    """Actualiza una asignatura existente."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asignatura, field, value)
    db.commit()
    db.refresh(asignatura)
    return asignatura


def delete_asignatura(db: Session, asignatura: Asignatura) -> None:
    """Elimina una asignatura."""
    db.delete(asignatura)
    db.commit()