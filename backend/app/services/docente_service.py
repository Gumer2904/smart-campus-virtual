"""
Servicios (lógica de negocio) para Docente.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.docente import Docente
from app.models.usuario import RolUsuario
from app.schemas.docente import DocenteCreate, DocenteUpdate
from app.services import usuario_service


def get_docente_by_id(db: Session, docente_id: int) -> Docente | None:
    """Obtiene un docente por su ID."""
    return db.get(Docente, docente_id)


def get_docente_by_codigo(db: Session, codigo: str) -> Docente | None:
    """Obtiene un docente por su código de empleado."""
    stmt = select(Docente).where(Docente.codigo_empleado == codigo)
    return db.execute(stmt).scalar_one_or_none()


def get_docentes(db: Session, skip: int = 0, limit: int = 100) -> list[Docente]:
    """Obtiene lista de docentes con paginación."""
    stmt = select(Docente).offset(skip).limit(limit).order_by(Docente.id)
    return list(db.execute(stmt).scalars().all())


def create_docente(db: Session, data: DocenteCreate) -> Docente:
    """Crea un docente nuevo (también crea su Usuario asociado)."""
    usuario_data = data.usuario.model_copy(update={"rol": RolUsuario.DOCENTE})
    usuario = usuario_service.create_usuario(db, usuario_data)

    docente = Docente(
        id=usuario.id,
        codigo_empleado=data.codigo_empleado,
        departamento=data.departamento,
        categoria=data.categoria,
        especialidad=data.especialidad,
    )
    db.add(docente)
    db.commit()
    db.refresh(docente)
    return docente


def update_docente(db: Session, docente: Docente, data: DocenteUpdate) -> Docente:
    """Actualiza un docente existente."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(docente, field, value)
    db.commit()
    db.refresh(docente)
    return docente


def delete_docente(db: Session, docente: Docente) -> None:
    """Elimina un docente (y su Usuario asociado por CASCADE)."""
    db.delete(docente)
    db.commit()