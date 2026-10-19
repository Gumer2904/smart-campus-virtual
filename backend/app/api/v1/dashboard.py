"""
Endpoints para el Dashboard.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import RolUsuario, Usuario
from app.services import dashboard_service

router = APIRouter()


@router.get(
    "/stats",
    summary="Obtener estadísticas para el dashboard",
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Devuelve contadores generales y matrículas por carrera.
    Accesible para todos los usuarios autenticados.
    """
    return dashboard_service.get_resumen_completo(db)