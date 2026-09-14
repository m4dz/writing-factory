"""The writer bench: the write node alone, per model, draws recorded as data."""

import yaml

from factory import cli
from factory.settings import settings


def test_bench_writes_one_directory_with_manifest_report_and_draws(fake_model, fake_chroma,
                                                                   quiet_progress, tmp_path,
                                                                   capsys):
    before = settings.author_model
    code = cli.main(["bench", "--models", "alpha:12b, beta:24b", "--draws", "2",
                     "--seed", "100", "--runs-dir", str(tmp_path)])
    assert code == 0 and settings.author_model == before
    (directory,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    assert directory.name.endswith("-ch07-bench")
    m = yaml.safe_load((directory / "manifest.yaml").read_text(encoding="utf-8"))
    assert m["kind"] == "bench" and m["variable"] == "author_model" and m["status"] == "ready"
    assert m["models"] == ["alpha:12b", "beta:24b"] and m["seeds"] == [100, 101]
    assert set(m["results"]) == {"alpha:12b", "beta:24b"}
    assert m["results"]["alpha:12b"]["draws"] == 2 and m["results"]["alpha:12b"]["style"] > 0
    draws = sorted(p.name for p in directory.glob("*-[12].md"))
    assert draws == ["alpha-12b-1.md", "alpha-12b-2.md", "beta-24b-1.md", "beta-24b-2.md"]
    text = (directory / "beta-24b-2.md").read_text(encoding="utf-8")
    assert text.startswith("---\nmodel: beta:24b\nseed: 101\n") and "Je rentre" in text
    report = (directory / "report.md").read_text(encoding="utf-8")
    assert "| `alpha:12b` | 2 |" in report and "| `beta-24b-2` |" in report
    assert "le mouvement déclaré est-il accompli" in report
    prompts = (directory / "prompts.md").read_text(encoding="utf-8")
    assert prompts.count("## appel") == len(fake_model.calls)
    # The bench is not a run: the registry and the API ignore it.
    from factory import runs
    assert runs.list_runs(tmp_path) == []
    assert "banc :" in capsys.readouterr().out


def test_bench_refuses_a_chapter_without_imposed_plan(fake_model, fake_chroma, quiet_progress,
                                                      tmp_path):
    import pytest

    with pytest.raises(SystemExit, match="plan imposé"):
        cli.main(["bench", "--models", "a", "--draws", "1", "--chapter", "2",
                  "--runs-dir", str(tmp_path)])
    with pytest.raises(SystemExit, match="en compte 2"):
        cli.main(["bench", "--models", "a", "--draws", "1", "--entry", "3",
                  "--runs-dir", str(tmp_path)])
