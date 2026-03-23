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
        ticket_id="SAV-FALLBACK",
        message="Chauffage en panne",
        attachments=[],
        customer={"id": "C-001", "name": "Test"},
        equipment={"type": "boiler", "model": None},
        history={"previous_tickets": 0}
    )
    
    response = await analyze_ticket(payload)
    
    assert response.audit.decision_type == "rules_engine"
    assert response.qualification.category == "heating"
    assert "Fallback" in response.justification[-1]

@pytest.mark.anyio
async def test_ai_custom_success(monkeypatch):
    """
    Test que si l'IA est activée, elle est utilisée.
    """
    monkeypatch.setattr(settings, "ai_enabled", True)
    
    payload = TicketInput(
        ticket_id="SAV-AI",
        message="Fuite d'eau importante",
        attachments=[],
        customer={"id": "C-001", "name": "Test"},
        equipment={"type": "faucet", "model": None},
        history={"previous_tickets": 0}
    )
    
    response = await analyze_ticket(payload)
    
    assert response.audit.decision_type == "ai_assisted"
    assert response.qualification.category == "plumbing"
