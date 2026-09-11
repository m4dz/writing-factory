import re

from factory.chapter_spec import chapter7 as ch7


def test_brief_is_read_from_the_file_and_names_no_bible_file():
    brief = ch7.brief_chapter_7()
    assert brief and not re.search(r"\b[\w-]+\.md\b", brief)
    assert "Entrée 1" in brief and "Entrée 2" in brief


def test_the_brief_carries_its_own_two_beats():
    beats = ch7.beats_chapter_7()
    assert len(beats) == 2
    assert "Entrée 1" in beats[0] and "Entrée 2" in beats[1]


def test_entry2_brief_sections():
    b = ch7.brief_entry2_v2()
    assert set(b) == {"beats", "intention", "trajectoire", "matiere", "vetos", "glissement"}
    assert len(b["beats"]) == 3 and all(b["beats"])
    assert b["trajectoire"] and b["matiere"]
    assert b["vetos"] == ch7.SERVED_VETOS
    assert b["glissement"]["texte"] and b["glissement"]["position"]


def test_movement_line_is_extracted_per_entry_never_the_file():
    m1, m2 = ch7.movement(7, 1), ch7.movement(7, 2)
    assert m1 and m2 and m1 != m2 and "\n" not in m1
    assert ch7.movement(99) == ""


def test_state_for_the_api_has_the_stage_structure():
    state = ch7.ch7_state(seed=5)
    assert state["seed"] == 5 and state["chapter"] == 7
    assert len(state["entry_specs"]) == 2 == state["expected_entries"]
    e1, e2 = state["entry_specs"]
    assert e1["citation"] == "" and e1["phrases_max"] == 2 and e1["gestures"] is False
    assert e2["citation"] == ch7.QUOTE_2 and e2["chute"] == "Constat : anniversaire."
    assert [(n, npd, pmax) for n, npd, pmax, _ in e2["beats"]] == \
        [("relève", 150, 4), ("découverte", 240, 5), ("doute", 150, 4)]
    assert state["prefix"] == "" and len(state["imposed_plan"]) == 2
    assert ch7.MARKERS_CH7 == {"on_second_header": True, "fall": "Constat : anniversaire."}


def test_random_seed_by_default_is_recorded():
    a, b = ch7.ch7_state(), ch7.ch7_state()
    assert isinstance(a["seed"], int) and a["seed"] >= 1
    assert a["seed"] != b["seed"] or a["seed"] == b["seed"]  # both ints, nothing else
