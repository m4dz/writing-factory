import pytest

from factory.pipeline import gestures
from fakes import fixtures as fx


def test_compose_drift_cuts_on_the_suspension_and_appends_the_fact():
    out = gestures.compose_drift("Si je savais seulement pourquoi… et", "L'assiette est sèche.")
    assert out == "Si je savais seulement pourquoi… L'assiette est sèche."
    assert gestures.compose_drift("Il faudrait que je relise le jour où elle",
                                      "La lampe.") == \
        "Il faudrait que je relise le jour où elle… La lampe."


def test_approach_validator_both_ways():
    for bank in gestures.DRIFT_BANK.values():
        for a in bank["approches"]:
            assert gestures.approach_valid(a) == (True, "")
    assert not gestures.approach_valid("Mardi 12. Pluie fine et douce")[0]
    assert not gestures.approach_valid("Trop court ici")[0]
    assert not gestures.approach_valid("Je range la vaisselle et je monte me coucher")[0]


def test_passage_validator_both_ways():
    ok = "J'aurais dû demander, quand il était encore temps, ce qui l'a… La marge reste blanche."
    assert gestures.passage_valid(ok) == (True, "")
    naming = "J'aurais dû demander, quand il était encore temps, pourquoi son départ… La marge."
    assert "nomme le départ" in gestures.passage_valid(naming)[1]
    assert "aucune interruption" in gestures.passage_valid(
        "J'aurais dû demander quand il était encore temps ce qui manquait ici.")[1]
    assert "2 interruptions" in gestures.passage_valid(
        "J'aurais dû demander… quand il était encore temps ce qui… manquait.")[1]


def test_draw_is_seeded_without_replacement_and_chapter_scoped():
    a1, f1 = gestures.draw_approach(2, [], 7)
    assert (a1, f1) == gestures.draw_approach(2, [], 7)
    a2, _ = gestures.draw_approach(2, [a1], 7)
    a3, _ = gestures.draw_approach(2, [a1, a2], 7)
    assert len({a1, a2, a3}) == 3
    exhausted, fact = gestures.draw_approach(2, [a1, a2, a3], 7)
    assert exhausted == "" and fact
    assert gestures.draw_approach(99, [], 7) == ("", "")


TEXT = ("Ouverture du soir, le cahier.\n\nJe reprends les faits dans l'ordre, la "
        "fatigue.\n\nErreur de relevé, la faute est à moi.\n\nLa nuque raide.")


def test_accumulation_position_is_the_verdict_paragraph():
    pos = gestures.accumulation_position(TEXT, "erreur de relevé")
    assert TEXT[pos:].startswith("Erreur de relevé")
    pos = gestures.accumulation_position(TEXT, "")
    assert TEXT[pos:].startswith("Je reprends")


def test_drift_never_lands_in_the_accumulation_paragraph_or_last_third():
    pos_acc = gestures.accumulation_position(TEXT, "erreur de relevé")
    pos = gestures.drift_position(TEXT, pos_acc)
    assert pos < pos_acc and pos <= int(len(TEXT) * 2 / 3)


def test_frontier_uses_the_downstream_anchor():
    text = "La boîte, les photos.\n\nLa musique tourne.\n\nLe plat est au four.\n\nFin."
    pos = gestures.frontier_position(text, "à la frontière entre la musique et le plat")
    assert text[pos:].startswith("Le plat")
    assert gestures.frontier_position(text, "à la frontière des couverts") is None
    assert gestures.frontier_position(text, "nulle part") is None


def test_assembler_inserts_from_the_end_and_notes_collisions():
    out, notes = gestures.assemble(TEXT, "ACC, acc, acc.", "Si je savais… La lampe.",
                                  "erreur de relevé")
    paras = out.split("\n\n")
    assert paras.index("ACC, acc, acc.") == paras.index("Erreur de relevé, la faute est à moi.") - 1
    assert "Si je savais… La lampe." in paras and notes == []
    out, _ = gestures.assemble("A.\n\nB.", "", "Si je savais… X.", "", frontier=0)
    assert out.startswith("Si je savais… X.\n\nA.")


@pytest.mark.parametrize("sentence,last,ok,fragment", [
    (fx.accumulation("l'assiette"), False, True, ""),
    (fx.ACCUMULATION_SHORT, False, False, "seuils non atteints"),
    (fx.ACCUMULATION_SHORT, True, True, "ACCEPTÉE malgré"),
    ("Le retour, l'assiette ; le verre, sauf une, l'assiette.", True, False, "point-virgule"),
    (fx.ACCUMULATION_ENGLISH, False, False, "seuils non atteints"),
])
def test_accumulation_validator_thresholds(sentence, last, ok, fragment):
    got_ok, reason = gestures.validate_accumulation(sentence, last_attempt=last, chapter=2)
    assert got_ok is ok and fragment in reason


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN GAP (found while writing the safety net): the last-attempt tolerance on "
    "the word/comma thresholds returns before the language check, so a SHORT English "
    "accumulation is accepted on the last try. Fix belongs to the eval package "
    "(revamp step 5); this test flips when it lands."))
def test_short_english_accumulation_is_rejected_on_last_attempt():
    ok, reason = gestures.validate_accumulation(fx.ACCUMULATION_ENGLISH, last_attempt=True,
                                             chapter=2)
    assert not ok and "langue" in reason


def _long(items, tail="l'assiette"):
    return ", ".join(items) + f", sauf une, une seule, {tail}."


def test_accumulation_validator_reads_not_counts():
    base = fx.accumulation("l'assiette")
    third = base.replace("la clé dans la serrure", "elle est revenue à vingt heures")
    assert "troisième personne" in gestures.validate_accumulation(third, chapter=2)[1]
    scenery = base.replace("la clé dans la serrure", "la télévision allumée")
    assert "décor hors du monde" in gestures.validate_accumulation(scenery, chapter=2)[1]
    assert gestures.validate_accumulation(scenery, last_attempt=True, chapter=2)[0]
    summary = _long(["la grande perplexité", "la concentration", "la fatigue lourde",
                     "la panique sourde", "la respiration calme", "l'explication",
                     "le verdict rendu", "la mémoire fautive", "le souvenir flou",
                     "la décision prise", "la résolution ferme", "l'attention"] * 3)
    assert "se résume" in gestures.validate_accumulation(summary, chapter=2)[1]
    runaway = _long(["le mot"] * 200)
    assert "emballement" in gestures.validate_accumulation(runaway, last_attempt=True,
                                                        chapter=2)[1]
    english = base.replace("la clé dans la serrure", "the key in the lock")
    assert "langue" in gestures.validate_accumulation(english, chapter=2)[1]
