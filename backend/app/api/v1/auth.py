"""
Endpoints de autenticación.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.services import usuario_service

router = APIRouter()


@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
def register(data: UsuarioCreate, db: Session = Depends(get_db)):
    """Crea un usuario nuevo en el sistema."""
    # Verificar que el email no exista
    existente = usuario_service.get_usuario_by_email(db, data.email)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )
    return usuario_service.create_usuario(db, data)


@router.post(
    "/login",
    summary="Iniciar sesión (obtener token JWT)",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Autentica un usuario y devuelve un token JWT.
    
    - **username**: email del usuario
    - **password**: contraseña en texto plano
    """
    usuario = usuario_service.authenticate_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": usuario.email, "rol": usuario.rol.value})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": UsuarioResponse.model_validate(usuario),
    }


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obtener el usuario autenticado",
)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return current_user