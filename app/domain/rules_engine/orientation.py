"""
Règles d'orientation.
Décide de l'action à entreprendre en fonction de la situation.
"""
from app.domain.types.enums import Action, Urgency
from app.shared.constants.equipment import EQUIPMENT_CATEGORY_MAP
from app.shared.constants.keywords import KEYWORDS_REPLACEMENT

from app.core.config import get_settings

settings = get_settings()


def decide_action(
    message: str,
    urgency: Urgency,
    equipment_type: str | None,
    previous_tickets_count: int,
    confidence_score: float,
    missing_elements: list[str]
) -> Action:
    """
    Sélectionne l'action recommandée pour le ticket.
    """
    # 1. Alerte de confiance (besoin d'un humain quoi qu'il arrive)
    if confidence_score < settings.confidence_threshold_escalate:
        return Action.ESCALATE_TO_HUMAN

    # 2. Priorité absolue aux urgences critiques ou hautes (danger/inondation...)
    # On planifie immédiatement même si des infos non-critiques manquent
    if urgency in (Urgency.HIGH, Urgency.CRITICAL):
        return Action.SCHEDULE_INTERVENTION

    # 3. Demande d'infos si incomplet (critique) pour urgence moyenne ou basse
    # Le modèle est considéré critique, la photo est optionnelle pour l'orientation
    critical_missing = {m for m in missing_elements} - {"clear_photo"}
    if critical_missing:
        return Action.REQUEST_ADDITIONAL_INFO

    # 4. Pour une urgence moyenne complète, on peut planifier
    if urgency == Urgency.MEDIUM:
        return Action.SCHEDULE_INTERVENTION

    # 5. Détection de besoin de devis (remplacement/installation)
    message_lower = message.lower()
    if any(kw in message_lower for kw in KEYWORDS_REPLACEMENT):
        return Action.GENERATE_QUOTE

    # 6. Tentative de résolution automatique (basse urgence, connu, complet)
    eq_type = (equipment_type or "").lower()
    equipment_known = eq_type in EQUIPMENT_CATEGORY_MAP
    
    if (urgency == Urgency.LOW and equipment_known 
        and previous_tickets_count == 0):
        return Action.AUTO_RESOLUTION

    # Par défaut, intervention
    return Action.SCHEDULE_INTERVENTION
