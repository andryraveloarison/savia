import pytest
from app.domain.rules_engine.qualification import qualify_ticket
from app.domain.rules_engine.completeness import check_completeness, has_exploitable_attachment
from app.domain.rules_engine.orientation import decide_action
from app.domain.rules_engine.scoring import compute_confidence_score
from app.domain.types.enums import Category, Urgency, Action
from app.shared.utils.text import normalize_text, count_keywords

# ─── Tests Qualification ──────────────────────────────────────────────

def test_normalize_text():
    assert normalize_text("L'eau est chaude !") == "l eau est chaude"
    assert normalize_text("Chaudière éteinte") == "chaudiere eteinte"
    assert normalize_text("Fuite d'eau") == "fuite d eau"

def test_count_keywords():
    text = "il y a une fuite d eau sous l evier"
    assert count_keywords(text, ["fuite", "eau"]) == 2
    assert count_keywords(text, ["chaudiere"]) == 0
    # Test mot entier
    assert count_keywords("pactole", ["pac"]) == 0 

def test_qualify_ticket_consistency():
    # Cas cohérent
    res = qualify_ticket("Ma chaudiere est en panne", "boiler")
    assert res["category"] == Category.HEATING
    assert res["is_consistent"] is True
    
    # Cas incohérent
    res = qualify_ticket("Inondation dans la cuisine", "boiler")
    assert res["category"] == Category.HEATING # Priorité équipement
    assert res["is_consistent"] is False # Car keywords pointent vers plumbing


# ─── Tests Scoring ────────────────────────────────────────────────────

def test_compute_confidence_score():
    score = compute_confidence_score(
        keyword_match_ratio=0.8,
        equipment_type="boiler",
        previous_tickets=0,
        missing_elements=[],
        has_useful_attachment=True
    )
    assert score > 0.8
    
    score_low = compute_confidence_score(
        keyword_match_ratio=0.1,
        equipment_type=None,
        previous_tickets=0,
        missing_elements=["model", "photo"],
        has_useful_attachment=False
    )
    assert score_low < 0.3


# ─── History rules ────────────────────────────────────────────────────

def test_previous_tickets_count_no_history():
    """Couvre le return 0 quand history est None"""
    from app.domain.entities.ticket import TicketEntity, CustomerEntity, EquipmentEntity

    ticket = TicketEntity(
        ticket_id="SAV-TEST",
        message="Test",
        customer=CustomerEntity(id="C-001", name="Test"),
        equipment=EquipmentEntity(type="boiler"),
        history=None  # ← force le return 0
    )

    assert ticket.previous_tickets_count == 0