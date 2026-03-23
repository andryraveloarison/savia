import pytest
import allure
from app.application.use_cases.analyze_ticket import analyze_ticket
from app.infrastructure.schemas.ticket_schema import TicketInput

@pytest.mark.parametrize("tc", [
    {
        "id": "T1",
        "message": "Chauffage ne démarre plus ce matin",
        "eq_type": "boiler",
        "eq_model": None,
        "expected_cat": "heating",
        "expected_urg": "medium",
        "expected_action": "request_additional_info",
    },
    {
        "id": "T2",
        "message": "Fuite d'eau sous l'évier, inondation en cours",
        "eq_type": "faucet",
        "eq_model": None,
        "expected_cat": "plumbing",
        "expected_urg": "high",
        "expected_action": "schedule_intervention",
    },
    {
        "id": "T3",
        "message": "Disjoncteur qui saute régulièrement",
        "eq_type": "circuit_breaker",
        "eq_model": "ABB-123",
        "expected_cat": "electrical",
        "expected_urg": "medium",
        "expected_action": "schedule_intervention",
    },
    {
        "id": "T4",
        "message": "Problème",
        "eq_type": None,
        "eq_model": None,
        "expected_cat": "other",
        "expected_urg": "low",
        "expected_action": "escalate_to_human",
    },
    {
        "id": "T5",
        "message": "Chaudière gaz en panne, 1er ticket client",
        "eq_type": "boiler",
        "eq_model": None,
        "expected_cat": "heating",
        "expected_urg": "high",
        "expected_action": "schedule_intervention",
    }
])
@pytest.mark.anyio
async def test_analyze_ticket(tc):
    payload = TicketInput(
        ticket_id=f"SAV-{tc['id']}",
        message=tc['message'],
        attachments=[],
        customer={"id": "C-001", "name": "Test"},
        equipment={
            "type": tc["eq_type"] or "unknown",
            "model": tc["eq_model"]
        },
        history={"previous_tickets": 0}
    )

    # ⚡ Attacher le payload envoyé à Allure
    allure.attach(
        payload.model_dump_json(indent=2),
        name="Payload envoyé",
        attachment_type=allure.attachment_type.JSON
    )

    response = await analyze_ticket(payload)

    assert response.qualification.category == tc["expected_cat"]
    assert response.qualification.urgency == tc["expected_urg"]
    assert response.recommendation.action == tc["expected_action"]