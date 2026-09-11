"""The fake model's fixtures conform to the validators the pipeline applies.

If a fixture stops conforming, the graph leaves its nominal path and the
snapshot diff becomes unreadable. This file says which fixture broke, and why.
"""

from factory import text as style
from factory.eval.lint import interdits_materiels
from factory.pipeline import gestures as gestes
from factory.pipeline import graph
from fakes import fixtures as fx


def test_accumulations_pass_the_gesture_validator():
    for fall, chapter in (("l'assiette", 2), ("la playlist qui tourne encore", 7)):
        phrase = fx.accumulation(fall)
        ok, reason = gestes.valider_accumulation(phrase, chapitre=chapter)
        assert ok, reason
        assert phrase.endswith(f"{fall}.")
        assert 60 <= len(phrase.split()) <= gestes.ACC_MOTS_MAX


def test_beats_are_clean_and_bounded():
    caps = (4, 5, 4)
    for i, (beat, cap) in enumerate(zip(fx.BEATS, caps)):
        score, defects = graph._scorer_beat(beat, i == 0, 7)
        assert not defects, (i, defects)
        assert len(style.sentence_ends(beat)) <= cap
        assert not style.ends_mid_sentence(beat)


def test_short_entry_names_the_erasure_in_two_sentences():
    assert len(style.sentence_ends(fx.SHORT_ENTRY)) == 2
    assert 25 <= len(fx.SHORT_ENTRY.split()) <= 60
    score, defects = graph._scorer_entree1(fx.SHORT_ENTRY)
    assert score > 0 and not defects


def test_segments_are_lint_clean_for_chapter_2():
    for text in (fx.OPENING, fx.RECONSTRUCTION, fx.CLOSING, fx.FULL_ENTRY):
        assert not style.ends_mid_sentence(text)
        assert style.delint(text)[1] == []
        assert interdits_materiels(text, 2) == []
        assert graph.ENTETE_PARASITE.findall(text) == []
        assert "…" not in text


def test_plan_fixture_parses_into_three_beats_with_weather():
    beats = graph._parse_beats(fx.PLAN)
    assert len(beats) == 3
    assert all(graph.separer_meteo(b)[0] for b in beats)


def test_failing_fixtures_do_fail():
    """Falsification: the variants meant to trip a validator trip it."""
    assert graph._scorer_beat(fx.BEAT_RESOLVING, False, 7)[0] < 0
    assert not gestes.valider_accumulation(fx.ACCUMULATION_ENGLISH, chapitre=2)[0]
    assert not gestes.valider_accumulation(fx.ACCUMULATION_SHORT, chapitre=2)[0]
    from factory.roleplay import session as roleplay
    assert roleplay.hors_role(fx.OUT_OF_ROLE)
