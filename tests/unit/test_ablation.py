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
    assert ablation.main([str(experiment), "--runs-dir", str(tmp_path / "runs"),
                          "--arms", "R"]) == 0
    assert "| A1 |" not in capsys.readouterr().out


def test_last_entry_and_litany():
    md = ("Samedi 14. Beau temps.\n\nUne.\n\n<!-- BASCULE -->\n\nSamedi 14. Beau temps.\n\n"
          "Je range. Je range. Je range. Elle dort.\n\n<!-- FIN AUDIO -->\n")
    entry = ablation.last_entry(md)
    assert entry == "Je range. Je range. Je range. Elle dort."
    assert ablation.litany(entry) == 0.75


def test_accumulation_alone_can_be_switched_off(fake_model, fake_chroma, tmp_path):
    """Arm A3: `micro_nodes=false` also drops the drift, the fall and the
    pruning; `accumulation_enabled=false` drops the accumulation only."""
    assert generate(tmp_path, "--chapter", "7") == 0
    assert generate(tmp_path, "--chapter", "7", "--override", "accumulation_enabled=false") == 0
    off, on = runs.list_runs(tmp_path / "runs")
    assert off.manifest["overrides"] == {"accumulation_enabled": False}
    assert settings.accumulation_enabled is True                          # restored

    def calls(run):                     # the accumulate call: 300 tokens, gesture temperature
        return run.prompts_path.read_text(encoding="utf-8").count(
            f"num_predict=300 temperature={settings.gesture_temperature}")

    assert calls(on) > 0 and calls(off) == 0
    for run in (on, off):
        assert "Constat : anniversaire." in run.chapter_path.read_text(encoding="utf-8")


def test_beats_can_see_the_whole_movement(fake_model, fake_chroma, tmp_path):
    """Each beat gets the entry as a map with its own time marked once; off,
    the beat prompts are the production ones (snapshot ch7)."""
    assert generate(tmp_path, "--chapter", "7", "--override", "beats_see_movement=true") == 0
    (run,) = runs.list_runs(tmp_path / "runs")
    assert run.manifest["overrides"] == {"beat_context": "map"}           # former name, aliased
    assert settings.beat_context == "blind"                               # restored
    spec = load_chapter(7).entries[1]
    calls = [p for p in run.prompts_path.read_text(encoding="utf-8").split("## appel")
             if "L'ENTRÉE ENTIÈRE" in p]
    assert len(calls) == 9                                                # 3 beats × best-of-3
    for beat, call in zip([b for b in spec.beats for _ in range(3)], calls):
        assert spec.movement in call and call.count("← CE TEMPS-CI") == 1
        marked = next(line for line in call.splitlines() if "← CE TEMPS-CI" in line)
        assert beat.instruction.split(".")[0] in marked
        assert "COMPORTEMENT DE LA PROSE" not in call                     # no trajectory


def beat_calls(run, marker):
    return [p for p in run.prompts_path.read_text(encoding="utf-8").split("## appel")
            if marker in p]


def test_beats_see_where_they_are_in_the_plan(fake_model, fake_chroma, tmp_path):
    """plan-state-beats: the code marks each time done / current / next and
    serves the current one's end condition; done times by their label only."""
    assert generate(tmp_path, "--chapter", "7", "--override", "beat_context=plan") == 0
    (run,) = runs.list_runs(tmp_path / "runs")
    assert run.manifest["overrides"] == {"beat_context": "plan"}
    assert settings.beat_context == "blind"                               # restored
    spec = load_chapter(7).entries[1]
    calls = beat_calls(run, "Où tu en es :")
    assert len(calls) == 9                                                # 3 beats × best-of-3
    labels = [b.instruction.split(".")[0] for b in spec.beats]
    for n, call in enumerate(calls):
        here = n // 3
        beat = spec.beats[here]
        state = call.split("Où tu en es :")[1].split("\n\n")[0]
        marks = [line.strip()[0] for line in state.strip().splitlines()]
        assert marks == ["✓"] * here + ["→"] + ["○"] * (len(spec.beats) - here - 1)
        assert labels[here] not in state                                  # served below, once
        assert all(labels[k] in state for k in range(len(labels)) if k != here)
        current = next(line for line in state.splitlines() if "→" in line)
        assert current.endswith(f"il finit quand : {beat.ends}") and beat.ends
        assert call.count("finit quand") == 1                             # in the state only
        assert "COMPORTEMENT DE LA PROSE" not in call                     # no trajectory
        user, start = call.split("### début de la réponse")              # v2: answer begun
        assert user.index("DÉJÀ COMMENCÉE") < user.index("CE TEMPS-CI :")  # task read last
        already = user.split("---\n")[1].split("\n---")[0]
        assert start.split("```\n")[1].strip() == already.split("\n\n")[-1].strip()


def test_a_continued_answer_folds_the_system_into_the_question(monkeypatch):
    """nemo's template drops the system prompt when the answer is begun: it
    goes at the head of the question; the begun answer closes the messages."""
    import json

    from factory.infra.ollama import OllamaClient
    from factory.text import FRENCH_GUARD

    sent = {}

    class Response:
        def __init__(self, req):
            sent.update(json.loads(req.data))

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"message": {"content": " la suite."}, "eval_count": 3,
                               "done_reason": "stop"}).encode()

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=0: Response(req))
    client = OllamaClient()
    client.recording = []
    text, _ = client.chat_continue("VOIX", "TÂCHE", "Le début.")
    assert text == "la suite."
    assert sent["messages"] == [
        {"role": "user", "content": f"{FRENCH_GUARD}\n\nVOIX\n\nTÂCHE"},
        {"role": "assistant", "content": "Le début."}]
    (call,) = client.recording
    assert (call["system"], call["user"], call["start"]) == ("VOIX", "TÂCHE", "Le début.")


@pytest.mark.parametrize("value", ["peut-être", "MAP", "plans"])
def test_beat_context_takes_three_values(tmp_path, value):
    with pytest.raises(SystemExit, match="blind | map | plan"):
        generate(tmp_path, "--chapter", "7", "--override", f"beat_context={value}")
