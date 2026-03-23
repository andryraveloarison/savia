import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.parametrize("tc", [
    {
        "id": "T1",
        "message": "Chauffage ne démarre plus ce matin",
        "eq_type": "boiler",
        "eq_model": None,
        "expected_cat": "heating",
        "expected_urg": "medium",
        "expected_action": "request_additional_info",
        "expected_consistent": True
    },
    {
        "id": "T2",
        "message": "Fuite d'eau sous l'évier, inondation en cours",
        "eq_type": "faucet",
        "eq_model": None,
        "expected_cat": "plumbing",
        "expected_urg": "high",
        "expected_action": "schedule_intervention",
        "expected_consistent": True
    },
    {
        "id": "T3",
        "message": "Disjoncteur qui saute régulièrement",
        "eq_type": "circuit_breaker",
        "eq_model": "ABB-123",
        "expected_cat": "electrical",
        "expected_urg": "medium",
        "expected_action": "schedule_intervention",
        "expected_consistent": True
    },
    {
        "id": "T4",
        "message": "Problème",
        "eq_type": "unknown",
        "eq_model": None,
        "expected_cat": "other",
        "expected_urg": "low",
        "expected_action": "escalate_to_human",
        "expected_consistent": True
    },
    {
        "id": "T5",
        "message": "Chaudière gaz en panne, 1er ticket client",
        "eq_type": "boiler",
        "eq_model": None,
        "expected_cat": "heating",
        "expected_urg": "high",
        "expected_action": "schedule_intervention",
        "expected_consistent": True
    }
])
def test_analyze_ticket_api(tc):
    payload = {
        "ticket_id": f"SAV-{tc['id']}",
        "message": tc['message'],
        "attachments": [],
        "customer": {"id": "C-123", "name": "John Doe"},
        "equipment": {
            "type": tc['eq_type'],
            "model": tc['eq_model']
        },
        "history": {"previous_tickets": 0}
    }
    
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["qualification"]["category"] == tc["expected_cat"]
    assert data["qualification"]["urgency"] == tc["expected_urg"]
    assert data["qualification"]["is_consistent"] == tc["expected_consistent"]
    assert data["recommendation"]["action"] == tc["expected_action"]
