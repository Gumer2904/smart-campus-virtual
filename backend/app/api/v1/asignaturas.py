"""
Endpoints CRUD para Asignatura con filtros y paginación.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.schemas.asignatura import (
    AsignaturaCreate,
    AsignaturaFiltros,
    AsignaturaResponse,
    AsignaturaUpdate,
)
from app.services import asignatura_service

router = APIRouter()


def _check_admin(current_user: Usuario):
    """Verifica permisos de admin/secretario."""
    if current_user.rol not in (RolUsuario.ADMINISTRADOR, RolUsuario.SECRETARIO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )


@router.get(
    "/",
    response_model=dict,
    summary="Listar asignaturas con filtros y paginación",
)
def list_asignaturas(
    search: str | None = Query(None, description="Buscar por código o nombre"),
    carrera: str | None = Query(None),
    facultad: str | None = Query(None),
    semestre: int | None = Query(None, ge=1, le=10),
    activa: bool | None = Query(None),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Lista asignaturas con filtros opcionales y paginación.
    
    Devuelve:
    - **items**: lista de asignaturas
    - **total**: total de registros que cumplen los filtros
    - **skip**, **limit**: paginación aplicada
    """
    filtros = AsignaturaFiltros(
        search=search,
        carrera=carrera,
        facultad=facultad,
        semestre=semestre,
        activa=activa,
    )
    asignaturas, total = asignatura_service.get_asignaturas(db, filtros, skip=skip, limit=limit)
    return {
        "items": [AsignaturaResponse.model_validate(a) for a in asignaturas],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post(
    "/",
    response_model=AsignaturaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una asignatura",
)
def create_asignatura(
    data: AsignaturaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una asignatura nueva. Solo admin/secretario."""
    _check_admin(current_user)

    existente = asignatura_service.get_asignatura_by_codigo(db, data.codigo)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de asignatura ya está registrado",
        )

    return asignatura_service.create_asignatura(db, data)


@router.get(
    "/{asignatura_id}",
    response_model=AsignaturaResponse,
    summary="Obtener una asignatura por ID",
)
def get_asignatura(
    asignatura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los datos de una asignatura concreta."""
    asignatura = asignatura_service.get_asignatura_by_id(db, asignatura_id)
    if not asignatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignatura no encontrada",
        )
    return asignatura


@router.patch(
    "/{asignatura_id}",
    response_model=AsignaturaResponse,
    summary="Actualizar una asignatura",
)
def update_asignatura(
    asignatura_id: int,
    data: AsignaturaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una asignatura. Solo admin/secretario."""
    _check_admin(current_user)

    asignatura = asignatura_service.get_asignatura_by_id(db, asignatura_id)
    if not asignatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignatura no encontrada",
        )
    return asignatura_service.update_asignatura(db, asignatura, data)


@router.delete(
    "/{asignatura_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una asignatura",
)
def delete_asignatura(
    asignatura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina una asignatura. Solo admin."""
    if current_user.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede eliminar asignaturas",
        )

    asignatura = asignatura_service.get_asignatura_by_id(db, asignatura_id)
    if not asignatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignatura no encontrada",
        )
    asignatura_service.delete_asignatura(db, asignatura)