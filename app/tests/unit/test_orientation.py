import pytest
from app.domain.rules_engine.orientation import decide_action
from app.domain.types.enums import Action, Urgency
from unittest.mock import patch


# ─── urgency == Urgency.MEDIUM complet ────────────────────────────

def test_decide_action_medium_urgency_complete():
    """Urgence MEDIUM + aucun élément critique manquant → SCHEDULE_INTERVENTION"""
    action = decide_action(
        message="Chaudière en panne",
        urgency=Urgency.MEDIUM,
        equipment_type="boiler",
        previous_tickets_count=0,
        confidence_score=0.9,
        missing_elements=[]
    )
    assert action == Action.SCHEDULE_INTERVENTION


# ─── AUTO_RESOLUTION ──────────────────────────────────────────────

def test_decide_action_auto_resolution():
    """Urgence LOW + équipement connu + 0 ticket précédent → AUTO_RESOLUTION"""
    action = decide_action(
        message="Entretien annuel chaudière",
        urgency=Urgency.LOW,
        equipment_type="boiler",
        previous_tickets_count=0,
        confidence_score=0.9,
        missing_elements=[]
    )
    assert action == Action.AUTO_RESOLUTION


# ─── Autres branches pour compléter la couverture ────────────────────────────

def test_decide_action_escalate_low_confidence():
    """Score de confiance trop bas → ESCALATE_TO_HUMAN"""
    with patch("app.domain.rules_engine.orientation.settings") as mock_settings:
        mock_settings.confidence_threshold_escalate = 0.99

        action = decide_action(
            message="Problème inconnu",
            urgency=Urgency.LOW,
            equipment_type="boiler",
            previous_tickets_count=0,
            confidence_score=0.5,
            missing_elements=[]
        )
        assert action == Action.ESCALATE_TO_HUMAN


def test_decide_action_critical_urgency():
    """Urgence CRITICAL → SCHEDULE_INTERVENTION immédiat"""
    action = decide_action(
        message="Inondation majeure",
        urgency=Urgency.CRITICAL,
        equipment_type="faucet",
        previous_tickets_count=0,
        confidence_score=0.9,
        missing_elements=["equipment_model"]
    )
    assert action == Action.SCHEDULE_INTERVENTION


def test_decide_action_generate_quote():
    """Mot-clé remplacement détecté → GENERATE_QUOTE"""
    from app.shared.constants.keywords import KEYWORDS_REPLACEMENT
    keyword = next(iter(KEYWORDS_REPLACEMENT))

    action = decide_action(
        message=f"Je voudrais {keyword} ma chaudière",
        urgency=Urgency.LOW,
        equipment_type="boiler",
        previous_tickets_count=0,
        confidence_score=0.9,
        missing_elements=[]
    )
    assert action == Action.GENERATE_QUOTE


def test_decide_action_default_schedule_intervention():
    """Urgence LOW + équipement inconnu → SCHEDULE_INTERVENTION par défaut"""
    action = decide_action(
        message="Problème divers",
        urgency=Urgency.LOW,
        equipment_type="unknown_equipment",
        previous_tickets_count=0,
        confidence_score=0.9,
        missing_elements=[]
    )
    assert action == Action.SCHEDULE_INTERVENTION