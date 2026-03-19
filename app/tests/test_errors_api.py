import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def test_status_200_success():
    payload = {
        "ticket_id": "SAV-200",
        "message": "Ma chaudière est en panne",
        "customer": {"id": "C-1", "name": "John"},
        "equipment": {"type": "boiler", "model": "V-100"},
        "history": {"previous_tickets": 0}
    }
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == 200
    assert "qualification" in response.json()

def test_status_400_malformed_json():
    # Envoi d'un JSON syntaxiquement incorrect
    response = client.post(
        "/tickets/analyze", 
        content='{ "ticket_id": "SAV-400", "message": "unclosed... ', 
        headers={"Content-Type": "application/json"}
    )
    # FastAPI retourne 400 pour un JSON malformé via Starlette
    assert response.status_code == 400
    # Note: Starlette retourne souvent un texte simple en 400 ou un detail spécifique

def test_status_422_missing_field():
    # Manque le champ obligatoire 'message'
    payload = {
        "ticket_id": "SAV-422",
        "customer": {"id": "C-1", "name": "John"},
        "equipment": {"type": "boiler"}
    }
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"

def test_status_422_empty_message():
    # Message vide (échoue au validateur min_length ou custom)
    payload = {
        "ticket_id": "SAV-422-EMPTY",
        "message": "   ",
        "customer": {"id": "C-1", "name": "John"},
        "equipment": {"type": "boiler", "model": "V-100"}
    }
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"

def test_status_500_internal_error():
    # Simuler une exception non gérée dans le use case
    with patch("app.infrastructure.api.routes.analyze_ticket", side_effect=Exception("BOOM")):
        payload = {
            "ticket_id": "SAV-500",
            "message": "Test server error",
            "customer": {"id": "C-1", "name": "John"},
            "equipment": {"type": "boiler", "model": "V-100"}
        }
        response = client.post("/tickets/analyze", json=payload)
        assert response.status_code == 500
        assert response.json()["error"] == "internal_server_error"
        assert "BOOM" not in response.json()["detail"] # Ne doit pas exposer la stack
