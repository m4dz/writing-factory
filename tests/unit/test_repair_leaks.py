"""The language repair touches only the sentences where English is detected."""

from factory.pipeline import qa
from factory.text import english_leaks

# Measured 2026-11-16 (seed 174597): served the whole entry, the repair
# rewrote this French and lost the decision.
CLEAN = ("Samedi 14. Beau temps.\n\nJ’ai décidé de ne pas allumer les bougies du soir. "
         "Les photos restent dans le tiroir de l’entrée.")


def _fake_repair(calls):
    def repair(text):
        calls.append(text)
        return text.replace("suddenly the door", "soudain la porte"), {"wall_s": 0.1}
    return repair


def test_french_is_returned_byte_for_byte_without_a_call(monkeypatch):
    calls = []
    monkeypatch.setattr(qa, "repair", _fake_repair(calls))
    text, metrics, notes = qa.repair_leaks(CLEAN)
    assert text == CLEAN and calls == [] and metrics == [] and notes == []


def test_only_the_leaking_sentence_is_served_and_replaced(monkeypatch):
    calls = []
    monkeypatch.setattr(qa, "repair", _fake_repair(calls))
    entry = CLEAN + " Puis, suddenly the door s’est ouverte.\n\nLa lampe reste allumée."
    text, metrics, notes = qa.repair_leaks(entry)
    assert calls == ["Puis, suddenly the door s’est ouverte."]
    assert text == CLEAN + " Puis, soudain la porte s’est ouverte.\n\nLa lampe reste allumée."
    assert len(metrics) == 1 and "phrase réparée ['the']" in notes[0]


def test_a_repair_that_is_no_longer_a_sentence_is_refused(monkeypatch):
    monkeypatch.setattr(qa, "repair",
                        lambda t: ("Voici le texte corrigé :\n\nLa porte.", {}))
    entry = "La porte, the door, s’ouvre."
    text, _, notes = qa.repair_leaks(entry)
    assert text == entry and "non réparée" in notes[0]


def test_detection_includes_glued_tokens():
    assert english_leaks("Nous nousWantons partir.") == ["nousWantons"]
    assert english_leaks(CLEAN) == []
