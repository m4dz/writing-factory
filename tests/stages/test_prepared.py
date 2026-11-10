"""`factory prepare` and `factory generate --from`, end to end on the fake model.

The owner's answer is the terminal's `input()`; Ollama's `/api/tags` is a
fake body; the chapter directory is a copy, so a rehearsal-day edit can be
simulated without touching `chapters/`.
"""

from __future__ import annotations

import builtins
import shutil

import pytest

from factory import cli, paths, runs
from factory.settings import settings

TAGS = {"models": [{"name": "mistral-nemo:12b-instruct-2407-q8_0", "digest": "sha256:aaaa"},
                   {"name": "qwen2.5:7b-instruct", "digest": "sha256:bbbb"}]}


@pytest.fixture
def stage(tmp_path, monkeypatch, fake_model, fake_chroma, repo_root):
    chapters = tmp_path / "chapters"
    shutil.copytree(repo_root / "chapters", chapters)
    monkeypatch.setattr(paths, "CHAPTERS_DIR", chapters)
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    monkeypatch.setattr(runs, "_ollama_tags", lambda: TAGS)
    return tmp_path / "runs"


def answer(monkeypatch, text: str | None) -> list[str]:
    """The owner's answer at the gate; the prompts asked are recorded."""
    asked: list[str] = []

    def fake_input(prompt=""):
        asked.append(prompt)
        if text is None:
            raise EOFError
        return text

    monkeypatch.setattr(builtins, "input", fake_input)
    return asked


def prepare(root, *extra) -> int:
    return cli.main(["prepare", "--chapter", "7", "--seed", "424242", "--no-preflight",
                     "--quiet", "--runs-dir", str(root), *extra])


def resume(root, token, *extra) -> int:
    return cli.main(["generate", "--from", token, "--no-preflight", "--no-render",
                     "--quiet", "--runs-dir", str(root), *extra])


def _writes(model) -> list:
    return [c for c in model.calls if c.role.startswith("write")]


def test_an_approved_plan_is_prepared_with_its_plan_and_fingerprint(stage, monkeypatch,
                                                                    fake_model, capsys):
    asked = answer(monkeypatch, "o")
    assert prepare(stage) == 0
    out = capsys.readouterr().out
    assert asked and "PLAN À APPROUVER" in out and "factory generate --from" in out
    (run,) = runs.list_runs(stage)
    m = run.manifest
    assert run.status == "prepared" and m["kind"] == "prepared" and run.id.endswith("-prep")
    assert m["leader"]["approved"] is True and m["leader"]["by"] == "owner"
    assert set(m["fingerprint"]) == {"commit", "dirty", "chapter", "config", "models",
                                     "narrative_state"}
    assert m["fingerprint"]["narrative_state"]                      # the prep indexed it
    plan = run.plan_path.read_text(encoding="utf-8")
    assert plan.startswith("# Plan — chapitre 7") and "1. " in plan
    assert (run.dir / "plan-report.md").is_file() and run.checkpoints_path.is_file()
    assert _writes(fake_model) == [] and not run.chapter_path.exists()


@pytest.mark.parametrize("reply", ["n", "", None])
def test_a_refused_plan_is_cancelled_without_a_write_call(stage, monkeypatch, fake_model, reply):
    answer(monkeypatch, reply)
    assert prepare(stage) == 0
    (run,) = runs.list_runs(stage)
    assert run.status == "cancelled" and run.manifest["leader"]["approved"] is False
    assert "fingerprint" not in run.manifest and not run.plan_path.exists()
    assert _writes(fake_model) == []
    # Chapter 7's plan is imposed by the brief: its prep serves no prompt.
    assert run.prompts_path.read_text(encoding="utf-8").startswith("# Prompts servis — 0 ")
    with pytest.raises(SystemExit, match="non préparé"):
        resume(stage, run.id)


def test_two_resumes_make_two_runs_and_leave_the_prepared_run_untouched(stage, monkeypatch,
                                                                         fake_model):
    answer(monkeypatch, "o")
    prepare(stage)
    (prepared,) = runs.list_runs(stage)
    # Every durable file of the prepared run. SQLite's `-shm` is excluded: a
    # read-only reader of a WAL database updates its read marks there; the
    # database and its `-wal` hold the data and are compared.
    def files():
        return {p.name: p.read_bytes() for p in prepared.dir.iterdir()
                if not p.name.endswith("-shm")}

    before = files()
    assert resume(stage, prepared.id, "--seed", "424242") == 0
    assert resume(stage, "latest") == 0
    assert files() == before                        # manifest, checkpoints, plan: untouched
    assert "checkpoints.sqlite" in before
    resumed = [r for r in runs.list_runs(stage) if r.id != prepared.id]
    assert len(resumed) == 2
    for r in resumed:
        assert r.status == "ready" and r.manifest["prepared_from"] == prepared.id
        assert r.manifest["prepared_seed"] == 424242
        assert r.manifest["fingerprint"] == prepared.manifest["fingerprint"]
        assert r.plan_path.read_bytes() == prepared.plan_path.read_bytes()
        assert r.checkpoints_path.is_file()
        assert not r.prompts_path.read_text(encoding="utf-8").startswith("# Prompts servis — 0 ")
    assert runs.find_run(prepared.id, stage).status == "prepared"
    pinned = next(r for r in resumed if r.seed == 424242)
    assert pinned.manifest["seed"] == 424242
    # Without --seed, the stage draws its own; the prepared seed stays recorded.
    other = next(r for r in resumed if r is not pinned)
    assert other.manifest["seed"] == other.seed


def test_a_rehearsal_day_edit_refuses_the_resume_before_any_model_call(stage, monkeypatch,
                                                                        fake_model, capsys):
    answer(monkeypatch, "o")
    prepare(stage)
    (prepared,) = runs.list_runs(stage)
    brief = paths.CHAPTERS_DIR / "07-anniversaire" / "brief.md"
    brief.write_text(brief.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    fake_model.calls.clear()
    assert resume(stage, prepared.id) == 1
    assert "brief.md" in capsys.readouterr().err
    run = next(r for r in runs.list_runs(stage) if r.id != prepared.id)
    assert run.status == "error" and "empreinte refusée" in run.manifest["error"]
    assert "brief.md" in run.manifest["error"] and fake_model.calls == []
    assert runs.find_run(prepared.id, stage).status == "prepared"


def test_resume_refuses_overrides_and_unknown_runs(stage):
    with pytest.raises(SystemExit, match="--override"):
        resume(stage, "latest", "--override", "beats_n=1")
    with pytest.raises(SystemExit, match="aucun run préparé"):
        resume(stage, "latest")
    with pytest.raises(SystemExit, match="inconnu"):
        resume(stage, "20990101-000000-ch07-prep")
    with pytest.raises(SystemExit, match="invalide"):
        resume(stage, "../etc")


def test_prepare_overrides_hold_for_every_resume(stage, monkeypatch, fake_model):
    answer(monkeypatch, "o")
    prepare(stage, "--override", "beats_n=1")
    (prepared,) = runs.list_runs(stage)
    assert prepared.manifest["fingerprint"]["config"]["beats_n"] == 1
    assert resume(stage, prepared.id) == 0
    run = next(r for r in runs.list_runs(stage) if r.id != prepared.id)
    assert run.overrides == {"beats_n": 1} and run.manifest["config"]["beats_n"] == 1
