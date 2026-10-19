"""
Tests de matrículas.
"""
import pytest
from fastapi.testclient import TestClient


def _estudiante_payload(expediente: str = "EST2026001", email: str = "est@test.com"):
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


def _asignatura_payload(codigo: str = "PROG101", nombre: str = "Programación I"):
    return {
        "codigo": codigo,
        "nombre": nombre,
        "descripcion": "Descripción de prueba",
        "creditos": 6,
        "semestre": 1,
        "carrera": "Informática",
        "facultad": "Ingeniería",
        "prerrequisitos": None,
        "activa": True,
    }


@pytest.fixture
def setup_estudiante_y_asignatura(client: TestClient, auth_headers):
    """Fixture que crea un estudiante y una asignatura, devuelve sus IDs."""
    est = client.post(
        "/api/v1/estudiantes/", json=_estudiante_payload(), headers=auth_headers
    ).json()
    asig = client.post(
        "/api/v1/asignaturas/", json=_asignatura_payload(), headers=auth_headers
    ).json()
    return est["id"], asig["id"]


@pytest.mark.integration
class TestMatriculas:
    """Tests CRUD de matrículas."""

    def test_crear_matricula(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        payload = {
            "estudiante_id": est_id,
            "asignatura_id": asig_id,
            "periodo": "2026-1",
            "estado": "confirmada",
        }
        response = client.post(
            "/api/v1/matriculas/", json=payload, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["estudiante_id"] == est_id
        assert data["asignatura_id"] == asig_id
        assert data["periodo"] == "2026-1"
        assert data["estado"] == "confirmada"

    def test_crear_matricula_sin_token(self, client: TestClient):
        response = client.post("/api/v1/matriculas/", json={})
        assert response.status_code == 401

    def test_crear_matricula_estudiante_no_existe(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        _, asig_id = setup_estudiante_y_asignatura
        payload = {
            "estudiante_id": 99999,
            "asignatura_id": asig_id,
            "periodo": "2026-1",
        }
        response = client.post(
            "/api/v1/matriculas/", json=payload, headers=auth_headers
        )
        assert response.status_code == 404
        assert "Estudiante no encontrado" in response.json()["detail"]

    def test_crear_matricula_asignatura_no_existe(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, _ = setup_estudiante_y_asignatura
        payload = {
            "estudiante_id": est_id,
            "asignatura_id": 99999,
            "periodo": "2026-1",
        }
        response = client.post(
            "/api/v1/matriculas/", json=payload, headers=auth_headers
        )
        assert response.status_code == 404
        assert "Asignatura no encontrada" in response.json()["detail"]

    def test_crear_matricula_duplicada(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        payload = {
            "estudiante_id": est_id,
            "asignatura_id": asig_id,
            "periodo": "2026-1",
        }
        # Primera matrícula
        client.post("/api/v1/matriculas/", json=payload, headers=auth_headers)
        # Segunda matrícula igual
        response = client.post(
            "/api/v1/matriculas/", json=payload, headers=auth_headers
        )
        assert response.status_code == 400
        assert "ya está matriculado" in response.json()["detail"]

    def test_listar_matriculas(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        client.post(
            "/api/v1/matriculas/",
            json={"estudiante_id": est_id, "asignatura_id": asig_id, "periodo": "2026-1"},
            headers=auth_headers,
        )
        response = client.get("/api/v1/matriculas/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_filtro_por_estudiante(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        client.post(
            "/api/v1/matriculas/",
            json={"estudiante_id": est_id, "asignatura_id": asig_id, "periodo": "2026-1"},
            headers=auth_headers,
        )
        response = client.get(
            f"/api/v1/matriculas/?estudiante_id={est_id}", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_filtro_por_periodo(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        client.post(
            "/api/v1/matriculas/",
            json={"estudiante_id": est_id, "asignatura_id": asig_id, "periodo": "2026-1"},
            headers=auth_headers,
        )
        response = client.get(
            "/api/v1/matriculas/?periodo=2026-1", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

        response = client.get(
            "/api/v1/matriculas/?periodo=2099-1", headers=auth_headers
        )
        assert response.json()["total"] == 0

    def test_actualizar_nota_y_aprobar(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        created = client.post(
            "/api/v1/matriculas/",
            json={"estudiante_id": est_id, "asignatura_id": asig_id, "periodo": "2026-1"},
            headers=auth_headers,
        ).json()

        # Asignar nota 4.5 (debería aprobar automáticamente)
        response = client.patch(
            f"/api/v1/matriculas/{created['id']}",
            json={"nota_final": 4.5, "estado": "completada"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nota_final"] == 4.5
        assert data["aprobada"] is True

    def test_actualizar_nota_suspensa(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        created = client.post(
            "/api/v1/matriculas/",
            json={"estudiante_id": est_id, "asignatura_id": asig_id, "periodo": "2026-1"},
            headers=auth_headers,
        ).json()

        # Asignar nota 2.0 (debería suspender automáticamente)
        response = client.patch(
            f"/api/v1/matriculas/{created['id']}",
            json={"nota_final": 2.0},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nota_final"] == 2.0
        assert data["aprobada"] is False

    def test_eliminar_matricula(
        self, client: TestClient, auth_headers, setup_estudiante_y_asignatura
    ):
        est_id, asig_id = setup_estudiante_y_asignatura
        created = client.post(
            "/api/v1/matriculas/",
            json={"estudiante_id": est_id, "asignatura_id": asig_id, "periodo": "2026-1"},
            headers=auth_headers,
        ).json()
        response = client.delete(
            f"/api/v1/matriculas/{created['id']}", headers=auth_headers
        )
        assert response.status_code == 204