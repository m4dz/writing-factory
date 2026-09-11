from pathlib import Path

import pytest

from factory.retrieval import indexer as index

SHEET = """---
doc_id: x
type: character
depends_on: chronologie-partie-double.md
version: 3
---
# X

Note de travail qui cite la chronologie.

## 1. Voix

Judith parle peu. <!-- consigne humaine -->

## Notes

Hors numérotation, jamais indexé.

## 2. Histoire

Chapeau de section.

### [SURFACE]

Ce que le lecteur sait.

### [PROFOND — la fin]

Ce que personne ne doit lire.
"""

OBJECTS = """---
doc_id: objets
---
## Le cahier

Grand cahier ligné.

## [RÉSERVÉS — chapitre 7]

photos, playlist, plat, couverts.
"""


@pytest.fixture
def bible(tmp_path, monkeypatch):
    monkeypatch.setattr(index, "BIBLE_DIR", tmp_path)
    (tmp_path / "characters").mkdir()
    (tmp_path / "profond").mkdir()
    (tmp_path / "characters" / "x.md").write_text(SHEET, encoding="utf-8")
    (tmp_path / "objets.md").write_text(OBJECTS, encoding="utf-8")
    (tmp_path / "profond" / "secret.md").write_text("## 1. Fin\n\nLa fin.", encoding="utf-8")
    (tmp_path / "style-auteur.md").write_text("## Interdits\n\nx", encoding="utf-8")
    (tmp_path / "characters" / "_template.md").write_text("## 1. Voix\n\nx", encoding="utf-8")
    return tmp_path


def test_character_sheet_keeps_numbered_sections_and_surface_blocks_only(bible):
    ids, docs, metas = index.index_file(bible / "characters" / "x.md", None)
    assert ids == ["x::voix", "x::histoire"]
    voice, history = docs
    assert voice.startswith("[x / Voix]") and "consigne humaine" not in voice
    assert "la narratrice parle peu" in voice and "Judith" not in voice
    assert "Chapeau de section" in history and "Ce que le lecteur sait" in history
    assert "PROFOND" not in history and "personne ne doit lire" not in history
    assert "Note de travail" not in " ".join(docs)


def test_metadata_is_whitelisted(bible):
    _, _, metas = index.index_file(bible / "characters" / "x.md", None)
    assert metas[0] == {"doc_id": "x", "type": "character", "version": 3,
                        "source_file": "characters/x.md", "section": "voix"}
    assert "depends_on" not in metas[0]


def test_reserved_section_is_dropped_by_the_layer_convention(bible):
    ids, _, _ = index.index_file(bible / "objets.md", None)
    assert ids == ["objets::le_cahier"]


def test_firewall_excludes_deep_directory_and_style_sheet(bible):
    assert index.exclu(bible / "profond" / "secret.md")
    assert index.exclu(bible / "style-auteur.md")
    assert not index.exclu(bible / "objets.md")
    files = [p for p in bible.rglob("*.md") if not p.name.startswith("_") and not index.exclu(p)]
    assert sorted(p.name for p in files) == ["objets.md", "x.md"]


def test_slug_and_name_translation():
    assert index.slugify("Voix et expression") == "voix_et_expression"
    assert index.slugify("État narratif courant") == "etat_narratif_courant"
    assert index.traduire_noms("[fiche-judith / Voix]\nJudith et judith") == \
        "[fiche-narratrice / Voix]\nla narratrice et la narratrice"


def test_real_bible_exposes_the_sections_retrieval_asks_for(bible_chroma):
    from factory.retrieval import context as retrieval

    col = bible_chroma.get_collection("auteur")
    for section in retrieval.WRITING_SECTIONS + retrieval.WORLD_SECTIONS:
        assert f"judith::{section}" in col.docs, section
    assert not any("profond" in (m.get("source_file") or "") for m in col.metas.values())
    assert not any("Romane" in d and "morte" in d for d in col.docs.values())
    from factory.paths import BIBLE_DIR
    assert (BIBLE_DIR / "profond").is_dir()
