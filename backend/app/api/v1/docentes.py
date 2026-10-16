"""
Endpoints CRUD para Docente.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.schemas.docente import DocenteCreate, DocenteResponse, DocenteUpdate
from app.services import docente_service

router = APIRouter()


def _check_admin(current_user: Usuario):
    """Verifica que el usuario tenga permisos de administrador."""
    if current_user.rol not in (RolUsuario.ADMINISTRADOR, RolUsuario.SECRETARIO):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )


@router.get("/", response_model=list[DocenteResponse], summary="Listar docentes")
def list_docentes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve la lista de docentes con paginación."""
    return docente_service.get_docentes(db, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=DocenteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un docente",
)
def create_docente(
    data: DocenteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un docente nuevo (y su Usuario asociado). Solo admin/secretario."""
    _check_admin(current_user)

    existente = docente_service.get_docente_by_codigo(db, data.codigo_empleado)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de empleado ya está registrado",
        )

    return docente_service.create_docente(db, data)


@router.get(
    "/{docente_id}",
    response_model=DocenteResponse,
    summary="Obtener un docente por ID",
)
def get_docente(
    docente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los datos de un docente concreto."""
    docente = docente_service.get_docente_by_id(db, docente_id)
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Docente no encontrado",
        )
    return docente


@router.patch(
    "/{docente_id}",
    response_model=DocenteResponse,
    summary="Actualizar un docente",
)
def update_docente(
    docente_id: int,
    data: DocenteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los datos de un docente. Solo admin/secretario."""
    _check_admin(current_user)

    docente = docente_service.get_docente_by_id(db, docente_id)
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Docente no encontrado",
        )
    return docente_service.update_docente(db, docente, data)


@router.delete(
    "/{docente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un docente",
)
def delete_docente(
    docente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina un docente (y su Usuario asociado). Solo admin."""
    if current_user.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede eliminar docentes",
        )

    docente = docente_service.get_docente_by_id(db, docente_id)
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Docente no encontrado",
        )
    docente_service.delete_docente(db, docente)