"""
Règles de complétude du ticket.
Vérifie si toutes les informations nécessaires sont présentes.
"""
from app.shared.constants.equipment import EQUIPMENT_CATEGORY_MAP


def has_exploitable_attachment(attachments: list[dict]) -> bool:
    """
    Détermine si au moins une pièce jointe est exploitable.
    Une photo ou vidéo avec description non vide est considérée exploitable.
    """
    if not attachments:
        return False
    exploitable_types = {"photo", "video", "image", "document", "pdf"}
    for att in attachments:
        att_type = (att.get("type") or "").lower()
        description = (att.get("description") or "").strip()
        if att_type in exploitable_types and len(description) > 5:
            return True
    return False


def check_completeness(
    message: str,
    equipment_model: str | None,
    equipment_type: str | None,
    attachments: list[dict]
) -> list[str]:
    """
    Vérifie les éléments manquants d'un ticket.
    
    Returns:
        list[str]: liste des codes d'éléments manquants.
    """
    missing: list[str] = []

    if not equipment_model:
        missing.append("equipment_model")

    if not has_exploitable_attachment(attachments):
        missing.append("clear_photo")

    if len((message or "").strip()) < 10:
        missing.append("detailed_message")

    return missing
