import re


def normalize_text(text: str) -> str:
    """Normalise le texte pour la recherche de mots-clés."""
    text = text.lower()
    # Accents
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ô': 'o', 'ö': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    
    # Remplacer ponctuation par des espaces pour isoler les mots
    text = re.sub(r'[^a-z0-9]', ' ', text)
    # Nettoyer les espaces doubles
    text = ' '.join(text.split())
    return text


def count_keywords(text: str, keywords: list[str]) -> int:
    """Compte les occurrences de mots-clés dans un texte normalisé."""
    normalized = f" {normalize_text(text)} "
    count = 0
    for kw in keywords:
        kw_norm = normalize_text(kw)
        if f" {kw_norm} " in normalized:
            count += 1
    return count
