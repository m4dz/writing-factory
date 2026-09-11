"""The ``factory`` command: dispatch, and ``generate`` end to end on the fake
model with the machine nodes switched off."""

import pytest

from factory import cli
from factory.settings import settings


def test_help_and_unknown_command(capsys):
    assert cli.main(["--help"]) == 0
    assert "factory generate" in capsys.readouterr().out
    assert cli.main([]) == 2
    assert cli.main(["nope"]) == 2
    assert "commande inconnue" in capsys.readouterr().err


def test_promote_is_a_placeholder_until_step_6(capsys):
    assert cli.main(["promote", "run-x"]) == 2
    assert "étape 6" in capsys.readouterr().err


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
    assert st["seed"] == 7 and st["render"] is True
    assert st["preflight"] == {"strict": True, "timer": True}
    st = cli._generate_state(p.parse_args(["--skip-preflight", "--no-render"]))
    assert st["preflight"] == {"strict": False, "timer": True} and st["render"] is False
    st = cli._generate_state(p.parse_args(["--brief", "Une entrée.", "--characters", "judith",
                                           "--no-preflight"]))
    assert st["brief"] == "Une entrée." and st["preflight"] is None and "seed" not in st


def test_generate_chapter_7_on_the_fake_model(fake_model, fake_chroma, tmp_path, capsys,
                                              monkeypatch):
    monkeypatch.setattr(settings, "output_dir", settings.output_dir)
    code = cli.main(["generate", "--chapter", "7", "--seed", "424242", "--no-preflight",
                     "--no-render", "--quiet", "--out", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert code == 0
    assert "CHAPITRE (après relecture" in out and "Constat : anniversaire." in out
    assert "PROFILAGE" in out and "appels LLM" in out
    assert settings.output_dir == tmp_path / "out" and not (tmp_path / "out").exists()


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
