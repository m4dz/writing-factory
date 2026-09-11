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


# Fin de phrase française. Le guillemet fermant peut suivre la ponctuation
# APRÈS une espace — c'est la typographie française (« Va-t'en. » et non
# « Va-t'en.»), et l'oublier faisait classer un dialogue correctement terminé
# comme une phrase en cours.
_SENTENCE_END = re.compile(r"[.!?…](?:\s*[»\"'])?\s*$")
_FINAL_PUNCTUATION = re.compile(r"[.!?…](?:\s*[»\"'])?(?=\s|$)")


def sentence_ends(text: str) -> list[int]:
    """Positions (fin exclusive) de chaque phrase complète du texte.

    Sert au placement du marqueur de bascule et au bornage de l'extrait audio.
    Même détection que `trim_to_sentence` — une seule définition de « fin de
    phrase » dans le projet, sinon le marqueur et la coupe ne tomberaient pas
    aux mêmes endroits.
    """
    return [m.end() for m in _FINAL_PUNCTUATION.finditer(text)]


def ends_mid_sentence(text: str) -> bool:
    """Vrai si le texte s'arrête en plein milieu d'une phrase.

    Signature d'une génération coupée par `num_predict` : Ollama rend le texte
    tel quel, sans marqueur autre que `done_reason: "length"`.
    """
    return not _SENTENCE_END.search(text.rstrip())


def trim_to_sentence(text: str) -> str:
    """Coupe à la dernière phrase complète — filet de dernier recours.

    Utilisé seulement quand une continuation n'a pas suffi : mieux vaut une
    scène qui s'arrête un peu tôt qu'un mot coupé en deux. Le texte est rendu
    INCHANGÉ si la coupe emporterait plus d'un quart du texte (cas pathologique
    d'un passage sans aucune ponctuation finale) : ce filet ne doit jamais
    détruire plus qu'il ne répare.
    """
    t = text.rstrip()
    if not ends_mid_sentence(t):
        return t
    ends = list(_FINAL_PUNCTUATION.finditer(t))
    if not ends:
        return text
    cut = t[: ends[-1].end()].rstrip()
    return cut if len(cut) >= 0.75 * len(t) else text


def delint(text: str) -> tuple[str, list[str]]:
    """Nettoie les fuites 1:1 et retourne (texte_corrigé, avertissements).

    Les avertissements listent ce que le filtre déterministe ne peut pas
    corriger seul (mots anglais résiduels, tokens corrompus) : c'est le signal
    pour la passe stylistique nemo, ou pour l'humain.
    """
    warnings: list[str] = []
    for pattern, repl in _FRANGLAIS.items():
        text = re.sub(pattern, repl, text)

    # Collage « j'aiallumé » : « j'ai » soudé à son participe, tout en
    # minuscules — invisible pour `_GARBAGE` (qui cherche une majuscule ASCII).
    # On sépare sur une liste de participes : sûr, aucune collision avec
    # « j'aime » / « j'aie ». Récurrent dans l'accumulation (« j'ai X, j'ai Y »).
    text = re.sub(
        r"\bj'ai(allumé|éteint|mangé|sorti|mis|ouvert|regardé|préparé|rangé"
        r"|débarrassé|fait|pris|accroché|enlevé|commencé|essuyé|vérifié|dansé"
        r"|coupé|marché|monté|bu|nettoyé|lavé|posé|trouvé|écrit|cherché)",
        r"j'ai \1", text)

    residual = sorted({m.group(0) for m in _SUSPECT_EN.finditer(text)})
    if residual:
        warnings.append(f"anglais résiduel : {residual}")

    garbage = sorted({m.group(0) for m in _GARBAGE.finditer(text)})
    if garbage:
        warnings.append(f"tokens corrompus : {garbage}")

    return text, warnings
