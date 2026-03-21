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

# ─── Tests Completeness ───────────────────────────────────────────────

def test_has_exploitable_attachment():
    assert has_exploitable_attachment([]) is False
    assert has_exploitable_attachment([{"type": "photo", "description": "une fuite"}]) is True
    assert has_exploitable_attachment([{"type": "pdf", "description": "  "}]) is False

def test_check_completeness():
    missing = check_completeness("Aider", None, "boiler", [])
    assert "equipment_model" in missing
    assert "clear_photo" in missing
    assert "detailed_message" in missing

# ─── Tests Orientation ────────────────────────────────────────────────

def test_decide_action_urgency():
    # Urgence High -> Intervention immédiate même si incomplet
    action = decide_action(
        message="Inondation !",
        urgency=Urgency.HIGH,
        equipment_type="faucet",
        previous_tickets_count=0,
        confidence_score=0.8,
        missing_elements=["equipment_model"]
    )
    assert action == Action.SCHEDULE_INTERVENTION

def test_decide_action_missing_info():
    # Urgence Low + Incomplet -> Demande d'infos
    action = decide_action(
        message="Besoin d'un entretien",
        urgency=Urgency.LOW,
        equipment_type="boiler",
        previous_tickets_count=0,
        confidence_score=0.9,
        missing_elements=["equipment_model"]
    )
    assert action == Action.REQUEST_ADDITIONAL_INFO

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
