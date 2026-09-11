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
