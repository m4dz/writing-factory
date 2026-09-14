"""Countable style features and a composite score, for SELECTION among draws.

Doctrine 3: counting is not reading. This module does not judge prose; it
ranks variants that have already passed the defect scorers, so that among
N acceptable draws the one closest to the contract's countable marks wins
(sentence regime, concrete verbs, exact figures, inventory lines) and the one
that leans on the genre's furniture loses (physiology of the thriller, named
emotions, rhetorical questions, narrative "alors"). Higher is better.

Falsified both ways (doctrine 4, ``tests/unit/test_style_score.py``): every
reference excerpt of the style sheet outranks the drafts read aloud as
generic (the retained 2026-08-27 draw, the inner novel, the eight-header
chapter), the references' mean outranks the journal's, and the conforming
fixtures score high. A failed run whose failure was STRUCTURAL (no
accumulation, an English leak) may score well here: structure is the lint's,
this module reads register only, and it never overrides a defect score.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from factory.eval.lint import (ACC_COMMAS, ACC_WORDS, AI_TICS, MENTAL_STATES, PASTICHE,
                               normalize, outside_quotes, paragraphs, sentences,
                               strip_frontmatter, words)

# --- positive marks --------------------------------------------------------------

# Verbs of perception and of the trade: she looks, counts, checks, rereads,
# notes. Conjugated forms are matched by stem.
CONCRETE_VERBS = re.compile(
    r"\b(?:v(?:ois|oit|u|ue|us|ues|oyais|oyait|érifi\w*)|regard\w*|compt\w*|"
    r"reli\w*|relu\w*|not\w+|consign\w*|relev\w*|point\w+|touch\w*|"
    r"soul[eè]v\w*|rang\w+|ferm\w*|éteins|éteint\w*|allum\w*|pli\w*|pos\w+|"
    r"ouvr\w*|ouvert\w*|essui\w*|rinc\w*|entend\w*|sen[st]\w*)\b",
    re.IGNORECASE)

# Exact figures: hours, counts, ordinals, the words of quantity she uses.
FIGURES = re.compile(
    r"\b(?:\d{1,2}\s?h(?:\s?\d{2})?\b|\d+\b|"
    r"(?:une?|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|quinze|vingt|"
    r"trente|quarante|cinquante)\s+(?:heures?|fois|minutes?|secondes?|assiettes?|"
    r"couverts?|verres?|photos?|lignes?|pages?|jours?|ans)\b|"
    r"(?:sept|huit|neuf|dix|onze)\s+heures\b|midi|minuit|"
    r"(?:premi[eè]re?|deuxi[eè]me|troisi[eè]me|quatri[eè]me)\b|"
    r"\b(?:une seule|deux fois|trois fois)\b)",
    re.IGNORECASE)

# Inventory line: the object, a colon, the count or the state constated.
INVENTORY = re.compile(r"(?:^|(?<=[.!?…]\s))[^.!?\n:]{2,50}\s?:\s[^.!?\n]{1,80}[.!?]", re.MULTILINE)

# --- negative marks --------------------------------------------------------------

# The thriller's body: what the contract replaces with "les mains froides".
GENRE_PHYSIOLOGY = re.compile(
    r"\b(?:chamade|sueurs? froides?|glac[ée]e? le sang|flageol\w*|frisson\w*|"
    r"trembl\w*|palpit\w*|mon c[œo]eur|le c[œo]eur|souffle court|"
    r"boule (?:au|dans le) ventre|gorge (?:nou[ée]e|serr[ée]e)|n[œo]eud (?:à|dans) "
    r"l'estomac|les larmes|sanglot\w*|hurl\w*|cri\w*|estomac)\b",
    re.IGNORECASE)

# Named emotions: the contract says the body constates, the name is refused.
EMOTION_NOUNS = re.compile(
    r"\b(?:angoisse\w*|peur\w*|terreur\w*|panique\w*|inqui[ée]tude\w*|malaise\w*|"
    r"vertige\w*|effroi|horreur\w*|folle|fou|folie|perd(?:re|ais|ait|s|u) la t[êe]te|"
    r"d[ée]sespoir|soulag\w*|r[ée]confort\w*|nerveu\w+|anxi\w+|apais\w*)\b",
    re.IGNORECASE)

# Telling the strange instead of showing the thing.
TELLING = re.compile(
    r"\b(?:[ée]trange\w*|bizarre\w*|inexplicable\w*|incompr[ée]hensible\w*|"
    r"impossible|myst[ée]r\w+|surnaturel\w*|troublant\w*|inqui[ée]tant\w*|"
    r"comme si\b|comme pour\b|comme s'il\b)",
    re.IGNORECASE)

# Narrative surprise adverbs and the linking « alors » of the recounted evening.
SURPRISE = re.compile(
    r"\b(?:soudain\w*|brusquement|tout à coup|subitement|alors|et puis|puis)\b",
    re.IGNORECASE)

# The mind narrated: the genre's interior camera, where the contract wants
# the object and the hand.
MENTAL_NARRATION = re.compile(
    r"\b(?:mon regard|mes yeux|sous mes yeux|dans mon esprit|mon esprit|ma raison|"
    r"mes pens[ée]es|le doute (?:qui|s')|m'obs[èe]de|me hante|solitaire|s'immisc\w*|"
    r"envahi\w*|submerg\w*|assaill\w*|sans fin|me joue des tours|"
    r"je ne comprends pas comment|je me souviens (?:encore|parfaitement|très bien|soudain))\b",
    re.IGNORECASE)

QUESTION = re.compile(r"\?")
STRAIGHT_QUOTES = re.compile(r'"[^"\n]{15,400}"')


def _is_accumulation(sentence: str) -> bool:
    """The contract's one long sentence per entry: exempt from the length regime."""
    return words(sentence) >= ACC_WORDS and sentence.count(",") >= ACC_COMMAS


