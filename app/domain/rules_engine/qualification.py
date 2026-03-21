"""
Règles de qualification du ticket.
Détermine la catégorie et l'urgence en fonction du contenu.
"""
from app.domain.types.enums import Category, Urgency
from app.shared.constants.keywords import (
    KEYWORDS_HEATING, KEYWORDS_PLUMBING, KEYWORDS_ELECTRICAL,
    KEYWORDS_VENTILATION, KEYWORDS_HIGH_URGENCY,
    KEYWORDS_MEDIUM_URGENCY,
)
from app.shared.constants.equipment import EQUIPMENT_CATEGORY_MAP
from app.shared.utils.text import count_keywords
    

def qualify_ticket(message: str, equipment_type: str | None) -> dict:
    """
    Qualifie un ticket en détectant sa catégorie et son urgence.
    """
    # On analyse les mots-clés sur le message uniquement pour détecter les incohérences
    scores = {
        Category.HEATING: count_keywords(message, KEYWORDS_HEATING),
        Category.PLUMBING: count_keywords(message, KEYWORDS_PLUMBING),
        Category.ELECTRICAL: count_keywords(message, KEYWORDS_ELECTRICAL),
        Category.VENTILATION: count_keywords(message, KEYWORDS_VENTILATION),
    }

    eq_type = (equipment_type or "").lower()
    mapped_cat_val = EQUIPMENT_CATEGORY_MAP.get(eq_type)
    
    # Détection de la catégorie suggérée par les mots-clés
    best = max(scores, key=lambda c: scores[c])
    best_keyword_cat = best if scores[best] > 0 else Category.OTHER
    
    if mapped_cat_val:
        category = Category(mapped_cat_val)
        # Incohérent si les mots-clés pointent vers une AUTRE catégorie que celle de l'équipement
        is_consistent = (category == best_keyword_cat or best_keyword_cat == Category.OTHER)
    else:
        category = best_keyword_cat
        is_consistent = True

    # L'urgence peut dépendre du message ou de l'équipement
    full_text = f"{message} {equipment_type or ''}"
    high_count = count_keywords(full_text, KEYWORDS_HIGH_URGENCY)
    medium_count = count_keywords(full_text, KEYWORDS_MEDIUM_URGENCY)

    if high_count >= 1:
        urgency = Urgency.HIGH
    elif medium_count >= 1:
        urgency = Urgency.MEDIUM
    else:
        urgency = Urgency.LOW

    # Calcul du ratio pour le score (pondération plus juste)
    total_keywords = max(len(KEYWORDS_HEATING), len(KEYWORDS_PLUMBING), len(KEYWORDS_ELECTRICAL), len(KEYWORDS_VENTILATION))
    best_score = max(scores.values()) if scores else 0
    keyword_match_ratio = min(best_score / max(total_keywords * 0.2, 1), 1.0)

    return {
        "category": category,
        "urgency": urgency,
        "is_consistent": is_consistent,
        "keyword_match_ratio": keyword_match_ratio
    }
