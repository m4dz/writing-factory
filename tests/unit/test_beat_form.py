"""beat-instruction-form: the served form of a beat, prose or person-less."""

import pytest

from factory.chapter_spec.model import BeatSpec, EntrySpec
from factory.pipeline import graph
from factory.settings import settings

PROSE = BeatSpec("relève", 300, 4, "Elle relit la ligne. Elle relève un écart.",
                 ends="elle a nommé l'écart",
                 nominal="La relève. La ligne relue ; un écart relevé.",
                 ends_nominal="l'écart nommé")
BARE = BeatSpec("doute", 300, 4, "Elle repose le crayon.", ends="elle repose le crayon")


@pytest.fixture
def nominal(monkeypatch):
    monkeypatch.setattr(settings, "beat_form", "nominal")


def test_prose_is_the_default():
    assert graph._served_beat(PROSE) == (PROSE.instruction, PROSE.ends)


def test_nominal_serves_the_person_less_form(nominal):
    assert graph._served_beat(PROSE) == (PROSE.nominal, PROSE.ends_nominal)


def test_nominal_without_its_own_end_keeps_the_prose_end(nominal):
    beat = BeatSpec("x", 300, 4, "Elle range.", ends="elle a rangé", nominal="Le rangement.")
    assert graph._served_beat(beat) == ("Le rangement.", "elle a rangé")


def test_nominal_refuses_a_beat_without_nominal_form(nominal):
    with pytest.raises(ValueError, match="Nominal"):
        graph._served_beat(BARE)


def test_plan_state_names_times_by_the_served_form(nominal):
    other = BeatSpec("doute", 300, 4, "Elle repose le crayon.", ends="elle repose le crayon",
                     nominal="Le doute. Le crayon reposé.")
    sheet = EntrySpec(beats=(PROSE, other), movement="m")
    state = graph._plan_state(sheet, "doute")
    assert "La relève." in state and "l'écart nommé" not in state
    assert "Elle relit" not in state
    assert "le crayon reposé" not in state.split("CE TEMPS-CI")[0]
    first = graph._plan_state(sheet, "relève")
    assert "il finit quand : l'écart nommé" in first and "Le doute." in first


def test_beat_prompt_under_nominal_carries_no_prose_instruction(nominal):
    served, _ = graph._served_beat(PROSE)
    prompt = graph._prompt_beat(served, "", graph._plan_state(
        EntrySpec(beats=(PROSE,), movement="m"), "relève"), written_first=True)
    assert "Elle relit" not in prompt and "La relève." in prompt


def test_beat_form_is_a_closed_override():
    from factory import runs
    assert runs.validate_overrides({"beat_form": "nominal"}) == {"beat_form": "nominal"}
    with pytest.raises(Exception):
        runs.validate_overrides({"beat_form": "tu"})
