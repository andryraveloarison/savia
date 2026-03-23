import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_status_200_success():
    payload = {
        "ticket_id": "SAV-200",
        "message": "Ma chaudière est en panne",
        "attachments": [],
        "customer": {"id": "C-1", "name": "John"},
        "equipment": {"type": "boiler", "model": "V-100"},
        "history": {"previous_tickets": 0}
    }
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == HTTP_200_OK
    assert "qualification" in response.json()


def test_status_400_malformed_json():
    # Envoi d'un JSON syntaxiquement incorrect
    response = client.post(
        "/tickets/analyze", 
        content='{ "ticket_id": "SAV-400", "message": "unclosed... ',
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_status_422_missing_field():
    # Champ obligatoire 'message' manquant
    payload = {
        "ticket_id": "SAV-422",
        "attachments": [],
        "customer": {"id": "C-1", "name": "John"},
        "equipment": {"type": "boiler"},
        "history": {"previous_tickets": 0}
    }
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["error"] == "validation_error"


def test_status_422_empty_message():
    # Message vide échoue au validateur min_length ou custom
    payload = {
        "ticket_id": "SAV-422-EMPTY",
        "message": "   ",
        "attachments": [],
        "customer": {"id": "C-1", "name": "John"},
        "equipment": {"type": "boiler", "model": "V-100"},
        "history": {"previous_tickets": 0}
    }
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json()["error"] == "validation_error"


def test_status_500_internal_error():
    # Simuler une exception non gérée dans le use case
    with patch("app.infrastructure.api.routes.analyze_ticket", side_effect=Exception("BOOM")):
        payload = {
            "ticket_id": "SAV-500",
            "message": "Test server error",
            "attachments": [],
            "customer": {"id": "C-1", "name": "John"},
            "equipment": {"type": "boiler", "model": "V-100"},
            "history": {"previous_tickets": 0}
        }
        response = client.post("/tickets/analyze", json=payload)
        assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["error"] == "internal_server_error"
        assert "BOOM" not in response.json().get("detail", "")