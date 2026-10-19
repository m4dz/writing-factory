"""The resolution check against the owner's verdicts (doctrine 4).

The 12 bare draws of experiment C5 all held the doubt by the owner's reading;
the check must flag none of them. The resolutions documented in the journal
digest must stay flagged. The draws are read from the journal itself, not
copied, so the test cannot drift from the record.
"""

import re

import pytest

from factory import paths
from factory.pipeline import graph

C5_JOURNAL = paths.EXPERIMENTS_DIR / "journal" / "20260831T162633-xp-resolution-C5.md"


def c5_draws() -> list[tuple[str, str]]:
    text = C5_JOURNAL.read_text(encoding="utf-8").split("## Verbatims", 1)[1]
    blocks = re.split(r"^\*\*(.+?)\*\*\s*$", text, flags=re.MULTILINE)[1:]
    draws = []
    for title, body in zip(blocks[::2], blocks[1::2]):
        quote = " ".join(line[1:].strip() for line in body.splitlines()
                         if line.startswith(">"))
        draws.append((title.strip(), quote))
    return draws


def test_corpus_is_the_twelve_draws():
    draws = c5_draws()
    assert len(draws) == 12
    assert all(len(q) > 200 for _, q in draws)


@pytest.mark.parametrize("title,draw", c5_draws(), ids=[t for t, _ in c5_draws()])
def test_held_draws_are_not_flagged(title, draw):
    assert not graph._BEAT_RESOLVES.search(draw), title


def test_the_former_false_positive_is_in_the_corpus():
    assert any("Je me souviens parfaitement de ma soirée de la veille" in q
               for _, q in c5_draws())


@pytest.mark.parametrize("resolving", [
    "Verdict : coquille. Ma mémoire m'a joué un tour. Je n'ai pas rêvé.",
    "Et puis je me souviens soudain : cela me revient maintenant, la table, les assiettes.",
    "Je me souviens parfaitement avoir mis les deux couverts avant le dîner.",
    "Je me souviens bien de les avoir posés là, face à face.",
    "Je me rappelle maintenant : j'ai bien mis la table moi-même.",
])
def test_resolutions_stay_flagged(resolving):
    assert graph._BEAT_RESOLVES.search(resolving)


@pytest.mark.parametrize("statement", [
    "Ma mémoire me joue des tours, voilà tout.",
    "Mon esprit me joue des tours ce soir.",
])
def test_tricks_stated_as_fact_stay_flagged(statement):
    assert graph._BEAT_RESOLVES.search(statement)
