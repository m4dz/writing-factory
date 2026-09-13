#!/usr/bin/env python3
"""French style lint, LOCAL, no cloud dependency.

Role: the French guard (prompt instruction) plus a deterministic post-filter
for the language leaks and corrupted tokens the model lets through.

This module is the intended anchor for the `style-writing-guide-FR` ruleset:
today a minimal franglais map plus detectors; later the guide's rules (banned
words, clichés, register) extend it. It stays LOCAL: the project's thesis,
the factory never leaves the machine.
"""

import re

# Anti-code-switching system instruction; single source (factory.infra.ollama).
FRENCH_GUARD = (
    "IMPÉRATIF ABSOLU : tu écris EXCLUSIVEMENT en français. Aucun mot, "
    "aucune expression dans une autre langue, jamais, même par accident."
)

# Safe 1:1 franglais replacements: words nemo leaks recurrently (« suddenly »
# first). Deterministic, instant replacement.
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

# Isolated English words to FLAG (auto-replacement unsafe in context).
_SUSPECT_EN = re.compile(
    r"\b(the|and|with|of|from|which|before|after|dread|reveals?|"
    r"revealing|whisper(?:ed|s)?)\b",
    re.I,
)

# Corrupted tokens like « nousWantons »: a lowercase letter (ASCII or accented)
# followed by an ASCII uppercase mid-word (token mash-up).
# NB: the uppercase is bounded to A-Z (ASCII) so that accented lowercase
# letters (é, è, à...) are NOT taken for capitals; the Unicode range « À-Ÿ »
# swallows lowercase accents.
_GARBAGE = re.compile(r"\b\w*[a-zà-ÿ][A-Z]\w*\b")


# French sentence end. The closing guillemet may follow the punctuation AFTER
# a space, French typography (« Va-t'en. » rather than « Va-t'en.»); forgetting
# it classed a correctly closed dialogue as a sentence in progress.
_SENTENCE_END = re.compile(r"[.!?…](?:\s*[»\"'])?\s*$")
_FINAL_PUNCTUATION = re.compile(r"[.!?…](?:\s*[»\"'])?(?=\s|$)")


def sentence_ends(text: str) -> list[int]:
    """Positions (exclusive end) of every complete sentence in the text.

    Used to place the switch marker and to bound the audio excerpt. Same
    detection as `trim_to_sentence`: one definition of "sentence end" in the
    project, or the marker and the cut would not fall at the same places.
    """
    return [m.end() for m in _FINAL_PUNCTUATION.finditer(text)]


def ends_mid_sentence(text: str) -> bool:
    """True when the text stops mid-sentence.

    Signature of a generation cut by `num_predict`: Ollama returns the text
    as is, with no marker other than `done_reason: "length"`.
    """
    return not _SENTENCE_END.search(text.rstrip())


def trim_to_sentence(text: str) -> str:
    """Cut at the last complete sentence: the net of last resort.

    Used only when a continuation was not enough: a scene ending a little
    early beats a word cut in two. The text is returned UNCHANGED when the cut
    would remove more than a quarter of it (pathological case of a passage
    with no final punctuation): this net must never destroy more than it
    repairs.
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
    """Clean the 1:1 leaks and return (corrected_text, warnings).

    The warnings list what the deterministic filter cannot fix alone
    (residual English words, corrupted tokens): the signal for the nemo style
    pass, or for the human.
    """
    warnings: list[str] = []
    for pattern, repl in _FRANGLAIS.items():
        text = re.sub(pattern, repl, text)

    # Glued « j'aiallumé »: « j'ai » welded to its participle, all lowercase,
    # invisible to `_GARBAGE` (which looks for an ASCII capital). Split against
    # a list of participles: safe, no collision with « j'aime » / « j'aie ».
    # Recurrent in the accumulation (« j'ai X, j'ai Y »).
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
