#!/usr/bin/env python3
"""Lint de style FR — LOCAL, pas de dépendance cloud.

Rôle : garde française (consigne prompt) + post-filtre déterministe des
fuites de langue et tokens corrompus que le modèle laisse passer.

Ce module est le point d'ancrage prévu pour le ruleset `style-writing-guide-FR` :
aujourd'hui une map franglais minimale + détecteurs ; demain, les règles du
guide (mots bannis, clichés, registre) viennent l'enrichir. Il reste LOCAL —
c'est la thèse du projet, la fabrique ne sort jamais de la machine.
"""

import re

# Consigne système anti-code-switching. Source unique (importée par llm.py).
FRENCH_GUARD = (
    "IMPÉRATIF ABSOLU : tu écris EXCLUSIVEMENT en français. Aucun mot, "
    "aucune expression dans une autre langue, jamais, même par accident."
)

# Remplacements franglais 1:1 sûrs — mots que nemo laisse fuir de façon
# récurrente (« suddenly » en tête). Remplacement déterministe, instantané.
_FRANGLAIS = {
    r"\bSuddenly\b": "Soudain",
    r"\bsuddenly\b": "soudain",
    r"\bSlowly\b": "Lentement",
    r"\bslowly\b": "lentement",
    r"\bThen\b": "Puis",
    r"\bthen\b": "alors",
    r"\bhowever\b": "cependant",
    r"\bindeed\b": "en effet",
}

# Mots anglais isolés à SIGNALER (remplacement auto non sûr en contexte).
_SUSPECT_EN = re.compile(
    r"\b(the|and|with|of|from|which|before|after|dread|reveals?|"
    r"revealing|whisper(?:ed|s)?)\b",
    re.I,
)

# Tokens corrompus type « nousWantons » : minuscule (ASCII ou accentuée)
# suivie d'une majuscule ASCII en milieu de mot (mash-up de tokens).
# NB : la majuscule est bornée à A-Z (ASCII) pour ne PAS confondre les
# minuscules accentuées (é, è, à...) avec des capitales — piège des plages
# Unicode où « À-Ÿ » englobe les accents minuscules.
_GARBAGE = re.compile(r"\b\w*[a-zà-ÿ][A-Z]\w*\b")


def delint(text: str) -> tuple[str, list[str]]:
    """Nettoie les fuites 1:1 et retourne (texte_corrigé, avertissements).

    Les avertissements listent ce que le filtre déterministe ne peut pas
    corriger seul (mots anglais résiduels, tokens corrompus) : c'est le signal
    pour la passe stylistique nemo, ou pour l'humain.
    """
    warnings: list[str] = []
    for pattern, repl in _FRANGLAIS.items():
        text = re.sub(pattern, repl, text)

    residual = sorted({m.group(0) for m in _SUSPECT_EN.finditer(text)})
    if residual:
        warnings.append(f"anglais résiduel : {residual}")

    garbage = sorted({m.group(0) for m in _GARBAGE.finditer(text)})
    if garbage:
        warnings.append(f"tokens corrompus : {garbage}")

    return text, warnings
