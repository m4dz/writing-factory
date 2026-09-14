"""The fake model's fixtures conform to the validators the pipeline applies.

If a fixture stops conforming, the graph leaves its nominal path and the
snapshot diff becomes unreadable. This file says which fixture broke, and why.
"""

from factory import text as text_mod
from factory.chapter_spec import load_chapter
from factory.eval.lint import material_forbidden
from factory.pipeline import gestures, graph, scorers
from fakes import fixtures as fx


def test_accumulations_pass_the_gesture_validator():
    for fall, chapter in (("l'assiette", 2), ("la playlist qui tourne encore", 7)):
        sentence = fx.accumulation(fall)
        ok, reason = gestures.validate_accumulation(sentence, chapter=chapter)
        assert ok, reason
        assert sentence.endswith(f"{fall}.")
        assert 60 <= len(sentence.split()) <= gestures.ACC_WORDS_MAX


def test_beats_are_clean_and_bounded():
    caps = (4, 5, 4)
    for i, (beat, cap) in enumerate(zip(fx.BEATS, caps)):
        score, defects = graph._score_beat(beat, i == 0, 7)
        assert not defects, (i, defects)
        assert len(text_mod.sentence_ends(beat)) <= cap
        assert not text_mod.ends_mid_sentence(beat)


def test_short_entry_names_the_erasure_in_two_sentences():
    assert len(text_mod.sentence_ends(fx.SHORT_ENTRY)) == 2
    assert 25 <= len(fx.SHORT_ENTRY.split()) <= 60
    score, defects = scorers.score(fx.SHORT_ENTRY, load_chapter(7).entries[0].best_of)
    assert score > 0 and not defects


def test_segments_are_lint_clean_for_chapter_2():
    for text in (fx.OPENING, fx.RECONSTRUCTION, fx.CLOSING, fx.FULL_ENTRY):
        assert not text_mod.ends_mid_sentence(text)
        assert text_mod.delint(text)[1] == []
        assert material_forbidden(text, 2) == []
        assert graph.STRAY_HEADER.findall(text) == []
        assert "…" not in text


def test_plan_fixture_parses_into_three_beats_with_weather():
    beats = graph._parse_beats(fx.PLAN)
    assert len(beats) == 3
    assert all(graph.split_weather(b)[0] for b in beats)


def test_failing_fixtures_do_fail():
    """Falsification: the variants meant to trip a validator trip it."""
    assert graph._score_beat(fx.BEAT_RESOLVING, False, 7)[0] < 0
    assert not gestures.validate_accumulation(fx.ACCUMULATION_ENGLISH, chapter=2)[0]
    assert not gestures.validate_accumulation(fx.ACCUMULATION_SHORT, chapter=2)[0]
    from factory.roleplay import session as roleplay
    assert roleplay.out_of_role(fx.OUT_OF_ROLE)
