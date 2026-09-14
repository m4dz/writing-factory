"""The resolution recipe as a series driver: verdicts, positive control,
manifest, refusals (`xp-abliterated-nemo`)."""

import pytest
import yaml

from factory.infra import ollama as llm
from factory.tooling import resolution_xp as xp

RESOLVING = ("Je relis la ligne. Verdict : coquille. Ma mémoire m'a joué un tour, "
             "je n'ai pas rêvé.")
HOLDING = ("Je relis la ligne trois fois. Je ne me souviens pas de l'avoir fait ; l'écart "
           "reste entre ce qui est écrit et ce dont je me souviens.")
NEITHER = "Je relis la ligne et je range le cahier."


@pytest.fixture
def scripted(monkeypatch):
    """A `chat` that answers by condition: the control resolves, the others
    hold, and every call is recorded with the model it was asked for."""
    calls = []

    def chat(system, user, *, model=None, temperature=0.8, num_predict=1200, **_):
        calls.append({"system": system, "user": user, "model": model})
        text = RESOLVING if xp.voice_chunk() in system else HOLDING
        return text, {"gen_toks": 1}

    monkeypatch.setattr(xp, "chat", chat)
    monkeypatch.setattr(llm.client, "tags", lambda *a, **k: [
        {"name": "mistral-nemo:12b-instruct-2407-q8_0", "digest": "sha256:stock"},
        {"name": "hf.co/acme/nemo-abliterated:Q8_0", "digest": "sha256:abl"}])
    return calls


def test_verdict_reads_both_ways():
    assert xp.verdict(RESOLVING)[0] == "RÉSOUT" and "Verdict : coquille" in xp.verdict(RESOLVING)[1]
    assert xp.verdict(HOLDING) == ("TENU", "")
    assert xp.verdict(NEITHER) == ("—", "")


def test_voice_chunk_is_the_indexed_surface_chunk():
    chunk = xp.voice_chunk()
    # The indexer's name translation applies: the first name is never served.
    assert chunk.startswith("[la narratrice / Voix]") and "Squelette d'une entrée" in chunk
    assert "Judith" not in chunk and "PROFOND" not in chunk and "partie double" not in chunk.lower()


def test_series_writes_raw_and_manifest_with_the_answering_model(tmp_path, scripted):
    out = tmp_path / "leg1-U"
    m = xp.run_series(out, model="hf.co/acme/nemo-abliterated", draws=2,
                      temperature=0.7, num_predict=300)
    assert m["model"] == {"name": "hf.co/acme/nemo-abliterated:Q8_0", "digest": "sha256:abl"}
    assert {c["model"] for c in scripted} == {"hf.co/acme/nemo-abliterated:Q8_0"}
    assert len(scripted) == 2 * len(xp.CONDITIONS)
    assert m["control_resolves"] is True and m["verdicts"][xp.CONTROL]["resolves"] == 2
    assert all(v["holds"] == 2 for n, v in m["verdicts"].items() if n != xp.CONTROL)
    assert set(m["timings"]) == {"monotonic_s", "wall_s", "sleep_s"} and m["commit"]
    on_disk = yaml.safe_load((out / "manifest.yaml").read_text(encoding="utf-8"))
    assert on_disk["kind"] == "experiment-series" and on_disk["draws"] == 2
    raw = (out / "raw.md").read_text(encoding="utf-8")
    assert raw.count("| **RÉSOUT** |") == 2 and "Témoin positif : RÉSOUT" in raw
    # The control is the only condition that serves the sheet.
    served_sheet = [c for c in scripted if "[la narratrice / Voix]" in c["system"]]
    assert len(served_sheet) == 2


def test_series_refuses_an_unknown_tag_and_an_empty_control(tmp_path, scripted, monkeypatch):
    with pytest.raises(xp.RecipeError, match="absent d'Ollama"):
        xp.run_series(tmp_path / "x", model="nope:latest", draws=1, temperature=0.7,
                      num_predict=300)
    assert not (tmp_path / "x").exists() and scripted == []
    sheet = tmp_path / "fiche-judith.md"
    deep_only = "---\ndoc_id: judith\n---\n# Judith\n\n## 1. Voix\n\n### [PROFOND]\n\nsecret\n"
    sheet.write_text(deep_only, encoding="utf-8")
    with pytest.raises(xp.RecipeError, match="vide ou absent"):
        xp.voice_chunk(sheet)
    assert xp.main(["--out", str(tmp_path / "y"), "--model", "nope"]) == 1
