import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.analyze_ticket import analyze_ticket
from app.infrastructure.schemas.ticket_schema import TicketInput
from app.core.config import get_settings
from app.domain.services.ai_analysis_service import AIAnalysisService
from app.domain.entities.ticket import TicketEntity
from app.domain.entities.ai_result import AIAnalysisResult
from app.domain.entities.ticket import TicketEntity, CustomerEntity, EquipmentEntity, HistoryEntity
from app.domain.types.enums import Category, Urgency, Action
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


# ─── Nouveaux tests pour AIAnalysisService ───────────────────────────────────

def _make_ticket() -> TicketEntity:
    """Helper pour créer un TicketEntity minimal."""
    return TicketEntity(
        ticket_id="SAV-TEST",
        message="Chauffage en panne",
        attachments=[],
        customer=CustomerEntity(id="C-001", name="Test"),
        equipment=EquipmentEntity(type="boiler", model=None),
        history=HistoryEntity(previous_tickets=0)
    )

@pytest.mark.anyio
async def test_ai_analysis_service_success(monkeypatch):
    """
    L'IA est activée et retourne un résultat avec un score de confiance suffisant.
    """
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(settings, "confidence_threshold_ai", 0.5)

    ai_result = AIAnalysisResult(
        category="heating",
        urgency="high",
        action="send_technician",
        confidence_score=0.9,
        justifications=["AI detected heating failure"],
    )

    ai_client = MagicMock()
    ai_client.analyze_ticket = AsyncMock(return_value=ai_result)

    completeness = {"is_complete": True, "missing_fields": []}
    ticket = _make_ticket()

    result = await AIAnalysisService.run(ticket, ai_client, completeness)

    assert result["provider"] == "ai_assisted"
    assert result["category"] == "heating"
    assert result["confidence_score"] == 0.9
    ai_client.analyze_ticket.assert_awaited_once_with(ticket)


@pytest.mark.anyio
async def test_ai_analysis_service_low_confidence_triggers_fallback(monkeypatch):
    """
    Score IA trop bas → fallback règles.
    """
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(settings, "confidence_threshold_ai", 0.8)

    ai_result = AIAnalysisResult(
        category="heating",
        urgency="low",
        action="ask_info",
        confidence_score=0.4,
        justifications=["Low confidence"],
    )

    ai_client = MagicMock()
    ai_client.analyze_ticket = AsyncMock(return_value=ai_result)

    completeness = {"is_complete": True, "missing_fields": [], "missing_elements": []}
    ticket = _make_ticket()

    result = await AIAnalysisService.run(ticket, ai_client, completeness)

    assert result["provider"] == "rules_engine"
    assert "Fallback" in result["justifications"][0]


@pytest.mark.anyio
async def test_ai_analysis_service_exception_triggers_fallback(monkeypatch):
    """
    Exception IA → fallback règles.
    """
    monkeypatch.setattr(settings, "ai_enabled", True)

    ai_client = MagicMock()
    ai_client.analyze_ticket = AsyncMock(side_effect=Exception("API timeout"))

    completeness = {"is_complete": True, "missing_fields": [], "missing_elements": []}
    ticket = _make_ticket()

    result = await AIAnalysisService.run(ticket, ai_client, completeness)

    assert result["provider"] == "rules_engine"
    assert "Fallback" in result["justifications"][0]



@pytest.mark.anyio
async def test_ai_adapter_default_case():
    """Message sans keywords fuite/inondation → OTHER/LOW pour le mock ai"""
    from app.infrastructure.ai.adapter import AIAdapter

    adapter = AIAdapter()
    ticket = _make_ticket()  # message = "Chauffage en panne", pas de fuite/inondation

    result = await adapter.analyze_ticket(ticket)

    assert result.category == Category.OTHER
    assert result.urgency == Urgency.LOW
    assert result.confidence_score == 0.5