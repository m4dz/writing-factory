"""The prepared-plan fingerprint, falsified both ways (doctrine 4).

A resume with nothing changed passes; one changed configuration key, one
edited chapter file, one differing model digest (fake `/api/tags`), one
missing narrative-state chunk, uncommitted code each refuse and name the
item. The chapter directory is a copy: `chapters/` is never edited.
"""

from __future__ import annotations

import shutil

import pytest

from factory import paths, runs
from factory.retrieval import context as retrieval
from factory.settings import settings

DIGESTS = {"mistral-nemo:12b-instruct-2407-q8_0": "sha256:aaaa",
           "qwen2.5:7b-instruct": "sha256:bbbb"}


@pytest.fixture
def tags(monkeypatch):
    """A fake `/api/tags` body, editable by the test."""
    body = {"models": [{"name": n, "model": n, "digest": d} for n, d in DIGESTS.items()]}
    monkeypatch.setattr(runs, "_ollama_tags", lambda: body)
    return body


@pytest.fixture
def prepared(tmp_path, monkeypatch, fake_chroma, tags, repo_root):
    """A prepared chapter-7 run whose fingerprint went through the manifest."""
    chapters = tmp_path / "chapters"
    shutil.copytree(repo_root / "chapters", chapters)
    monkeypatch.setattr(paths, "CHAPTERS_DIR", chapters)
    retrieval._collection().upsert(ids=[runs.narrative_chunk_id(7)],
                                   documents=["[la narratrice / État narratif courant] x"],
                                   metadatas=[{"chapter": 7}], embeddings=[[0.0] * 768])
    run = runs.create_run(7, "prep", seed=1, root=tmp_path / "runs")
    runs.write_manifest(run, fingerprint=runs.fingerprint(run, STATE))
    return runs.load_run(run.dir)               # read back from the YAML


STATE = {"narrative_state_path": "generated/narrative-state/ch-07.md"}


def _refusal(run) -> runs.FingerprintError:
    with pytest.raises(runs.FingerprintError) as caught:
        runs.check_fingerprint(run, STATE)
    return caught.value


def test_nothing_changed_passes(prepared):
    fp = prepared.manifest["fingerprint"]
    assert fp["models"] == {**DIGESTS} and fp["narrative_state"]
    assert {"spec.yaml", "brief.md"} <= set(fp["chapter"])
    runs.check_fingerprint(prepared, STATE)


def test_a_changed_config_key_refuses_and_names_it(prepared, monkeypatch):
    monkeypatch.setattr(settings, "beats_n", settings.beats_n + 1)
    err = _refusal(prepared)
    assert err.items == ["config.beats_n"] and "beats_n" in str(err)


def test_an_edited_chapter_file_refuses_and_names_it(prepared):
    brief = paths.CHAPTERS_DIR / "07-anniversaire" / "brief.md"
    brief.write_text(brief.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    err = _refusal(prepared)
    assert err.items == ["chapter"] and "brief.md" in str(err)


def test_a_repulled_model_refuses_and_names_it(prepared, tags):
    tags["models"][0]["digest"] = "sha256:cccc"
    err = _refusal(prepared)
    name = "mistral-nemo:12b-instruct-2407-q8_0"
    assert err.items == [f"models.{name}"] and name in str(err)
    tags["models"].pop(0)
    assert "absent d'Ollama" in str(_refusal(prepared))


def test_a_missing_narrative_chunk_refuses_and_names_it(prepared):
    retrieval._collection().delete(ids=[runs.narrative_chunk_id(7)])
    err = _refusal(prepared)
    assert err.items == ["narrative_state"] and "absent de Chroma" in str(err)


def test_uncommitted_code_refuses(prepared, monkeypatch):
    monkeypatch.setattr(runs, "code_dirty", lambda: "0" * 64)
    assert _refusal(prepared).items == ["dirty"]


def test_ollama_unreachable_refuses(prepared, monkeypatch):
    monkeypatch.setattr(runs, "_ollama_tags", lambda: (_ for _ in ()).throw(OSError("down")))
    err = _refusal(prepared)
    assert err.items == ["models"] and "injoignable" in str(err)


def test_a_run_without_fingerprint_is_refused(tmp_path):
    run = runs.create_run(7, "x", seed=1, root=tmp_path)
    assert _refusal(run).items == ["fingerprint"]
