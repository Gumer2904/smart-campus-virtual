"""
Tests de asignaturas.
"""
import pytest
from fastapi.testclient import TestClient


def _asignatura_payload(codigo: str = "PROG101", nombre: str = "Programación I"):
    """Helper: payload para crear asignatura."""
    return {
        "codigo": codigo,
        "nombre": nombre,
        "descripcion": "Descripción de prueba",
        "creditos": 6,
        "semestre": 1,
        "carrera": "Informática de Gestión",
        "facultad": "Ingeniería Informática",
        "prerrequisitos": None,
        "activa": True,
    }


@pytest.mark.integration
class TestAsignaturas:
    """Tests CRUD de asignaturas."""

    def test_crear_asignatura(self, client: TestClient, auth_headers):
        """Crear asignatura como admin devuelve 201."""
        response = client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload(),
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "PROG101"
        assert data["nombre"] == "Programación I"
        assert data["creditos"] == 6
        assert data["semestre"] == 1

    def test_crear_asignatura_sin_token(self, client: TestClient):
        """Crear asignatura sin token devuelve 401."""
        response = client.post("/api/v1/asignaturas/", json=_asignatura_payload())
        assert response.status_code == 401

    def test_crear_asignatura_codigo_duplicado(
        self, client: TestClient, auth_headers
    ):
        """Código duplicado devuelve 400."""
        client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload("PROG101"),
            headers=auth_headers,
        )
        response = client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload("PROG101", "Otra asignatura"),
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]

    def test_listar_asignaturas(self, client: TestClient, auth_headers):
        """Listar asignaturas devuelve estructura con items y total."""
        client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload(),
            headers=auth_headers,
        )
        response = client.get("/api/v1/asignaturas/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert data["total"] >= 1

    def test_filtro_search(self, client: TestClient, auth_headers):
        """Filtro search busca por código o nombre."""
        # Crear 2 asignaturas
        client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload("PROG101", "Programación I"),
            headers=auth_headers,
        )
        client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload("BD102", "Bases de Datos I"),
            headers=auth_headers,
        )
        # Buscar "prog"
        response = client.get(
            "/api/v1/asignaturas/?search=prog", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["codigo"] == "PROG101"

    def test_filtro_carrera(self, client: TestClient, auth_headers):
        """Filtro por carrera."""
        client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload("PROG101", "Programación I"),
            headers=auth_headers,
        )
        # Buscar por carrera
        response = client.get(
            "/api/v1/asignaturas/?carrera=Informática de Gestión",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_filtro_semestre(self, client: TestClient, auth_headers):
        """Filtro por semestre."""
        client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload("PROG101", "Programación I"),
            headers=auth_headers,
        )
        response = client.get("/api/v1/asignaturas/?semestre=1", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

        response = client.get("/api/v1/asignaturas/?semestre=5", headers=auth_headers)
        assert response.json()["total"] == 0

    def test_paginacion(self, client: TestClient, auth_headers):
        """Paginación con skip y limit."""
        # Crear 3 asignaturas
        for i in range(3):
            client.post(
                "/api/v1/asignaturas/",
                json=_asignatura_payload(f"TEST{i:03d}", f"Asignatura {i}"),
                headers=auth_headers,
            )
        # Pedir solo 2
        response = client.get(
            "/api/v1/asignaturas/?skip=0&limit=2", headers=auth_headers
        )
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 3
        assert data["limit"] == 2

    def test_obtener_asignatura_por_id(self, client: TestClient, auth_headers):
        """Obtener asignatura por ID."""
        created = client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload(),
            headers=auth_headers,
        ).json()
        response = client.get(
            f"/api/v1/asignaturas/{created['id']}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_obtener_asignatura_no_existe(self, client: TestClient, auth_headers):
        """Asignatura inexistente devuelve 404."""
        response = client.get("/api/v1/asignaturas/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_actualizar_asignatura(self, client: TestClient, auth_headers):
        """Actualizar asignatura."""
        created = client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload(),
            headers=auth_headers,
        ).json()
        response = client.patch(
            f"/api/v1/asignaturas/{created['id']}",
            json={"nombre": "Programación Avanzada", "creditos": 8},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["nombre"] == "Programación Avanzada"
        assert response.json()["creditos"] == 8

    def test_eliminar_asignatura(self, client: TestClient, auth_headers):
        """Eliminar asignatura como admin devuelve 204."""
        created = client.post(
            "/api/v1/asignaturas/",
            json=_asignatura_payload(),
            headers=auth_headers,
        ).json()
        response = client.delete(
            f"/api/v1/asignaturas/{created['id']}", headers=auth_headers
        )
        assert response.status_code == 204

    def test_validacion_creditos_invalidos(self, client: TestClient, auth_headers):
        """Créditos fuera de rango devuelven 422."""
        payload = _asignatura_payload()
        payload["creditos"] = 100  # máximo 20
        response = client.post(
            "/api/v1/asignaturas/", json=payload, headers=auth_headers
        )
        assert response.status_code == 422

    def test_validacion_semestre_invalido(self, client: TestClient, auth_headers):
        """Semestre fuera de rango devuelve 422."""
        payload = _asignatura_payload()
        payload["semestre"] = 15  # máximo 10
        response = client.post(
            "/api/v1/asignaturas/", json=payload, headers=auth_headers
        )
        assert response.status_code == 422