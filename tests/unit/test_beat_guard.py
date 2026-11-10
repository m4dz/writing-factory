"""The entry guard reads what the CODE serves, not the model's own prose
re-served as the begun entry (beat-guard-model-text). Falsified both ways per
site (doctrine 4): a served workshop term still raises, « la grille du four »
written by the model passes. The sentence is the one that killed
xp-author-models M/781771."""

import pytest

from factory.chapter_spec.model import EntrySpec
from factory.pipeline import graph

MODEL_TEXT = "Je pose le plat sur la grille du four. Le code de la porte, je l'ai oublié."
PREFIX = "Samedi 14. Beau temps."


def block(text: str) -> str:
    already = f"{PREFIX}\n\n{text}".strip()
    return ("L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris "
            f"PAS :\n---\n{already}\n---\n"
            "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne "
            "répète rien de ce qui précède.\n")


SHEET = EntrySpec(movement="elle relit, doute, repose le crayon")


def test_beat_model_text_term_passes():
    prompt = graph._prompt_beat("Elle relit la ligne.", block(MODEL_TEXT),
                                model_text=MODEL_TEXT)
    assert "la grille du four" in prompt          # served untouched


def test_beat_served_term_raises():
    with pytest.raises(AssertionError, match="grille"):
        graph._prompt_beat("Elle relit la grille.", block(MODEL_TEXT),
                           model_text=MODEL_TEXT)


def test_beat_term_in_code_prefix_raises():
    # The prefix (header, anchor) is code-posed: only the model's part is skipped.
    text = "Je relis."
    leaky = block(text).replace(PREFIX, PREFIX + " Le pipeline.")
    with pytest.raises(AssertionError, match="pipeline"):
        graph._prompt_beat("Elle relit la ligne.", leaky, model_text=text)


def test_beat_without_model_text_still_scans_everything():
    with pytest.raises(AssertionError, match="grille"):
        graph._prompt_beat("Elle relit la ligne.", block(MODEL_TEXT))


def test_movement_model_text_term_passes():
    prompt = graph._movement_prompt(SHEET, "100 à 200 mots", "Tu écris la suite.",
                                    block(MODEL_TEXT), model_text=MODEL_TEXT)
    assert "la grille du four" in prompt


def test_movement_served_term_raises():
    with pytest.raises(AssertionError, match="grille"):
        graph._movement_prompt(SHEET, "100 à 200 mots", "Tu écris la grille.",
                               block(MODEL_TEXT), model_text=MODEL_TEXT)
