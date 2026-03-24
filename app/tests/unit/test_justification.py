import pytest
from unittest.mock import patch
from app.domain.services.justification_service import JustificationService
from app.domain.entities.ticket import TicketEntity, CustomerEntity, EquipmentEntity, HistoryEntity
from app.domain.types.enums import Category, Urgency, Action, CompletenessStatus


def _make_ticket(equipment_type="boiler", previous_tickets=0) -> TicketEntity:
    return TicketEntity(
        ticket_id="SAV-TEST",
        message="Test message",
        attachments=[],
        customer=CustomerEntity(id="C-001", name="Test"),
        equipment=EquipmentEntity(type=equipment_type, model=None),
        history=HistoryEntity(previous_tickets=previous_tickets)
    )


def _make_inputs(urgency=Urgency.LOW, status=CompletenessStatus.INCOMPLETE, missing=None, action=Action.REQUEST_ADDITIONAL_INFO, score=0.9):
    qualification = {"category": Category.HEATING, "urgency": urgency}
    completeness = {"status": status, "missing_elements": missing or []}
    orientation = {"action": action, "confidence_score": score}
    return qualification, completeness, orientation


# ─── Urgency.CRITICAL ─────────────────────────────────────────────

def test_justification_critical_urgency():
    ticket = _make_ticket()
    qualification, completeness, orientation = _make_inputs(urgency=Urgency.CRITICAL)

    justifications = JustificationService.run(ticket, qualification, completeness, orientation)

    assert any("Critical" in j for j in justifications)


# ─── CompletenessStatus.COMPLETE ──────────────────────────────────

def test_justification_complete_ticket():
    ticket = _make_ticket()
    qualification, completeness, orientation = _make_inputs(status=CompletenessStatus.COMPLETE)

    justifications = JustificationService.run(ticket, qualification, completeness, orientation)

    assert any("All required information" in j for j in justifications)


# ─── category_mismatch ─────────────────

def test_justification_category_mismatch():
    ticket = _make_ticket()
    qualification, completeness, orientation = _make_inputs(
        status=CompletenessStatus.INCOMPLETE,
        missing=["category_mismatch:heating,plumbing"]
    )

    justifications = JustificationService.run(ticket, qualification, completeness, orientation)

    assert any("Inconsistency detected" in j for j in justifications)

# ─── previous_tickets > 0 ────────────────────────────────────────────────────

def test_justification_with_previous_tickets():
    ticket = _make_ticket(previous_tickets=3)
    qualification, completeness, orientation = _make_inputs()

    justifications = JustificationService.run(ticket, qualification, completeness, orientation)

    assert any("3 previous ticket" in j for j in justifications)