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
    # Either apostrophe: the spec types « ' », the models write « ’ ».
    alts = "|".join(re.escape(t.strip()).replace(r"\ ", r"\s+").replace("'", "['’]")
                    for t in terms)
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
    # The decision is the entry's first half, as the brief writes it: 4 draws
    # in 24 kept it in the two served sentences without quotation marks, and
    # the selection had no reason to prefer them (entry1-decision). Absent
    # list, no check.
    decision = _terms(criterion.decision)
    if decision and not decision.search(variant):
        score -= 4
        defects.append("ne pose pas la décision")
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


def notebook(variant: str, *, cites: bool, day_word: str = "") -> tuple[int, list[str]]:
    """Defects of the notebook itself, added to any criterion's score.

    THIRD PERSON: the entry transposes its served matter, written with
    « elle », instead of writing as the narrator. No first-person mark, and
    either two « elle » (the beats' rule) or a sentence opening on « Elle »:
    bounded to two sentences, a transposed entry may carry a single one
    (« --- Elle a effacé l'anniversaire… »). « elle » next to a « je » is
    Romane (« les photos d'elle »). QUOTATION: an entry without an anchor (`cites`
    false, entry 1 of chapter 7) does not quote; the models open it with an
    invented quotation in a third of the retained runs, nemo included
    (xp-author-models-2, 2026-11-10). Both are vetoes of the brief. DAY'S
    WORD: an entry whose verdict is absent does not write the chapter's
    verdict word (`day_word`, « anniversaire »): the fall owns it.
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
    if day_word.strip() and re.search(rf"\b{re.escape(day_word.strip())}\b", variant,
                                      re.IGNORECASE):
        score -= 5
        defects.append(f"écrit le mot du jour (« {day_word.strip()} »)")
    return score, defects


_CLOSES_QUOTED = re.compile(r"[»\"”]")
_SECOND_PERSON = re.compile(r"(?<!\w)(?:(?:tu|te|toi|ton|ta|tes)(?!\w)|t['’])",
                            re.IGNORECASE)
_SENTENCE_CLOSED = re.compile(r"[.!?…]$")


def unquote_own_line(variant: str) -> str:
    """Remove the quotation marks around the notebook's own opening line.

    An entry without an anchor still opens, in 9 draws out of 24, on
    « « J'ai décidé … » »: the narrator's own line in the anchor's dress, and
    in 7 of them the decision the brief asks for (entry1-decision). The code
    owns the quotation marks of an entry that does not cite; the line is
    kept, its dress removed — as the stray header is. Only a line that is
    hers: first person, nobody addressed (« tu » is a voice, and the entry
    has none), closed on a sentence end (« "…", disait-elle » is a quotation
    with an attribution). Anything else is left to `notebook`, which rejects
    it. Emphasis inside the line goes with the marks.
    """
    m = _OPENS_QUOTED.match(variant)
    if not m:
        return variant
    rest = variant[m.end():]
    close = _CLOSES_QUOTED.search(rest)
    inner = (rest[:close.start()] if close else rest).replace("*", "").strip()
    tail = rest[close.end():].lstrip(" *_") if close else ""
    if (not FIRST_PERSON.search(inner) or _SECOND_PERSON.search(inner)
            or (close and not _SENTENCE_CLOSED.search(inner))):
        return variant
    return f"{inner} {tail}".strip()


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
