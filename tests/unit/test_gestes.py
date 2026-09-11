import gestes
import pytest
from fakes import fixtures as fx


def test_compose_drift_cuts_on_the_suspension_and_appends_the_fact():
    out = gestes.composer_glissement("Si je savais seulement pourquoi… et", "L'assiette est sèche.")
    assert out == "Si je savais seulement pourquoi… L'assiette est sèche."
    assert gestes.composer_glissement("Il faudrait que je relise le jour où elle",
                                      "La lampe.") == \
        "Il faudrait que je relise le jour où elle… La lampe."


def test_approach_validator_both_ways():
    for bank in gestes.BANQUE_GLISSEMENT.values():
        for a in bank["approches"]:
            assert gestes.approche_valide(a) == (True, "")
    assert not gestes.approche_valide("Mardi 12. Pluie fine et douce")[0]
    assert not gestes.approche_valide("Trop court ici")[0]
    assert not gestes.approche_valide("Je range la vaisselle et je monte me coucher")[0]


def test_passage_validator_both_ways():
    ok = "J'aurais dû demander, quand il était encore temps, ce qui l'a… La marge reste blanche."
    assert gestes.passage_valide(ok) == (True, "")
    naming = "J'aurais dû demander, quand il était encore temps, pourquoi son départ… La marge."
    assert "nomme le départ" in gestes.passage_valide(naming)[1]
    assert "aucune interruption" in gestes.passage_valide(
        "J'aurais dû demander quand il était encore temps ce qui manquait ici.")[1]
    assert "2 interruptions" in gestes.passage_valide(
        "J'aurais dû demander… quand il était encore temps ce qui… manquait.")[1]


def test_draw_is_seeded_without_replacement_and_chapter_scoped():
    a1, f1 = gestes.tirer_approche(2, [], 7)
    assert (a1, f1) == gestes.tirer_approche(2, [], 7)
    a2, _ = gestes.tirer_approche(2, [a1], 7)
    a3, _ = gestes.tirer_approche(2, [a1, a2], 7)
    assert len({a1, a2, a3}) == 3
    exhausted, fact = gestes.tirer_approche(2, [a1, a2, a3], 7)
    assert exhausted == "" and fact
    assert gestes.tirer_approche(99, [], 7) == ("", "")


TEXT = ("Ouverture du soir, le cahier.\n\nJe reprends les faits dans l'ordre, la "
        "fatigue.\n\nErreur de relevé, la faute est à moi.\n\nLa nuque raide.")


def test_accumulation_position_is_the_verdict_paragraph():
    pos = gestes.position_accumulation(TEXT, "erreur de relevé")
    assert TEXT[pos:].startswith("Erreur de relevé")
    pos = gestes.position_accumulation(TEXT, "")
    assert TEXT[pos:].startswith("Je reprends")


def test_drift_never_lands_in_the_accumulation_paragraph_or_last_third():
    pos_acc = gestes.position_accumulation(TEXT, "erreur de relevé")
    pos = gestes.position_glissement(TEXT, pos_acc)
    assert pos < pos_acc and pos <= int(len(TEXT) * 2 / 3)


def test_frontier_uses_the_downstream_anchor():
    text = "La boîte, les photos.\n\nLa musique tourne.\n\nLe plat est au four.\n\nFin."
    pos = gestes.position_frontiere(text, "à la frontière entre la musique et le plat")
    assert text[pos:].startswith("Le plat")
    assert gestes.position_frontiere(text, "à la frontière des couverts") is None
    assert gestes.position_frontiere(text, "nulle part") is None


def test_assembler_inserts_from_the_end_and_notes_collisions():
    out, notes = gestes.assembler(TEXT, "ACC, acc, acc.", "Si je savais… La lampe.",
                                  "erreur de relevé")
    paras = out.split("\n\n")
    assert paras.index("ACC, acc, acc.") == paras.index("Erreur de relevé, la faute est à moi.") - 1
    assert "Si je savais… La lampe." in paras and notes == []
    out, _ = gestes.assembler("A.\n\nB.", "", "Si je savais… X.", "", frontiere=0)
    assert out.startswith("Si je savais… X.\n\nA.")


@pytest.mark.parametrize("phrase,last,ok,fragment", [
    (fx.accumulation("l'assiette"), False, True, ""),
    (fx.ACCUMULATION_SHORT, False, False, "seuils non atteints"),
    (fx.ACCUMULATION_SHORT, True, True, "ACCEPTÉE malgré"),
    ("Le retour, l'assiette ; le verre, sauf une, l'assiette.", True, False, "point-virgule"),
    (fx.ACCUMULATION_ENGLISH, False, False, "seuils non atteints"),
])
def test_accumulation_validator_thresholds(phrase, last, ok, fragment):
    got_ok, reason = gestes.valider_accumulation(phrase, dernier_essai=last, chapitre=2)
    assert got_ok is ok and fragment in reason


@pytest.mark.xfail(strict=True, reason=(
    "KNOWN GAP (found while writing the safety net): the last-attempt tolerance on "
    "the word/comma thresholds returns before the language check, so a SHORT English "
    "accumulation is accepted on the last try. Fix belongs to the eval package "
    "(revamp step 5); this test flips when it lands."))
def test_short_english_accumulation_is_rejected_on_last_attempt():
    ok, reason = gestes.valider_accumulation(fx.ACCUMULATION_ENGLISH, dernier_essai=True,
                                             chapitre=2)
    assert not ok and "langue" in reason


def _long(items, tail="l'assiette"):
    return ", ".join(items) + f", sauf une, une seule, {tail}."


def test_accumulation_validator_reads_not_counts():
    base = fx.accumulation("l'assiette")
    third = base.replace("la clé dans la serrure", "elle est revenue à vingt heures")
    assert "troisième personne" in gestes.valider_accumulation(third, chapitre=2)[1]
    decor = base.replace("la clé dans la serrure", "la télévision allumée")
    assert "décor hors du monde" in gestes.valider_accumulation(decor, chapitre=2)[1]
    assert gestes.valider_accumulation(decor, dernier_essai=True, chapitre=2)[0]
    summary = _long(["la grande perplexité", "la concentration", "la fatigue lourde",
                     "la panique sourde", "la respiration calme", "l'explication",
                     "le verdict rendu", "la mémoire fautive", "le souvenir flou",
                     "la décision prise", "la résolution ferme", "l'attention"] * 3)
    assert "se résume" in gestes.valider_accumulation(summary, chapitre=2)[1]
    runaway = _long(["le mot"] * 200)
    assert "emballement" in gestes.valider_accumulation(runaway, dernier_essai=True,
                                                        chapitre=2)[1]
    english = base.replace("la clé dans la serrure", "the key in the lock")
    assert "langue" in gestes.valider_accumulation(english, chapitre=2)[1]
