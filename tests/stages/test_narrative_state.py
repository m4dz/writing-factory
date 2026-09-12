"""The narrative-state node: one generated file per chapter, indexed with its
chapter, served in place of the sheet's section 7 — and the sheet's section
when no state was generated, which is what the snapshot suite runs on."""

from factory.chapter_spec import narrative_state as ns
from factory.pipeline.nodes import narrative_state as node
from factory.retrieval import context as retrieval
from factory.settings import settings


def test_state_text_is_derived_from_the_previous_row_in_world_language():
    assert ns.state_text(1) == ns.OPENING
    text = ns.state_text(3)                      # what chapter 2 left
    assert "erreur de relevé" in text and "Régime" not in text and "grade" not in text
    try:
        ns.state_text(13)
    except LookupError as exc:
        assert "chapitre 12" in str(exc)
    else:
        raise AssertionError("row 12 does not exist")


def test_node_is_idempotent_and_indexes_a_chapter_scoped_chunk(tmp_path, monkeypatch,
                                                                fake_chroma, quiet_progress):
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    assert node.narrative_state_node({"chapter": 7}) == {}          # not asked
    out = node.narrative_state_node({"chapter": 7, "narrative_state": True})
    path = tmp_path / "generated" / "narrative-state" / "ch-07.md"
    assert out == {"narrative_state_path": str(path)} and path.is_file()
    assert "chapter: 7" in path.read_text(encoding="utf-8")
    col = fake_chroma.get_collection("auteur")
    got = col.get(ids=["judith::etat_narratif_courant::ch07"], include=["documents", "metadatas"])
    assert got["ids"] == ["judith::etat_narratif_courant::ch07"]
    assert got["metadatas"][0]["chapter"] == 7 and "Judith" not in got["documents"][0]
    assert got["documents"][0].startswith("[la narratrice / État narratif courant]")
    # Second pass: same file, same chunk, "inchangé" noted.
    node.narrative_state_node({"chapter": 7, "narrative_state": True})
    assert any("inchangé" in n for n in quiet_progress.notes)
    # A chapter beyond the table is not an error: the sheet alone serves it.
    out = node.narrative_state_node({"chapter": 13, "narrative_state": True})
    assert out == {"narrative_state_path": ""}


def test_retrieval_prefers_the_chapter_chunk_and_falls_back_to_the_sheet(tmp_path, monkeypatch,
                                                                          fake_chroma):
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    sheet_state = retrieval.character_context("judith")
    assert retrieval.character_context("judith", chapter=7) == sheet_state   # nothing generated yet
    node.narrative_state_node({"chapter": 7, "narrative_state": True})
    scoped = retrieval.character_context("judith", chapter=7)
    assert scoped != sheet_state and ns.state_text(7).split(".")[0] in scoped
    assert retrieval.character_context("judith") == sheet_state      # other chapters untouched
    assert retrieval.character_context("judith", chapter=2) == sheet_state
    prompt = retrieval.assemble_system_prompt(characters=["judith"], scene_brief="x",
                                              include_scenes=False, chapter=7)
    assert ns.state_text(7).split(".")[0] in prompt
