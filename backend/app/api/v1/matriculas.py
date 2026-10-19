"""
Endpoints CRUD para Matricula.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.matricula import EstadoMatricula
from app.models.usuario import RolUsuario, Usuario
from app.schemas.matricula import (
    MatriculaCreate,
    MatriculaFiltros,
    MatriculaResponse,
    MatriculaUpdate,
)
from app.services import asignatura_service, estudiante_service, matricula_service

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
    summary="Listar matrículas con filtros",
)
def list_matriculas(
    estudiante_id: int | None = Query(None),
    asignatura_id: int | None = Query(None),
    periodo: str | None = Query(None),
    estado: EstadoMatricula | None = Query(None),
    aprobada: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista matrículas con filtros y paginación."""
    filtros = MatriculaFiltros(
        estudiante_id=estudiante_id,
        asignatura_id=asignatura_id,
        periodo=periodo,
        estado=estado,
        aprobada=aprobada,
    )
    matriculas, total = matricula_service.get_matriculas(db, filtros, skip=skip, limit=limit)
    return {
        "items": [MatriculaResponse.model_validate(m) for m in matriculas],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post(
    "/",
    response_model=MatriculaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una matrícula",
)
def create_matricula(
    data: MatriculaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una matrícula nueva. Solo admin/secretario."""
    _check_admin(current_user)

    # Validar que el estudiante existe
    estudiante = estudiante_service.get_estudiante_by_id(db, data.estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado",
        )

    # Validar que la asignatura existe
    asignatura = asignatura_service.get_asignatura_by_id(db, data.asignatura_id)
    if not asignatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignatura no encontrada",
        )

    # Validar que no exista matrícula duplicada
    existente = matricula_service.get_matricula_existente(
        db, data.estudiante_id, data.asignatura_id, data.periodo
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El estudiante ya está matriculado en esa asignatura para ese período",
        )

    return matricula_service.create_matricula(db, data)


@router.get(
    "/{matricula_id}",
    response_model=MatriculaResponse,
    summary="Obtener una matrícula por ID",
)
def get_matricula(
    matricula_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve los datos de una matrícula."""
    matricula = matricula_service.get_matricula_by_id(db, matricula_id)
    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula no encontrada",
        )
    return matricula


@router.patch(
    "/{matricula_id}",
    response_model=MatriculaResponse,
    summary="Actualizar una matrícula (nota, estado, etc.)",
)
def update_matricula(
    matricula_id: int,
    data: MatriculaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una matrícula. Solo admin/secretario/docente."""
    if current_user.rol not in (
        RolUsuario.ADMINISTRADOR,
        RolUsuario.SECRETARIO,
        RolUsuario.DOCENTE,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )

    matricula = matricula_service.get_matricula_by_id(db, matricula_id)
    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula no encontrada",
        )
    return matricula_service.update_matricula(db, matricula, data)


@router.delete(
    "/{matricula_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una matrícula",
)
def delete_matricula(
    matricula_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina una matrícula. Solo admin."""
    if current_user.rol != RolUsuario.ADMINISTRADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede eliminar matrículas",
        )

    matricula = matricula_service.get_matricula_by_id(db, matricula_id)
    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matrícula no encontrada",
        )
    matricula_service.delete_matricula(db, matricula)
    
@router.post(
    "/inteligente",
    summary="Realizar una matrícula inteligente (con validaciones)",
)
    
def crear_matricula_inteligente(
    data: MatriculaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Realiza una matrícula validando automáticamente:
    - Prerrequisitos aprobados
    - Límite de créditos por período
    - Duplicados
    """
    _check_admin(current_user)

    # Validar estudiante
    estudiante = estudiante_service.get_estudiante_by_id(db, data.estudiante_id)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Ejecutar validaciones inteligentes
    resultado = matricula_service.validar_matricula_inteligente(
        db, data.estudiante_id, data.asignatura_id, data.periodo
    )

    if not resultado["puede_matricularse"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "mensaje": "Matrícula rechazada",
                "errores": resultado["errores"],
                "creditos_actuales": resultado["creditos_actuales"],
                "creditos_nuevos": resultado["creditos_nuevos"],
                "max_creditos": resultado["max_creditos"],
            },
        )

    # Si todo está bien, crear la matrícula
    return matricula_service.create_matricula(db, data)