def body(text: str) -> str:
    """The prose to score: frontmatter stripped, quotations blanked, stage
    markers removed, journal header (when present) dropped."""
    text = normalize(strip_frontmatter(text))
    # A journal file: header block, then a second frontmatter, then the run.
    if text.startswith("<!--"):
        parts = text.split("\n---\n")
        text = parts[-1] if len(parts) > 1 else text
        text = strip_frontmatter(text.strip())
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"^#+ .*$", "", text, flags=re.MULTILINE)
    text = STRAIGHT_QUOTES.sub(lambda m: " " * len(m.group(0)), text)
    return outside_quotes(text)


def features(text: str) -> dict:
    """Every countable mark, per 100 words where it is a count."""
    t = body(text)
    ss = [s for s in sentences(t) if words(s) > 0]
    n_words = sum(words(s) for s in ss) or 1
    per100 = 100.0 / n_words
    # The accumulation is the contract's own long sentence: outside the regime.
    lengths = [words(s) for s in ss if not _is_accumulation(s)]
    n = len(lengths) or 1
    paras = paragraphs(t)
    closing_cleavers = sum(1 for p in paras
                           if (ph := sentences(p)) and 3 <= words(ph[-1]) <= 6)
    return {
        "words": n_words,
        "sentences": len(ss),
        "mean_length": round(sum(lengths) / n, 1),
        "short_share": round(sum(1 for w in lengths if 3 <= w <= 16) / n, 2),
        "long_share": round(sum(1 for w in lengths if w > 25) / n, 2),
        "closing_cleavers": closing_cleavers,
        "concrete_verbs": round(len(CONCRETE_VERBS.findall(t)) * per100, 2),
        "figures": round(len(FIGURES.findall(t)) * per100, 2),
        "inventory_lines": len(INVENTORY.findall(t)),
        "genre_physiology": round(len(GENRE_PHYSIOLOGY.findall(t)) * per100, 2),
        "emotion_nouns": round(len(EMOTION_NOUNS.findall(t)) * per100, 2),
        "telling": round(len(TELLING.findall(t)) * per100, 2),
        "surprise": round(len(SURPRISE.findall(t)) * per100, 2),
        "questions": round(len(QUESTION.findall(t)) * per100, 2),
        "mental_states": round(len(MENTAL_STATES.findall(t)) * per100, 2),
        "mental_narration": round(len(MENTAL_NARRATION.findall(t)) * per100, 2),
        "tics": len(AI_TICS.findall(t)) + len(PASTICHE.findall(t)),
    }


# Weights: one composite, kept simple and legible. Positive marks are capped
# so that a litany of figures cannot buy back a genre body.
WEIGHTS = (
    ("short_share", 6.0, 1.0),
    ("concrete_verbs", 1.0, 5.0),
    ("figures", 1.0, 4.0),
    ("inventory_lines", 1.0, 3.0),
    ("closing_cleavers", 0.5, 3.0),
    ("long_share", -8.0, 1.0),
    ("genre_physiology", -3.0, 99.0),
    ("emotion_nouns", -3.0, 99.0),
    ("telling", -2.0, 99.0),
    ("surprise", -1.5, 99.0),
    ("questions", -1.5, 99.0),
    ("mental_states", -3.0, 99.0),
    ("mental_narration", -2.0, 99.0),
    ("tics", -3.0, 99.0),
)


def score(text: str) -> float:
    """The composite, higher is better. Zero is a text with no mark either way."""
    f = features(text)
    total = 0.0
    for key, weight, cap in WEIGHTS:
        total += weight * min(float(f[key]), cap)
    return round(total, 2)


def report(text: str, title: str = "") -> str:
    f = features(text)
    lines = [f"### {title}" if title else "### style", f"score : {score(text)}", ""]
    lines += [f"- {k} : {v}" for k, v in f.items()]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="factory eval style",
                                     description="Marques de style comptables d'un texte "
                                                 "(sélection, jamais jugement).")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    for path in args.files:
        p = Path(path)
        print(report(p.read_text(encoding="utf-8"), title=p.name))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
