from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture
def mock_db():
    """
    Intercepta get_db_connection() en main.py y devuelve una conexión y cursor falsos.
    """
    with patch("main.get_db_connection") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Simula el bloque: with conn.cursor() as cur:
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn, mock_cursor


# --- 4.1. Registrar una tarea ---

def test_crear_tarea_exitosa(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "titulo": "Implementar pruebas",
        "prioridad": "alta",
        "completada": False,
    }

    response = client.post(
        "/api/tareas",
        json={"titulo": "  Implementar pruebas  ", "prioridad": "alta"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "titulo": "Implementar pruebas",
        "prioridad": "alta",
        "completada": False,
    }
    mock_conn.commit.assert_called_once()


def test_crear_tarea_titulo_vacio():
    # No necesita mock_db porque Pydantic rechaza la petición antes de tocar la BD
    response = client.post(
        "/api/tareas",
        json={"titulo": "   ", "prioridad": "media"},
    )
    assert response.status_code == 422


def test_crear_tarea_prioridad_invalida():
    response = client.post(
        "/api/tareas",
        json={"titulo": "Revisar logs", "prioridad": "urgente"},
    )
    assert response.status_code == 422


# --- 4.2. Consultar todas las tareas ---

def test_listar_tareas(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchall.return_value = [
        {"id": 1, "titulo": "Tarea A", "prioridad": "alta", "completada": False},
        {"id": 2, "titulo": "Tarea B", "prioridad": "baja", "completada": True},
    ]

    response = client.get("/api/tareas")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["titulo"] == "Tarea A"


# --- 4.3. Buscar una tarea ---

def test_buscar_tarea_existente(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "titulo": "Corregir login",
        "prioridad": "alta",
        "completada": False,
    }

    response = client.get("/api/tareas/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_buscar_tarea_inexistente(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None

    response = client.get("/api/tareas/999")

    assert response.status_code == 404
    assert "No se encontró" in response.json()["detail"]


# --- 4.4. Completar una tarea ---

def test_completar_tarea_pendiente(mock_db):
    mock_conn, mock_cursor = mock_db
    # Primera llamada (SELECT) devuelve pendiente; segunda llamada (UPDATE RETURNING) devuelve completada
    mock_cursor.fetchone.side_effect = [
        {"id": 1, "titulo": "Corregir login", "prioridad": "alta", "completada": False},
        {"id": 1, "titulo": "Corregir login", "prioridad": "alta", "completada": True},
    ]

    response = client.patch("/api/tareas/1/completar")

    assert response.status_code == 200
    assert response.json()["completada"] is True
    mock_conn.commit.assert_called_once()


def test_completar_tarea_ya_completada(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "titulo": "Corregir login",
        "prioridad": "alta",
        "completada": True,
    }

    response = client.patch("/api/tareas/1/completar")

    assert response.status_code == 400
    assert "ya se encuentra completada" in response.json()["detail"]
    mock_conn.commit.assert_not_called()


def test_completar_tarea_inexistente(mock_db):
    _, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None

    response = client.patch("/api/tareas/999/completar")

    assert response.status_code == 404


# --- 4.5. Eliminar una tarea ---

def test_eliminar_tarea_existente(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = {"id": 1}

    response = client.delete("/api/tareas/1")

    assert response.status_code == 200
    assert "eliminada correctamente" in response.json()["mensaje"]
    mock_conn.commit.assert_called_once()


def test_eliminar_tarea_inexistente(mock_db):
    mock_conn, mock_cursor = mock_db
    mock_cursor.fetchone.return_value = None

    response = client.delete("/api/tareas/999")

    assert response.status_code == 404
    mock_conn.commit.assert_not_called()