"""
Servicios (lógica de negocio) para Usuario.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


def get_usuario_by_id(db: Session, usuario_id: int) -> Usuario | None:
    """Obtiene un usuario por su ID."""
    return db.get(Usuario, usuario_id)


def get_usuario_by_email(db: Session, email: str) -> Usuario | None:
    """Obtiene un usuario por su email."""
    stmt = select(Usuario).where(Usuario.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    """Obtiene lista de usuarios con paginación."""
    stmt = select(Usuario).offset(skip).limit(limit).order_by(Usuario.id)
    return list(db.execute(stmt).scalars().all())


def create_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    """Crea un usuario nuevo (hashea la contraseña)."""
    usuario = Usuario(
        email=data.email,
        password_hash=hash_password(data.password),
        nombre=data.nombre,
        apellidos=data.apellidos,
        telefono=data.telefono,
        rol=data.rol,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def update_usuario(db: Session, usuario: Usuario, data: UsuarioUpdate) -> Usuario:
    """Actualiza un usuario existente."""
    update_data = data.model_dump(exclude_unset=True)

    # Si se cambia la contraseña, hashearla
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario: Usuario) -> None:
    """Elimina un usuario."""
    db.delete(usuario)
    db.commit()


def authenticate_usuario(db: Session, email: str, password: str) -> Usuario | None:
    """Autentica un usuario por email y contraseña."""
    usuario = get_usuario_by_email(db, email)
    if not usuario:
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    if not usuario.activo:
        return None
    return usuario