"""The run registry: directories, manifests, whitelists, listing order."""

from datetime import datetime

import pytest

from factory import runs
from factory.settings import settings


def test_create_run_writes_a_queued_manifest_with_the_resolved_config(tmp_path):
    run = runs.create_run(7, "anniversaire", seed=5, overrides={"beats_n": 1}, root=tmp_path,
                          now=datetime(2026, 9, 12, 10, 0, 0))
    assert run.id == "20260912-100000-ch07-anniversaire" and runs.RUN_ID.match(run.id)
    assert run.dir == tmp_path / run.id and (run.dir / "manifest.yaml").is_file()
    m = run.manifest
    assert m["kind"] == "run" and m["status"] == "queued" and m["seed"] == 5
    assert m["overrides"] == {"beats_n": 1} and m["config"]["beats_n"] == 1
    assert m["config"]["author_model"] == settings.author_model and m["commit"]
    # Same second, same chapter: a distinct directory, still a valid id.
    again = runs.create_run(7, "anniversaire", seed=6, root=tmp_path,
                            now=datetime(2026, 9, 12, 10, 0, 0))
    assert again.id != run.id and runs.RUN_ID.match(again.id)


def test_overrides_are_whitelisted_and_cast():
    assert runs.validate_overrides({"beats_n": "2", "pruning_enabled": 0}) == \
        {"beats_n": 2, "pruning_enabled": False}
    with pytest.raises(runs.RunError, match="override refusé"):
        runs.validate_overrides({"bible_dir": "/tmp"})
    with pytest.raises(runs.RunError, match="valeur invalide"):
        runs.validate_overrides({"beats_n": "trois"})


def test_listing_is_newest_first_and_ignores_foreign_directories(tmp_path):
    a = runs.create_run(2, "premiere-divergence", seed=1, root=tmp_path,
                        now=datetime(2026, 9, 12, 9, 0, 0))
    b = runs.create_run(7, "anniversaire", seed=2, root=tmp_path,
                        now=datetime(2026, 9, 12, 11, 0, 0))
    (tmp_path / "20260809-ch2-calibration").mkdir()          # a series of step 3, not a run
    (tmp_path / "20260809-ch2-calibration" / "manifest.yaml").write_text("kind: series\n")
    assert [r.id for r in runs.list_runs(tmp_path)] == [b.id, a.id]
    assert runs.latest_run(tmp_path).id == b.id
    assert runs.find_run(a.id, tmp_path).seed == 1
    assert runs.find_run("../etc", tmp_path) is None
    assert runs.find_run("20260912-000000-ch07-nope", tmp_path) is None


def test_record_result_closes_the_manifest_and_writes_prompts_and_lint(tmp_path):
    run = runs.create_run(7, "anniversaire", seed=5, root=tmp_path)
    final = {"metrics": [{"gen_toks": 10, "ctx_need": 0.4}, {"gen_toks": 5, "ctx_truncated": True}],
             "repaired": ["a", "b"], "warnings": ["w"],
             "chapter_md": "Samedi 14. Beau temps.\n\nUne.",
             "audio": None, "coherence": "ok", "plan_report": "fourni"}
    calls = [{"model": "m", "system": "S", "user": "U", "num_predict": 1, "temperature": 0.7,
              "gen_toks": 10, "wall_s": 1.0}]
    runs.record_result(run, final, clocks={"monotonic_s": 1.0, "wall_s": 1.5, "sleep_s": 0.5},
                       calls=calls, collections=["auteur", "auteur"], status="ready")
    m = runs.load_run(run.dir).manifest
    assert m["status"] == "ready" and m["metrics"] == {"calls": 2, "gen_toks": 15,
                                                       "ctx_need_max": 0.4, "ctx_truncated": 1}
    assert m["collections"] == ["auteur"] and m["timings"]["sleep_s"] == 0.5 and m["scenes"] == 2
    assert run.prompts_path.read_text(encoding="utf-8").count("## appel") == 1
    assert (run.dir / "lint.md").read_text(encoding="utf-8").startswith(f"### {run.id}")
    runs.record_result(run, None, clocks={}, calls=None, collections=[], status="error",
                       error="boom")
    assert runs.load_run(run.dir).manifest["error"] == "boom"
