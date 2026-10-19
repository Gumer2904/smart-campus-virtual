"""
Tests de docentes.
"""
import pytest
from fastapi.testclient import TestClient


def _docente_payload(codigo: str = "DOC001", email: str = "doc@test.com"):
    return {
        "codigo_empleado": codigo,
        "departamento": "Informática",
        "categoria": "Titular",
        "especialidad": "Bases de Datos",
        "usuario": {
            "email": email,
            "password": "password123",
            "nombre": "Pedro",
            "apellidos": "Nguema",
            "telefono": "+240222333444",
            "rol": "docente",
        },
    }


@pytest.mark.integration
class TestDocentes:
    def test_crear_docente(self, client: TestClient, auth_headers):
        response = client.post(
            "/api/v1/docentes/",
            json=_docente_payload(),
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["codigo_empleado"] == "DOC001"
        assert response.json()["usuario"]["rol"] == "docente"

    def test_crear_docente_sin_token(self, client: TestClient):
        response = client.post("/api/v1/docentes/", json=_docente_payload())
        assert response.status_code == 401

    def test_codigo_duplicado(self, client: TestClient, auth_headers):
        client.post("/api/v1/docentes/", json=_docente_payload(), headers=auth_headers)
        response = client.post(
            "/api/v1/docentes/",
            json=_docente_payload("DOC001", "otro@test.com"),
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]

    def test_listar_docentes(self, client: TestClient, auth_headers):
        client.post("/api/v1/docentes/", json=_docente_payload(), headers=auth_headers)
        response = client.get("/api/v1/docentes/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_obtener_docente(self, client: TestClient, auth_headers):
        created = client.post(
            "/api/v1/docentes/", json=_docente_payload(), headers=auth_headers
        ).json()
        response = client.get(f"/api/v1/docentes/{created['id']}", headers=auth_headers)
        assert response.status_code == 200

    def test_actualizar_docente(self, client: TestClient, auth_headers):
        created = client.post(
            "/api/v1/docentes/", json=_docente_payload(), headers=auth_headers
        ).json()
        response = client.patch(
            f"/api/v1/docentes/{created['id']}",
            json={"categoria": "Asociado"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["categoria"] == "Asociado"

    def test_eliminar_docente(self, client: TestClient, auth_headers):
        created = client.post(
            "/api/v1/docentes/", json=_docente_payload(), headers=auth_headers
        ).json()
        response = client.delete(
            f"/api/v1/docentes/{created['id']}", headers=auth_headers
        )
        assert response.status_code == 204