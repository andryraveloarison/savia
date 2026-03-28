"""
Moteur de calcul du confidence_score.
Score entre 0.0 et 1.0 basé sur des critères pondérés.
"""
from app.shared.constants.scoring import (
    WEIGHT_KEYWORD_MATCH,
    WEIGHT_EQUIPMENT_KNOWN,
    WEIGHT_HISTORY,
    WEIGHT_COMPLETENESS,
    WEIGHT_ATTACHMENT,
)
from app.shared.constants.equipment import EQUIPMENT_CATEGORY_MAP


def compute_confidence_score(
    keyword_match_ratio: float,       # 0.0–1.0 : richesse correspondance mots-clés
    equipment_type: str | None,       # type d'équipement fourni
    previous_tickets: int,            # nombre de tickets précédents
    missing_elements: list[str],      # éléments manquants détectés
    has_useful_attachment: bool,      # pièce jointe exploitable
) -> float:
    """
    Calcule un score de confiance pondéré.

    Returns:
        float: score entre 0.0 et 1.0 (arrondi à 2 décimales)
    """
    score = 0.0

    # 1. Correspondance mots-clés (qualité de la qualification)
    score += WEIGHT_KEYWORD_MATCH * min(keyword_match_ratio, 1.0)

    # 2. Équipement identifiable dans le dictionnaire métier
    equipment_known = (
        equipment_type is not None
        and equipment_type.lower() in EQUIPMENT_CATEGORY_MAP
    )
    score += WEIGHT_EQUIPMENT_KNOWN * (1.0 if equipment_known else 0.0)

    # 3. Historique client (connaissance du client)
    history_score = min(previous_tickets / 5.0, 1.0)  # max à 5 tickets
    score += WEIGHT_HISTORY * history_score

    # 4. Complétude du ticket
    completeness_score = max(0.0, 1.0 - len(missing_elements) * 0.25)
    score += WEIGHT_COMPLETENESS * completeness_score

    # 5. Pièce jointe exploitable
    score += WEIGHT_ATTACHMENT * (1.0 if has_useful_attachment else 0.0)

    return round(min(score, 1.0), 2)
