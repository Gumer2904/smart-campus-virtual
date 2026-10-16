"""
Tests de estudiantes.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.usuario import RolUsuario


def _estudiante_payload(expediente: str = "EST2026001", email: str = "est@test.com"):
    """Helper: payload para crear estudiante."""
    return {
        "expediente": expediente,
        "cedula": "01234567890",
        "fecha_nacimiento": "2000-05-15",
        "carrera": "Informática",
        "facultad": "Ingeniería",
        "año_ingreso": 2026,
        "usuario": {
            "email": email,
            "password": "password123",
            "nombre": "María",
            "apellidos": "Esono",
            "telefono": "+240222111222",
            "rol": "estudiante",
        },
    }


@pytest.mark.integration
class TestEstudiantes:
    """Tests CRUD de estudiantes."""

    def test_crear_estudiante(self, client: TestClient, auth_headers):
        """Crear estudiante como admin devuelve 201."""
        response = client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload(),
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["expediente"] == "EST2026001"
        assert data["usuario"]["email"] == "est@test.com"
        assert data["usuario"]["rol"] == "estudiante"

    def test_crear_estudiante_sin_token(self, client: TestClient):
        """Crear estudiante sin token devuelve 401."""
        response = client.post("/api/v1/estudiantes/", json=_estudiante_payload())
        assert response.status_code == 401

    def test_crear_estudiante_expediente_duplicado(
        self, client: TestClient, auth_headers
    ):
        """Expediente duplicado devuelve 400."""
        # Primer estudiante
        client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload("EST001", "uno@test.com"),
            headers=auth_headers,
        )
        # Segundo con mismo expediente
        response = client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload("EST001", "dos@test.com"),
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]

    def test_listar_estudiantes(self, client: TestClient, auth_headers):
        """Listar estudiantes devuelve array."""
        client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload(),
            headers=auth_headers,
        )
        response = client.get("/api/v1/estudiantes/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_obtener_estudiante_por_id(self, client: TestClient, auth_headers):
        """Obtener estudiante existente por ID."""
        created = client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload(),
            headers=auth_headers,
        ).json()
        response = client.get(
            f"/api/v1/estudiantes/{created['id']}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_obtener_estudiante_no_existe(self, client: TestClient, auth_headers):
        """Estudiante inexistente devuelve 404."""
        response = client.get("/api/v1/estudiantes/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_actualizar_estudiante(self, client: TestClient, auth_headers):
        """Actualizar estudiante existente."""
        created = client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload(),
            headers=auth_headers,
        ).json()
        response = client.patch(
            f"/api/v1/estudiantes/{created['id']}",
            json={"carrera": "Ingeniería Informática"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["carrera"] == "Ingeniería Informática"

    def test_eliminar_estudiante(self, client: TestClient, auth_headers):
        """Eliminar estudiante como admin devuelve 204."""
        created = client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload(),
            headers=auth_headers,
        ).json()
        response = client.delete(
            f"/api/v1/estudiantes/{created['id']}", headers=auth_headers
        )
        assert response.status_code == 204

    def test_estudiante_no_puede_crear(self, client: TestClient, db):
        """Un estudiante no puede crear otros estudiantes (403)."""
        from app.core.security import hash_password
        from app.models.usuario import Usuario

        # Crear estudiante
        user = Usuario(
            email="est@test.com",
            password_hash=hash_password("password123"),
            nombre="Est",
            apellidos="Test",
            rol=RolUsuario.ESTUDIANTE,
            activo=True,
        )
        db.add(user)
        db.commit()

        # Login como estudiante
        login = client.post(
            "/api/v1/auth/login",
            data={"username": "est@test.com", "password": "password123"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Intentar crear estudiante
        response = client.post(
            "/api/v1/estudiantes/",
            json=_estudiante_payload("EST999", "nuevo@test.com"),
            headers=headers,
        )
        assert response.status_code == 403