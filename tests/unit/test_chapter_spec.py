"""Chapter knowledge as data: the spec files load, point at the briefs without
copying them, build the states the graph runs on, and refuse what leaks."""

import re
import textwrap

import pytest

from factory.chapter_spec import ChapterSpecError, chapter_dirs, load_chapter, load_spec, loader
from factory.chapter_spec.model import EntrySpec


def test_both_chapters_are_discovered():
    assert set(chapter_dirs()) >= {2, 7}
    with pytest.raises(ChapterSpecError, match="chapitre 99"):
        load_chapter(99)


def test_chapter7_brief_is_read_from_the_file_and_names_no_bible_file():
    spec = load_chapter(7)
    assert spec.brief and not re.search(r"\b[\w-]+\.md\b", spec.brief)
    assert "Entrée 1" in spec.brief and "Entrée 2" in spec.brief
    assert len(spec.imposed_plan) == 2 == spec.entry_count
    assert "Entrée 1" in spec.imposed_plan[0] and "Entrée 2" in spec.imposed_plan[1]
    # The owner's brief carries workshop words; they are reported, not rewritten.
    assert "matériau" in spec.workshop_terms


def test_chapter7_entries_have_the_stage_structure():
    spec = load_chapter(7)
    e1, e2 = spec.entries
    assert e1.citation == "" and e1.sentences_max == 2 and e1.gestures is False
    assert e1.strategy == "single" and e1.best_of.n == 3
    assert e1.best_of.criterion == "names-erasure" and "playlist" in e1.best_of.names
    assert e1.movement and e1.material and e1.vetos
    assert e2.citation.startswith("« Neuf ans") and e2.fall == "Constat : anniversaire."
    assert e2.strategy == "beats"
    assert [(b.name, b.num_predict, b.sentences_max) for b in e2.beats] == \
        [("relève", 150, 4), ("découverte", 240, 5), ("doute", 150, 4)]
    assert all(b.instruction for b in e2.beats)          # read from brief-entree-2.md §7
    assert e2.trajectory and e2.material and e2.drift.text and e2.drift.position
    assert e2.form == {"accumulation": "allowed", "verdict": "absent"}
    assert spec.assembly == {"on_second_header": True, "fall": "Constat : anniversaire."}


def test_movement_line_is_extracted_per_entry_never_the_file():
    e1, e2 = load_chapter(7).entries
    assert e1.movement and e2.movement and e1.movement != e2.movement
    assert "\n" not in e1.movement
    assert loader.movement_row(99) == ""


def test_chapter2_spec_carries_the_calibration_constants():
    spec = load_chapter(2)
    assert spec.entry_count == 3 and spec.entries == ()
    assert spec.prefix.startswith("« Deux assiettes") and spec.verdict == "erreur de relevé"
    assert spec.calendar.weekday == "Mardi" and spec.calendar.number == 12
    assert spec.entry_brief.startswith("Chapitre 2, entrée unique")
    assert spec.brief.startswith("Chapitre 2 complet")
    assert len(spec.stations) == 6 and spec.accumulation_fall == "l'assiette"
    assert len(spec.drift_bank.approaches) == 3 and len(spec.drift_bank.facts) == 3


def test_state_builder_and_its_run_overrides():
    spec = load_chapter(7)
    st = spec.state(seed=5)
    assert st["seed"] == 5 and st["chapter"] == 7 and st["prefix"] == ""
    assert len(st["entry_specs"]) == 2 == st["expected_entries"]
    assert len(st["imposed_plan"]) == 2 and st["stations"] == list(spec.stations)
    assert st["drift_bank"] == {"approaches": list(spec.drift_bank.approaches),
                                "facts": list(spec.drift_bank.facts)}
    ch2 = load_chapter(2)
    scored = ch2.state(seed=1, brief=ch2.entry_brief, entry_count=1, rag=False,
                       micro_nodes=False, segments=False, prefix="")
    assert scored["expected_entries"] == 1 and scored["brief"] == ch2.entry_brief
    assert scored["imposed_plan"] == [] and scored["rag"] is False and scored["prefix"] == ""
    a, b = ch2.state(), ch2.state()
    assert isinstance(a["seed"], int) and a["seed"] >= 1 and isinstance(b["seed"], int)


def _write_spec(tmp_path, body: str, name="03-essai"):
    d = tmp_path / name
    d.mkdir()
    (d / "spec.yaml").write_text(textwrap.dedent(body), encoding="utf-8")
    return d


def test_minimal_spec_leaves_defaults_unchanged(tmp_path):
    d = _write_spec(tmp_path, """
        chapter: 3
        slug: essai
        narrator: judith
        brief: "Une entrée du carnet, le soir."
    """)
    spec = load_spec(d / "spec.yaml")
    st = spec.state(seed=1)
    assert st["entry_specs"] == [] and st["expected_entries"] == 1
    assert st["stations"] == [] and st["accumulation_fall"] == "" and st["assembly"] == {}
    assert st["start_day"] == "Mardi" and st["drift_bank"] == {"approaches": [], "facts": []}
    assert EntrySpec().uses_segments(True) is True
    assert EntrySpec(strategy="single").uses_segments(True) is False
    assert chapter_dirs(tmp_path) == {3: d}


def test_loader_refuses_leaks_and_inconsistencies(tmp_path):
    with pytest.raises(ChapterSpecError, match="fichiers de bible"):
        load_spec(_write_spec(tmp_path, """
            chapter: 3
            slug: a
            narrator: judith
            brief: "Voir `fiche-romane.md` pour la ligne relue."
        """, "03-a") / "spec.yaml")
    with pytest.raises(ChapterSpecError, match="termes d'atelier"):
        load_spec(_write_spec(tmp_path, """
            chapter: 4
            slug: b
            narrator: judith
            brief: "Matériau : le cahier. Couperet en fin."
        """, "04-b") / "spec.yaml")
    with pytest.raises(ChapterSpecError, match="validateur"):
        load_spec(_write_spec(tmp_path, """
            chapter: 5
            slug: c
            narrator: judith
            brief: "Le soir."
            drift_bank: {approaches: ["Trop court ici"], facts: ["La lampe."]}
        """, "05-c") / "spec.yaml")
    with pytest.raises(ChapterSpecError, match="beats"):
        load_spec(_write_spec(tmp_path, """
            chapter: 6
            slug: d
            narrator: judith
            brief: "Le soir."
            entries:
              - {strategy: beats}
        """, "06-d") / "spec.yaml")


def test_served_brief_drops_fabrication_notes():
    text = ("ancre [CIT-2], fournie en matériau, pré-écrite selon `fiche-romane.md` §1 : une ligne "
            "chaude (cf. `objets.md`) sans plus.")
    out = loader.strip_fabrication_notes(text)
    assert "fiche-romane" not in out and "objets.md" not in out
    assert out.startswith("ancre [CIT-2], fournie en matériau : une ligne")
