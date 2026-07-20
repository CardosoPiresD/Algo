"""Validation des sorties IA + vérification de citation verbatim.

Anti-hallucination MÉCANIQUE (design v2 §3.1) : tout verdict de l'IA qui cite
un passage du document source doit contenir un extrait réellement présent dans
la source (comparaison par sous-chaîne, texte normalisé). Pas de correspondance
=> verdict ignoré. C'est vérifié, pas déclaré.
"""

import re
import unicodedata


def normalize(text: str) -> str:
    """Normalisation Unicode + espaces pour la comparaison de sous-chaîne."""
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def citation_is_verbatim(excerpt: str, source_text: str, min_len: int = 12) -> bool:
    """True si `excerpt` (normalisé) est une sous-chaîne de `source_text`.

    Un extrait trop court (< min_len caractères normalisés) est refusé : il ne
    prouve rien (« the », « risk »… matcheraient partout).
    """
    ex = normalize(excerpt)
    if len(ex) < min_len:
        return False
    return ex in normalize(source_text)


def validate_keys(data: dict, required: dict) -> tuple[bool, str]:
    """Vérifie présence des clés et appartenance aux énumérations.

    required : {clé: None} pour "présent", {clé: {"a","b"}} pour énum autorisée.
    """
    if not isinstance(data, dict):
        return False, "sortie non-dict"
    for key, allowed in required.items():
        if key not in data:
            return False, f"clé manquante: {key}"
        if allowed is not None and data[key] not in allowed:
            return False, f"valeur hors énumération pour {key}: {data[key]!r}"
    return True, "ok"
