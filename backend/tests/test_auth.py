"""
Tests de autenticación.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.usuario import RolUsuario


@pytest.mark.integration
class TestAuth:
    """Tests del módulo de autenticación."""

    def test_register_usuario_exitoso(self, client: TestClient):
        """Registrar un usuario nuevo devuelve 201."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "nuevo@test.com",
                "password": "password123",
                "nombre": "Nuevo",
                "apellidos": "Usuario",
                "telefono": "+240222000000",
                "rol": "estudiante",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nuevo@test.com"
        assert data["nombre"] == "Nuevo"
        assert data["rol"] == "estudiante"
        assert "id" in data
        assert "password_hash" not in data  # ¡No exponer hash!

    def test_register_email_duplicado(self, client: TestClient, admin_user):
        """Registrar con email existente devuelve 400."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",
                "password": "password123",
                "nombre": "Otro",
                "apellidos": "Usuario",
                "rol": "estudiante",
            },
        )
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]

    def test_login_exitoso(self, client: TestClient, admin_user):
        """Login con credenciales correctas devuelve token."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "admin12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["usuario"]["email"] == "admin@test.com"

    def test_login_password_incorrecta(self, client: TestClient, admin_user):
        """Login con password incorrecta devuelve 401."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_email_no_existe(self, client: TestClient):
        """Login con email inexistente devuelve 401."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "noexiste@test.com", "password": "cualquiera"},
        )
        assert response.status_code == 401

    def test_get_me_con_token(self, client: TestClient, auth_headers):
        """GET /me con token válido devuelve el usuario."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["rol"] == "administrador"

    def test_get_me_sin_token(self, client: TestClient):
        """GET /me sin token devuelve 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_token_invalido(self, client: TestClient):
        """GET /me con token inválido devuelve 401."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_invalido"},
        )
        assert response.status_code == 401