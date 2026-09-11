import graph
import pytest
from fakes import fixtures as fx

HEADER = "Samedi 14. Beau temps."
ANCHOR = "« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts. »"


def test_header_is_composed_and_dates_derive():
    assert graph.entete("Mardi", 12, 1, "pluie fine") == "Mercredi 13. Pluie fine."
    assert graph.entete("Dimanche", 20, 1, "") == "Lundi 21. Temps calme."
    assert graph.entete("samedi", 14, 0, "Beau temps.") == "Samedi 14. Beau temps."


def test_weather_field_is_split_from_the_beat():
    assert graph.separer_meteo("[Ciel couvert] elle relit") == ("Ciel couvert", "elle relit")
    assert graph.separer_meteo("elle relit") == ("", "elle relit")


def test_reattach_removes_exact_overlap_and_closes_orphans():
    tail = "la lampe du couloir restée allumée jusqu'au matin."
    debut = "Elle a vu " + tail
    assert graph._recoller(debut, tail + " Puis rien.") == debut + "\n\nPuis rien."
    assert graph._recoller("dans un coin de la pièce", "Elle s'en approche.") == \
        "dans un coin de la pièce. Elle s'en approche."
    assert graph._recoller("il hésita, puis", "— Tu mens.") == "il hésita, puis…\n\n— Tu mens."
    assert graph._recoller("il hésita, puis", "sans un mot.") == "il hésita, puis sans un mot."


def test_approximate_anchor_repeat_is_removed():
    prefix = f"{HEADER}\n\n{ANCHOR}"
    suite = (f"{HEADER}\n\n« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis les deux "
             "couverts. »\n\nLe reste du texte.")
    assert graph._retirer_reprise_approximative(prefix, suite) == "Le reste du texte."
    assert graph._retirer_reprise_approximative(prefix, "Le reste.") == "Le reste."


def test_sentence_bound_excludes_the_prefix():
    prefix = f"{HEADER}\n\n"
    text = prefix + "Une. Deux. Trois. Quatre."
    out, warns = graph._borner_en_phrases(text, 2, 0, prefix)
    assert out == prefix + "Une. Deux." and warns and "2 retirée" in warns[0]
    assert graph._borner_en_phrases("Une. Deux.", 2, 0, "") == ("Une. Deux.", [])


def test_segment_cleaning_removes_owned_markers():
    seg = f"{HEADER}\n\nElle attend… attend encore. Puis... rien."
    out, warns = graph._nettoyer_segment(seg, "t")
    assert HEADER not in out and "…" not in out and "..." not in out
    assert out == "Elle attend encore. Puis, rien."
    assert len(warns) == 2


def test_beat_scorer_falsified_both_ways():
    assert graph._scorer_beat(fx.BEATS[1], False, 7) == (3, [])
    score, defects = graph._scorer_beat(fx.BEAT_RESOLVING, False, 7)
    assert score < 0 and any("résout" in d for d in defects)
    wake = "Je me suis réveillée. La table est mise."
    assert graph._scorer_beat(wake, True, 7)[1] == []
    assert "redémarre (réveil déjà servi)" in graph._scorer_beat(wake, False, 7)[1]
    assert "présence perçue" in graph._scorer_beat("Un bruit dans le salon.", False, 7)[1]
    assert any("décor" in d for d in
               graph._scorer_beat("La télévision est allumée.", False, 7)[1])


def test_entry1_scorer():
    assert graph._scorer_entree1(fx.SHORT_ENTRY) == (3, [])
    score, defects = graph._scorer_entree1("J'ai décidé de ranger le cahier au grenier.")
    assert score < 0 and len(defects) == 2


def test_restamp_replaces_altered_header_and_removes_anchor_copy():
    entry = f"Samedi 14, beau temps.\n\n{ANCHOR}\n\nCorps.\n\n{ANCHOR}\n\nSuite."
    out, notes = graph._retamponner(entry, tete=HEADER, ancre=ANCHOR)
    paras = out.split("\n\n")
    assert paras[0] == HEADER and paras.count(ANCHOR) == 1
    assert any("re-tamponné" in n for n in notes) and any("doublon" in n for n in notes)


def test_restamp_reposes_missing_anchor():
    out, notes = graph._retamponner(f"{HEADER}\n\nCorps.", tete=HEADER, ancre=ANCHOR)
    assert out.split("\n\n")[1] == ANCHOR and any("ABSENT" in n for n in notes)


@pytest.mark.parametrize("before,after,target,ok", [
    (1033, 495, (450, 600), True),    # into the target: accepted whatever the depth
    (500, 480, (450, 600), True),
    (400, 250, (450, 600), True),     # already short, cut < 40 %
    (400, 200, (450, 600), False),    # already short, cut too deep
    (700, 300, (450, 600), False),    # crossed below the floor, moved away
    (315, 156, (25, 60), True),       # ch. 7 entry 1: towards the brief
])
def test_cut_acceptance(before, after, target, ok):
    assert graph._coupe_acceptable(before, after, target) is ok


def test_plan_parsing_and_machinery_stripping():
    assert graph._parse_beats("intro\n1. a\n 2) b\nprose\n") == ["a", "b"]
    assert graph._sans_machinerie(
        "Rien ne se résout : la dernière ligne est posée par le code") == "Rien ne se résout."
    assert graph._sans_machinerie("Le texte commence agacé.") == "Le texte commence agacé."


def test_pruning_removes_marked_sentences_and_protects_owned_lines():
    entry = ("Samedi 14. Beau temps.\n\n« Une citation posée par le code, assez longue. »\n\n"
             "Je pose le manteau. Un bruit dans le salon me fait sursauter. "
             "Je n'ai pas rêvé, tout est normal. Je ne sais pas.\n\nConstat : anniversaire.")
    out, notes = graph._assembler_qwen(entry)
    assert "Un bruit" not in out and "pas rêvé" not in out
    assert "« Une citation" in out and out.endswith("Constat : anniversaire.")
    assert notes and "2 phrase(s)" in notes[0]
    clean = "Je pose le manteau. Je ne sais pas."
    assert graph._assembler_qwen(clean) == (clean, ["pruning : rien à retirer"])
    mostly_bad = "Un bruit. Une voix. Des pas. Je reste."
    out, notes = graph._assembler_qwen(mostly_bad)
    assert out == mostly_bad and "REJETÉ" in notes[0]


def test_gestures_permission_reads_the_entry_spec():
    state = {"scenes": ["a"], "entrees_spec": [{"gestes": False}, {"gestes": True}]}
    assert graph._gestes_permis(state) is False
    state["scenes"].append("b")
    assert graph._gestes_permis(state) is True
    assert graph._gestes_permis({"scenes": ["a"], "entrees_spec": []}) is True
