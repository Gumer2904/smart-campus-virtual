"""
Endpoints CRUD para Estudiante.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.schemas.estudiante import (
    EstudianteCreate,
    EstudianteResponse,
    EstudianteUpdate,
)
from app.services import estudiante_service

router = APIRouter()


def _check_admin(current_user: Usuario):
    """Verifica que el usuario tenga permisos de administrador."""
    if current_user.rol not in (RolUsuario.ADMINISTRADOR, RolUsuario.SECRETARIO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )


@router.get(
    "/",
    response_model=list[EstudianteResponse],
    summary="Listar estudiantes",
)
def list_estudiantes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve la lista de estudiantes con paginación."""
    return estudiante_service.get_estudiantes(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=EstudianteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un estudiante",
)
def create_estudiante(
    data: EstudianteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un estudiante nuevo (y su Usuario asociado). Solo admin/secretario."""
    _check_admin(current_user)

    # Verificar que el expediente no exista
    existente = estudiante_service.get_estudiante_by_expediente(db, data.expediente)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El expediente ya está registrado",
        )

    return estudiante_service.create_estudiante(db, data)


@router.get(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    summary="Obtener un estudiante por ID",
)
def get_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los datos de un estudiante concreto."""
    estudiante = estudiante_service.get_estudiante_by_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )
    return estudiante


@router.patch(
    "/{estudiante_id}",
    response_model=EstudianteResponse,
    summary="Actualizar un estudiante",
)
def update_estudiante(
    estudiante_id: int,
    data: EstudianteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los datos de un estudiante. Solo admin/secretario."""
    _check_admin(current_user)

    estudiante = estudiante_service.get_estudiante_by_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )
    return estudiante_service.update_estudiante(db, estudiante, data)


@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un estudiante",
)
def delete_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina un estudiante (y su Usuario asociado). Solo admin."""
    if current_user.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede eliminar estudiantes",
        )

    estudiante = estudiante_service.get_estudiante_by_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )
    estudiante_service.delete_estudiante(db, estudiante)