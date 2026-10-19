"""
Servicios de agregación para el Dashboard.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asignatura import Asignatura
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.matricula import EstadoMatricula, Matricula
from app.models.usuario import RolUsuario, Usuario


def get_resumen_general(db: Session) -> dict:
    """Obtiene los contadores principales para el dashboard."""
    
    total_estudiantes = db.execute(
        select(func.count(Estudiante.id))
    ).scalar_one()

    total_docentes = db.execute(
        select(func.count(Docente.id))
    ).scalar_one()

    total_asignaturas = db.execute(
        select(func.count(Asignatura.id))
    ).scalar_one()

    total_matriculas = db.execute(
        select(func.count(Matricula.id))
    ).scalar_one()

    # Matrículas activas (no anuladas)
    matriculas_activas = db.execute(
        select(func.count(Matricula.id)).where(
            Matricula.estado != EstadoMatricula.ANULADA
        )
    ).scalar_one()

    return {
        "total_estudiantes": total_estudiantes,
        "total_docentes": total_docentes,
        "total_asignaturas": total_asignaturas,
        "total_matriculas": total_matriculas,
        "matriculas_activas": matriculas_activas,
    }


def get_matriculas_por_carrera(db: Session) -> list[dict]:
    """Devuelve el número de matrículas agrupadas por carrera de la asignatura."""
    stmt = (
        select(
            Asignatura.carrera,
            func.count(Matricula.id).label("total"),
        )
        .join(Matricula, Matricula.asignatura_id == Asignatura.id)
        .group_by(Asignatura.carrera)
    )
    
    resultados = db.execute(stmt).all()
    
    return [
        {"carrera": r.carrera or "Sin asignar", "total": r.total}
        for r in resultados
    ]


def get_resumen_completo(db: Session) -> dict:
    """Devuelve todo lo necesario para el dashboard."""
    return {
        "resumen": get_resumen_general(db),
        "matriculas_por_carrera": get_matriculas_por_carrera(db),
    }