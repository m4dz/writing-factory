"""The selection checks fixed after the scaffold-ablation draws, each falsified
both ways (doctrine 4): the sentences quoted are the runs' own."""

import pytest

from factory import cli
from factory.pipeline import graph


def defects(text: str, is_first: bool = False) -> list[str]:
    return graph._score_beat(text, is_first, 7)[1]


@pytest.mark.parametrize("perceived", [
    "Je me souviens maintenant avoir entendu la porte d'entrée se fermer ce matin.",
    "Je note également les bruits que j'ai entendus, les sons qui ont résonné dans la maison.",
    "J'entends la musique qui tourne encore.",
    "J'ai cru entendre la porte.",
])
def test_presence_by_perception_is_flagged(perceived):
    assert "présence perçue" in defects(perceived)


@pytest.mark.parametrize("silent", [
    "Je n'ai rien entendu de la soirée.",
    "Je n'entends rien, la maison est silencieuse.",
    "La playlist est restée sur l'enceinte, l'écran allumé.",
])
def test_silence_is_not_presence(silent):
    assert "présence perçue" not in defects(silent)


@pytest.mark.parametrize("deciding", [
    "Je décide de vérifier une dernière fois la cuisine.",
    "Je ne me souviens pas l'avoir fait ce matin, mais je décide de noter cette information.",
    "Je décide d'attendre.",
])
def test_stated_intention_is_flagged(deciding):
    assert "décide (intention énoncée, doctrine 8)" in defects(deciding)


def test_a_decision_shown_is_not_flagged():
    assert defects("Je reprends le carnet. Je note l'heure, puis les deux couverts.") == []


@pytest.mark.parametrize("hypothesis", [
    "Je ne me souviens pas l'avoir sortie, mais peut-être l'ai-je fait sans y penser.",
    "Je ne me souviens pas avoir mis deux couverts ce matin, mais peut-être l'ai-je fait "
    "sans y penser.",
    "L'ai-je posé là sans y penser ?",
])
def test_an_open_hypothesis_does_not_dismiss(hypothesis):
    assert not any(d.startswith("congédie") for d in defects(hypothesis))


@pytest.mark.parametrize("dismissal", [
    "J'ai dû le faire machinalement. Je range le cahier.",
    "Je l'ai posé sans y penser, voilà tout.",
    "Je dois me tromper.",
])
def test_a_dismissal_stays_flagged(dismissal):
    assert any(d.startswith("congédie") for d in defects(dismissal))


def test_waking_is_exempt_in_the_first_entry_only(fake_model, fake_chroma, tmp_path,
                                                  monkeypatch):
    """Chapter 7's entry 2 is written the same night as entry 1: no beat of it
    may serve the waking again."""
    seen = []
    score = graph._score_beat

    def recording(variant, is_first, chapter=2):
        seen.append(is_first)
        return score(variant, is_first, chapter)

    monkeypatch.setattr(graph, "_score_beat", recording)
    assert cli.main(["generate", "--chapter", "7", "--seed", "424242", "--no-preflight",
                     "--no-voice", "--no-narrative-state", "--quiet",
                     "--runs-dir", str(tmp_path / "runs")]) == 0
    assert len(seen) == 9 and not any(seen)            # entry 2: 3 beats × best-of-3
    wake = "Je me suis réveillée ce matin avec une sensation bizarre."
    assert "redémarre (réveil déjà servi)" in defects(wake, is_first=False)
