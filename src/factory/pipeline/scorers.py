"""Reading criteria for best-of-N selection — a registry keyed by name.

A scorer is deterministic and falsifiable (doctrine 3: counting is not
reading, so we do not grade prose; we REJECT named defects that repeated
draws made recurrent). The mechanism lives here; a criterion's lexical lists
live in the chapter spec (``best_of.names`` / ``best_of.drift``) and reach the
scorer through the ``BestOf`` object. Higher is better.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from factory.chapter_spec.model import BestOf

Scorer = Callable[[str, BestOf], tuple[int, list[str]]]


def _terms(terms: tuple[str, ...]) -> re.Pattern | None:
    if not terms:
        return None
    alts = "|".join(re.escape(t.strip()).replace(r"\ ", r"\s+") for t in terms)
    return re.compile(rf"\b(?:{alts})\b", re.IGNORECASE)


def names_erasure(variant: str, criterion: BestOf) -> tuple[int, list[str]]:
    """The served text must NAME the listed terms (the erasure of the day) and
    not drift towards the listed drift phrases (a generic tidying-up)."""
    defects: list[str] = []
    score = 0
    names, drift = _terms(criterion.names), _terms(criterion.drift)
    if names and names.search(variant):
        score += 3
    else:
        score -= 3
        defects.append("ne nomme pas l'effacement de l'anniversaire")
    if drift and drift.search(variant):
        score -= 5
        defects.append("dérive (cahier / grenier / album)")
    return score, defects


# The notebook's grammar, true of every entry whatever its criterion.
# The elided forms end on the apostrophe: a word character follows (« j'ai »),
# so they take no right boundary. Until 2026-11-10 they had one and never
# matched; a beat written in the first person only through « j' » / « m' »
# could be counted as third person.
FIRST_PERSON = re.compile(r"(?<!\w)(?:(?:je|me|moi|mon|ma|mes)(?!\w)|[jm]['’])",
                          re.IGNORECASE)
SHE = re.compile(r"\belle\b", re.IGNORECASE)
# « Elle » opening a sentence (after a stray rule, emphasis or quotation mark).
_SHE_OPENS = re.compile(r"(?:^[\s*_\-«\"“]*|[.!?…»”\"]\s+)Elle\s", re.MULTILINE)
# A quotation: one opening the entry (after a stray rule or emphasis), or any
# quoted span of five words or more. Short quoted words (« oui ») stay legal.
_OPENS_QUOTED = re.compile(r"^[\s*_\-]*[«\"“]")
_QUOTED_SPAN = re.compile(r"[«\"“]([^»\"”]+)[»\"”]")


def notebook(variant: str, *, cites: bool) -> tuple[int, list[str]]:
    """Defects of the notebook itself, added to any criterion's score.

    THIRD PERSON: the entry transposes its served matter, written with
    « elle », instead of writing as the narrator. No first-person mark, and
    either two « elle » (the beats' rule) or a sentence opening on « Elle »:
    bounded to two sentences, a transposed entry may carry a single one
    (« --- Elle a effacé l'anniversaire… »). « elle » next to a « je » is
    Romane (« les photos d'elle »). QUOTATION: an entry without an anchor (`cites`
    false, entry 1 of chapter 7) does not quote; the models open it with an
    invented quotation in a third of the retained runs, nemo included
    (xp-author-models-2, 2026-11-10). Both are vetoes of the brief.
    """
    defects: list[str] = []
    score = 0
    if not FIRST_PERSON.search(variant) and (len(SHE.findall(variant)) >= 2
                                              or _SHE_OPENS.search(variant)):
        score -= 10
        defects.append("troisième personne (la matière transposée)")
    if not cites and (_OPENS_QUOTED.match(variant)
                      or any(len(q.split()) >= 5 for q in _QUOTED_SPAN.findall(variant))):
        score -= 10
        defects.append("cite (l'entrée ne porte pas de citation)")
    return score, defects


def none(variant: str, criterion: BestOf) -> tuple[int, list[str]]:
    """No criterion: every variant scores 0, the first draw wins (stable)."""
    return 0, []


SCORERS: dict[str, Scorer] = {"": none, "none": none, "names-erasure": names_erasure}


def score(variant: str, criterion: BestOf | None) -> tuple[int, list[str]]:
    if criterion is None:
        return none(variant, BestOf(1))
    try:
        return SCORERS[criterion.criterion](variant, criterion)
    except KeyError:
        raise KeyError(f"critère de sélection inconnu : {criterion.criterion!r} "
                       f"(connus : {sorted(k for k in SCORERS if k)})") from None
