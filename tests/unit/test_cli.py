"""The ``factory`` command: dispatch, and ``generate`` end to end against the
fake model with the machine nodes switched off."""

import pytest

from factory import cli
from factory.settings import settings


def test_help_and_unknown_command(capsys):
    assert cli.main(["--help"]) == 0
    assert "factory generate" in capsys.readouterr().out
    assert cli.main([]) == 2
    assert cli.main(["nope"]) == 2
    assert "commande inconnue" in capsys.readouterr().err


def test_promote_refuses_an_unknown_run(capsys):
    assert cli.main(["promote", "run-x"]) == 1
    assert "run inconnu" in capsys.readouterr().err


def test_eval_requires_a_known_tool(capsys):
    assert cli.main(["eval"]) == 2
    assert cli.main(["eval", "score"]) == 2


def test_eval_lint_self_test_passes_on_the_reference_excerpts(capsys):
    assert cli.main(["eval", "lint", "--references"]) == 0
    assert "AUTO-TEST OK" in capsys.readouterr().out


def test_generate_refuses_a_chapter_without_spec():
    with pytest.raises(SystemExit, match="chapitre 3"):
        cli.main(["generate", "--chapter", "3", "--no-preflight", "--no-render", "--quiet"])


def test_generate_state_carries_the_machine_requests():
    p = cli._generate_parser()
    st = cli._generate_state(p.parse_args(["--seed", "7"]))
    assert st["seed"] == 7 and st["render"] is True and st["narrative_state"] is True
    assert st["preflight"] == {"strict": True, "timer": True}
    st = cli._generate_state(p.parse_args(["--skip-preflight", "--no-render",
                                           "--no-narrative-state"]))
    assert st["preflight"] == {"strict": False, "timer": True} and st["render"] is False
    assert st["narrative_state"] is False
    st = cli._generate_state(p.parse_args(["--brief", "Une entrée.", "--characters", "judith",
                                           "--no-preflight"]))
    assert st["brief"] == "Une entrée." and st["preflight"] is None and "seed" not in st


def test_generate_chapter_7_on_the_fake_model(fake_model, fake_chroma, tmp_path, capsys):
    code = cli.main(["generate", "--chapter", "7", "--seed", "424242", "--no-preflight",
                     "--no-render", "--no-narrative-state", "--quiet",
                     "--runs-dir", str(tmp_path / "runs")])
    out = capsys.readouterr().out
    assert code == 0
    assert "CHAPITRE (après relecture" in out and "Constat : anniversaire." in out
    assert "PROFILAGE" in out and "appels LLM" in out
    from factory import runs
    (run,) = runs.list_runs(tmp_path / "runs")
    assert run.chapter == 7 and run.seed == 424242 and run.status == "ready"
    assert run.prompts_path.is_file() and (run.dir / "lint.md").is_file()
    assert not run.chapter_path.exists()                                # --no-render


def test_generate_several_chapters_back_to_back(fake_model, fake_chroma, tmp_path, monkeypatch,
                                                capsys):
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    code = cli.main(["generate", "--chapters", "2,7", "--seed", "424242", "--no-preflight",
                     "--quiet", "--runs-dir", str(tmp_path / "runs")])
    assert code == 0
    from factory import runs
    listed = runs.list_runs(tmp_path / "runs")
    assert [r.chapter for r in listed] == [7, 2] and all(r.status == "ready" for r in listed)
    assert all(r.chapter_path.is_file() for r in listed)               # rendered chapter, no voice
    assert (tmp_path / "generated" / "narrative-state" / "ch-02.md").is_file()
    assert (tmp_path / "generated" / "narrative-state" / "ch-07.md").is_file()
    assert cli.parse_chapters("1-3,7") == [1, 2, 3, 7]
    with pytest.raises(SystemExit, match="chapitre 3"):
        cli.main(["generate", "--chapters", "3,7", "--no-preflight", "--quiet",
                  "--runs-dir", str(tmp_path / "runs")])
    assert len(runs.list_runs(tmp_path / "runs")) == 2        # the series was refused whole


def test_promote_copies_the_chapter_into_the_scenes_and_indexes_it(fake_model, fake_chroma,
                                                                    tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(settings, "runs_dir", tmp_path / "runs")
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    bible = tmp_path / "bible"
    bible.mkdir()
    monkeypatch.setattr(settings, "bible_dir", bible)
    from factory.retrieval import indexer
    monkeypatch.setattr(indexer, "BIBLE_DIR", bible)
    assert cli.main(["promote", "20260912-000000-ch07-nope"]) == 1
    assert cli.main(["generate", "--chapter", "7", "--seed", "1", "--no-preflight",
                     "--no-narrative-state", "--quiet"]) == 0
    from factory import runs
    (run,) = runs.list_runs()
    assert cli.main(["promote", run.id]) == 0
    target = bible / "scenes" / f"ch-07-{run.id}.md"
    text = target.read_text(encoding="utf-8")
    assert text.startswith("---\ndoc_id: scene-ch07\ntype: scene\nchapter: 7\n")
    assert "Constat : anniversaire." in text
    got = fake_chroma.get_collection("auteur").get(where={"type": "scene"}, include=["metadatas"])
    assert got["ids"] == ["scene-ch07::preambule::ch07"]
    assert got["metadatas"][0]["source_file"] == f"scenes/ch-07-{run.id}.md"
    assert got["metadatas"][0]["chapter"] == 7 and "promoted_from" not in got["metadatas"][0]
    assert cli.main(["promote", run.id]) == 1                            # already promoted
    assert cli.main(["promote", run.id, "--force", "--no-index"]) == 0
    assert runs.find_run(run.id).manifest["promoted_to"] == str(target)


def test_doctor_reports_each_probe(monkeypatch, capsys):
    from factory.infra import preflight as pf

    monkeypatch.setattr(pf, "report", lambda: "disque 100 GB libres")
    monkeypatch.setattr(pf, "preflight", lambda **k: ["swap tiède"])
    monkeypatch.setattr(cli, "_http_ok", lambda url, timeout=5.0: (
        (True, '{"models": [{"name": "mistral-nemo:12b-instruct-2407-q8_0"}]}')
        if "api/tags" in url else (False, "refused")))
    code = cli.main(["doctor"])
    out = capsys.readouterr().out
    assert code == 1
    assert "✓ disque 100 GB libres" in out and "⚠ swap tiède" in out
    assert "✓ modèle auteur" in out and "✗ modèle QA" in out
    assert "✗ ChromaDB" in out and "problème(s) bloquant(s)" in out
