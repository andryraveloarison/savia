import pytest
from app.domain.rules_engine.completeness import check_completeness, has_exploitable_attachment

# ─── Tests has_exploitable_attachment ────────────────────────────────────────────────
def test_has_exploitable_attachment_empty():
    assert has_exploitable_attachment([]) is False


def test_has_exploitable_attachment_valid_photo():
    assert has_exploitable_attachment([{"type": "photo", "description": "une fuite sous l evier"}]) is True


def test_has_exploitable_attachment_pdf_empty_description():
    assert has_exploitable_attachment([{"type": "pdf", "description": "  "}]) is False


def test_has_exploitable_attachment_short_description():
    """Description trop courte (<=5 chars) → non exploitable"""
    assert has_exploitable_attachment([{"type": "photo", "description": "ok"}]) is False


def test_has_exploitable_attachment_video():
    assert has_exploitable_attachment([{"type": "video", "description": "fuite visible sous evier"}]) is True


def test_has_exploitable_attachment_none_values():
    """Valeurs None dans type/description → ne plante pas"""
    assert has_exploitable_attachment([{"type": None, "description": None}]) is False


# ─── Tests check_completeness ────────────────────────────────────────────────
def test_check_completeness_all_missing():
    """Message trop court, pas de modèle, pas de type, pas de photo"""
    missing = check_completeness("Aider", None, None, [])
    assert "equipment_model" in missing
    assert "equipment_type" in missing   
    assert "clear_photo" in missing
    assert "detailed_message" in missing


def test_check_completeness_equipment_type_missing():
    """equipment_type est None → ajout de 'equipment_type'"""
    missing = check_completeness(
        message="Ma chaudière ne fonctionne plus du tout",
        equipment_model="Viessmann 200",
        equipment_type=None,
        attachments=[]
    )
    assert "equipment_type" in missing
    assert "equipment_model" not in missing


def test_check_completeness_only_model_missing():
    missing = check_completeness("Ma chaudière ne fonctionne plus du tout", None, "boiler", [])
    assert "equipment_model" in missing
    assert "equipment_type" not in missing
    assert "clear_photo" in missing
    assert "detailed_message" not in missing


def test_check_completeness_complete():
    """Ticket complet → aucun élément manquant"""
    missing = check_completeness(
        message="Ma chaudière ne fonctionne plus depuis ce matin",
        equipment_model="Viessmann 200",
        equipment_type="boiler",
        attachments=[{"type": "photo", "description": "photo de la chaudière en panne"}]
    )
    assert missing == []


def test_check_completeness_message_none():
    """Message None → ne plante pas et détecte detailed_message manquant"""
    missing = check_completeness(None, "Viessmann", "boiler", [])
    assert "detailed_message" in missing