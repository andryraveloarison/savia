import pytest
from app.application.use_cases.analyze_ticket import analyze_ticket
from app.infrastructure.schemas.ticket_schema import TicketInput
from app.core.config import get_settings

settings = get_settings()

@pytest.mark.anyio
async def test_ai_fallback_logic(monkeypatch):
    """
    Test que si l'IA est désactivée ou échoue, le moteur de règles prend le relais.
    """
    monkeypatch.setattr(settings, "ai_enabled", False)
    
    payload = TicketInput(
        ticket_id="TEST-FALLBACK",
        message="Chauffage en panne",
        customer={"id": "C-001", "name": "Test"},
        equipment={"type": "boiler", "model": None},
        history={"previous_tickets": 0}
    )
    
    response = await analyze_ticket(payload)
    
    assert response.audit.provider == "rules_engine"
    assert response.qualification.category == "heating"
    assert "Fallback" in response.justification[-1]

@pytest.mark.anyio
async def test_ai_mock_success(monkeypatch):
    """
    Test que si l'IA est activée, elle est utilisée.
    """
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(settings, "ai_provider", "mock")
    
    payload = TicketInput(
        ticket_id="TEST-AI",
        message="Fuite d'eau importante",
        customer={"id": "C-001", "name": "Test"},
        equipment={"type": "faucet", "model": None},
        history={"previous_tickets": 0}
    )
    
    response = await analyze_ticket(payload)
    
    assert response.audit.provider == "ai_mock"
    assert response.qualification.category == "plumbing"
    assert response.recommendation.confidence_score == 0.95
