"""The experiment plumbing of `scaffold-ablation`: variant specs, run
overrides and options from the command line, the pre-selection variants, the
text-only render, and the ablation table with its blind reading set."""

import pytest
import yaml

from factory import cli, runs
from factory.chapter_spec import ChapterSpecError, load_chapter, load_variant
from factory.eval import ablation
from factory.settings import settings

CANONICAL = "chapters/07-anniversaire/spec.yaml"


def single_call_variant(tmp_path, repo_root):
    """Chapter 7 with entry 2 written in one call (arm A4): a copy of the
    canonical spec with one line edited, as an experiment writes it."""
    text = (repo_root / CANONICAL).read_text(encoding="utf-8")
    assert text.count("    strategy: beats\n") == 1
    path = tmp_path / "specs" / "a4-single.yaml"
    path.parent.mkdir()
    path.write_text(text.replace("    strategy: beats\n", "    strategy: single\n"),
                    encoding="utf-8")
    return path


def generate(tmp_path, *extra):
    return cli.main(["generate", "--seed", "424242", "--no-preflight", "--no-voice",
                     "--no-narrative-state", "--quiet", "--runs-dir", str(tmp_path / "runs"),
                     *extra])


def test_a_variant_reads_the_canonical_briefs(tmp_path, repo_root):
    variant = load_variant(single_call_variant(tmp_path, repo_root))
    canonical = load_chapter(7)
    assert variant.entries[1].strategy == "single"
    assert variant.brief == canonical.brief                     # pointer resolved in chapters/
    assert variant.entries[1].drift == canonical.entries[1].drift


def test_a_variant_needs_a_canonical_chapter(tmp_path):
    path = tmp_path / "x.yaml"
    path.write_text("chapter: 3\nslug: x\nnarrator: judith\n", encoding="utf-8")
    with pytest.raises(ChapterSpecError, match="chapitre 3"):
        load_variant(path)


def test_generate_from_a_variant_records_it(fake_model, fake_chroma, tmp_path, repo_root):
    path = single_call_variant(tmp_path, repo_root)
    assert generate(tmp_path, "--spec-file", str(path)) == 0
    (run,) = runs.list_runs(tmp_path / "runs")
    spec = run.manifest["spec"]
    assert spec["source"] == str(path) and spec["canonical"].endswith(CANONICAL)
    changed = [line for line in spec["diff"].splitlines()
               if line[:1] in "+-" and line[:3] not in ("+++", "---")]
    assert changed == ["-    strategy: beats", "+    strategy: single"]
    assert (run.dir / "spec.yaml").read_text(encoding="utf-8") == path.read_text(encoding="utf-8")
    beats = [p for p in run.prompts_path.read_text(encoding="utf-8").split("## appel")
             if "write.beat" in p]
    assert beats == []                                          # entry 2 in one call
    assert (repo_root / CANONICAL).read_text(encoding="utf-8").count("strategy: beats") == 1


def test_overrides_and_options_apply_for_the_run_only(fake_model, fake_chroma, tmp_path):
    assert generate(tmp_path, "--chapter", "7", "--override", "beats_n=1",
                    "--override", "pruning_enabled=false", "--option", "micro_nodes=false") == 0
    (run,) = runs.list_runs(tmp_path / "runs")
    assert run.manifest["overrides"] == {"beats_n": 1, "pruning_enabled": False}
    assert run.manifest["config"]["beats_n"] == 1
    assert run.manifest["options"] == {"micro_nodes": False}
    assert run.manifest["variants"] == {"drawn": 3, "with_defects": 0}   # one per beat
    assert settings.beats_n == 3 and settings.pruning_enabled is True     # restored


@pytest.mark.parametrize("flag,pair,message", [
    ("--option", "strategy=single", "option refusée"),
    ("--option", "rag=maybe", "true ou false"),
    ("--override", "bible_dir=/", "override refusé"),
    ("--override", "pruning_enabled=peut-être", "valeur invalide"),
    ("--override", "beats_n", "CLÉ=VALEUR"),
])
def test_bad_pairs_are_refused_before_any_run(tmp_path, flag, pair, message):
    with pytest.raises(SystemExit, match=message):
        generate(tmp_path, "--chapter", "7", flag, pair)
    assert runs.list_runs(tmp_path / "runs") == []


def test_variants_and_text_only_render(fake_model, fake_chroma, tmp_path):
    assert generate(tmp_path, "--chapter", "7") == 0
    (run,) = runs.list_runs(tmp_path / "runs")
    assert run.manifest["variants"]["drawn"] == 9               # 3 beats × best-of-3
    text = (run.dir / "variants.md").read_text(encoding="utf-8")
    assert text.count("— RETENU") == 3
    assert run.chapter_path.is_file() and run.manifest["audio"] is None


def test_ablation_table_and_blind_set(fake_model, fake_chroma, tmp_path, capsys):
    assert generate(tmp_path, "--chapter", "7") == 0
    assert generate(tmp_path, "--chapter", "7", "--override", "beats_n=1") == 0
    newest, oldest = runs.list_runs(tmp_path / "runs")
    experiment = tmp_path / "xp"
    experiment.mkdir()
    (experiment / "manifest.yaml").write_text(
        yaml.safe_dump({"arms": {"R": [oldest.id], "A1": [newest.id]}}), encoding="utf-8")
    assert ablation.main([str(experiment), "--runs-dir", str(tmp_path / "runs"),
                          "--blind", "--seed", "1"]) == 0
    out = capsys.readouterr().out
    assert f"| R | {oldest.id} |" in out and f"| A1 | {newest.id} |" in out
    assert "| R | 1/1 |" in out
    key = yaml.safe_load((experiment / "blind-key.yaml").read_text(encoding="utf-8"))
    assert sorted(v["arm"] for v in key.values()) == ["A1", "R"]
    for tag in key:
        entry = (experiment / "blind" / f"{tag}.md").read_text(encoding="utf-8")
        assert "Samedi 14" not in entry and "<!--" not in entry and len(entry.split()) > 50
    assert "A1" not in (experiment / "blind" / "verdicts.md").read_text(encoding="utf-8")


def test_last_entry_and_litany():
    md = ("Samedi 14. Beau temps.\n\nUne.\n\n<!-- BASCULE -->\n\nSamedi 14. Beau temps.\n\n"
          "Je range. Je range. Je range. Elle dort.\n\n<!-- FIN AUDIO -->\n")
    entry = ablation.last_entry(md)
    assert entry == "Je range. Je range. Je range. Elle dort."
    assert ablation.litany(entry) == 0.75
