"""
Configuración de pytest: fixtures compartidas.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.usuario import RolUsuario, Usuario

# ===== BD de prueba (en memoria SQLite o PostgreSQL test) =====
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "/smartcampus_db", "/smartcampus_test_db"
)

engine_test = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crea las tablas al inicio y las borra al final."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db():
    """Sesión de BD para tests, con rollback al final."""
    connection = engine_test.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Cliente HTTP de test con la BD de prueba inyectada."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db) -> Usuario:
    """Crea un usuario administrador de prueba."""
    usuario = Usuario(
        email="admin@test.com",
        password_hash=hash_password("admin12345"),
        nombre="Admin",
        apellidos="Test",
        rol=RolUsuario.ADMINISTRADOR,
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def admin_token(client, admin_user) -> str:
    """Devuelve un token JWT de admin."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "admin12345"},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token) -> dict:
    """Headers con token de admin para peticiones autenticadas."""
    return {"Authorization": f"Bearer {admin_token}"}