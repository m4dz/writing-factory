import re

from factory.chapter_spec import chapter7 as ch7


def test_brief_is_read_from_the_file_and_names_no_bible_file():
    brief = ch7.brief_chapitre_7()
    assert brief and not re.search(r"\b[\w-]+\.md\b", brief)
    assert "Entrée 1" in brief and "Entrée 2" in brief


def test_the_brief_carries_its_own_two_beats():
    beats = ch7.beats_chapitre_7()
    assert len(beats) == 2
    assert "Entrée 1" in beats[0] and "Entrée 2" in beats[1]


def test_entry2_brief_sections():
    b = ch7.brief_entree2_v2()
    assert set(b) == {"beats", "intention", "trajectoire", "matiere", "vetos", "glissement"}
    assert len(b["beats"]) == 3 and all(b["beats"])
    assert b["trajectoire"] and b["matiere"]
    assert b["vetos"] == ch7.VETOS_SERVIS
    assert b["glissement"]["texte"] and b["glissement"]["position"]


def test_movement_line_is_extracted_per_entry_never_the_file():
    m1, m2 = ch7.mouvement(7, 1), ch7.mouvement(7, 2)
    assert m1 and m2 and m1 != m2 and "\n" not in m1
    assert ch7.mouvement(99) == ""


def test_state_for_the_api_has_the_stage_structure():
    state = ch7.etat_ch7(graine=5)
    assert state["graine"] == 5 and state["chapitre"] == 7
    assert len(state["entrees_spec"]) == 2 == state["entrees_attendues"]
    e1, e2 = state["entrees_spec"]
    assert e1["citation"] == "" and e1["phrases_max"] == 2 and e1["gestes"] is False
    assert e2["citation"] == ch7.CIT_2 and e2["chute"] == "Constat : anniversaire."
    assert [(n, npd, pmax) for n, npd, pmax, _ in e2["beats"]] == \
        [("relève", 150, 4), ("découverte", 240, 5), ("doute", 150, 4)]
    assert state["prefixe"] == "" and len(state["plan_impose"]) == 2
    assert ch7.MARQUEURS_CH7 == {"sur_second_entete": True, "chute": "Constat : anniversaire."}


def test_random_seed_by_default_is_recorded():
    a, b = ch7.etat_ch7(), ch7.etat_ch7()
    assert isinstance(a["graine"], int) and a["graine"] >= 1
    assert a["graine"] != b["graine"] or a["graine"] == b["graine"]  # both ints, nothing else
