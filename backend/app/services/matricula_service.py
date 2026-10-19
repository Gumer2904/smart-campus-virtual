"""
Servicios (lógica de negocio) para Matricula.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.matricula import EstadoMatricula, Matricula
from app.schemas.matricula import (
    MatriculaCreate,
    MatriculaFiltros,
    MatriculaUpdate,
)


def get_matricula_by_id(db: Session, matricula_id: int) -> Matricula | None:
    """Obtiene una matrícula por ID (con relaciones cargadas)."""
    stmt = (
        select(Matricula)
        .options(
            joinedload(Matricula.estudiante).joinedload(Matricula.estudiante.property.mapper.class_.usuario),
            joinedload(Matricula.asignatura),
        )
        .where(Matricula.id == matricula_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_matriculas(
    db: Session,
    filtros: MatriculaFiltros,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Matricula], int]:
    """Lista matrículas con filtros y paginación."""
    conditions = []

    if filtros.estudiante_id is not None:
        conditions.append(Matricula.estudiante_id == filtros.estudiante_id)

    if filtros.asignatura_id is not None:
        conditions.append(Matricula.asignatura_id == filtros.asignatura_id)

    if filtros.periodo:
        conditions.append(Matricula.periodo == filtros.periodo)

    if filtros.estado is not None:
        conditions.append(Matricula.estado == filtros.estado)

    if filtros.aprobada is not None:
        conditions.append(Matricula.aprobada == filtros.aprobada)

    stmt = select(Matricula).options(
        joinedload(Matricula.estudiante),
        joinedload(Matricula.asignatura),
    )
    if conditions:
        stmt = stmt.where(*conditions)

    # Contar total
    count_stmt = select(func.count()).select_from(Matricula)
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = db.execute(count_stmt).scalar_one()

    # Ordenar y paginar
    stmt = stmt.order_by(Matricula.fecha_creacion.desc()).offset(skip).limit(limit)
    matriculas = list(db.execute(stmt).scalars().all())

    return matriculas, total


def get_matricula_existente(
    db: Session, estudiante_id: int, asignatura_id: int, periodo: str
) -> Matricula | None:
    """Verifica si ya existe una matrícula para ese estudiante/asignatura/período."""
    stmt = select(Matricula).where(
        Matricula.estudiante_id == estudiante_id,
        Matricula.asignatura_id == asignatura_id,
        Matricula.periodo == periodo,
    )
    return db.execute(stmt).scalar_one_or_none()


def create_matricula(db: Session, data: MatriculaCreate) -> Matricula:
    """Crea una matrícula nueva."""
    matricula = Matricula(**data.model_dump())
    db.add(matricula)
    db.commit()
    db.refresh(matricula)
    return matricula


def update_matricula(
    db: Session, matricula: Matricula, data: MatriculaUpdate
) -> Matricula:
    """Actualiza una matrícula existente."""
    update_data = data.model_dump(exclude_unset=True)

    # Si se asigna nota y no se especifica "aprobada", calcular automáticamente
    if "nota_final" in update_data and update_data["nota_final"] is not None:
        if "aprobada" not in update_data:
            update_data["aprobada"] = update_data["nota_final"] >= 3.0

    for field, value in update_data.items():
        setattr(matricula, field, value)

    db.commit()
    db.refresh(matricula)
    return matricula


def delete_matricula(db: Session, matricula: Matricula) -> None:
    """Elimina una matrícula."""
    db.delete(matricula)
    db.commit()