"""The refactor invariant: served prompts and assembled chapters do not move.

Each scenario runs the whole graph against the fake model at a fixed seed and is
compared, byte for byte, to the golden files under ``tests/snapshots/<name>/``:

- ``prompts.md``   every (system, user) pair served, in call order;
- ``chapter.md``   the chapter as ``assembly.assembler`` serves it;
- ``warnings.txt`` the pipeline's own trace of what it did.

A diff here is not necessarily a bug: it is a change to what the model sees or
to what the code composes, and it must be intended and named by the change
that carries it. Regenerate with ``make snapshots`` only then.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from factory.pipeline import assembly
from snapshots import scenarios

HERE = Path(__file__).resolve().parent


def _compare(path: Path, produced: str, update: bool) -> None:
    if update:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(produced, encoding="utf-8")
        return
    assert path.exists(), f"missing golden file {path} — run `make snapshots`"
    expected = path.read_text(encoding="utf-8")
    assert produced == expected, (
        f"{path.name} differs from the golden file for {path.parent.name}. "
        "If the change is intended, regenerate with `make snapshots` and "
        "name the change in the openspec proposal."
    )


@pytest.mark.snapshot
@pytest.mark.parametrize("scenario", scenarios.all_scenarios(), ids=lambda s: s.name)
def test_served_prompts_and_chapter_are_frozen(scenario, fake_model, fake_chroma,
                                               quiet_progress, request):
    update = request.config.getoption("--update-snapshots")
    final = scenarios.run(scenario, fake_model)

    prompts = scenarios.render_prompts(fake_model.calls)
    chapter = assembly.assemble(final["repaired"], **scenario.assembly)
    # The render node assembles the same chapter into the state (no file, no
    # voice: the scenario does not ask for rendering).
    assert final["chapter_md"] == chapter and "audio" not in final
    warnings = "\n".join(final.get("warnings") or []) + "\n"

    folder = HERE / scenario.name
    _compare(folder / "prompts.md", prompts, update)
    _compare(folder / "chapter.md", chapter, update)
    _compare(folder / "warnings.txt", warnings, update)

    # The prompts the code kept for the run are the same as what was served.
    served = {u for _, u in final.get("served_prompts") or []}
    assert served <= {c.user for c in fake_model.calls}


@pytest.mark.snapshot
def test_ch7_structure_is_the_stage_structure(fake_model, fake_chroma, quiet_progress):
    """Two entries the same day, anchor in the second only, fall posed by code,
    switch at the second header, audio ending with the fall."""
    sc = scenarios.all_scenarios()[0]
    final = scenarios.run(sc, fake_model)
    assert len(final["repaired"]) == 2
    e1, e2 = final["repaired"]
    assert e1.startswith("Samedi 14.") and e2.startswith("Samedi 14.")
    assert "« Neuf ans aujourd'hui" not in e1 and "« Neuf ans aujourd'hui" in e2
    assert e2.rstrip().endswith("Constat : anniversaire.")
    chapter = assembly.assemble(final["repaired"], **sc.assembly)
    before, after = chapter.split(assembly.SWITCH)
    assert before.count("Samedi 14.") == 1 and after.count("Samedi 14.") == 1
    assert after.split(assembly.AUDIO_END)[0].rstrip().endswith("Constat : anniversaire.")


def _calls(prompts: str) -> list[str]:
    """The served calls of a rendered `prompts.md`, unnumbered, sorted."""
    return sorted(re.split(r"^## call \d+ — ", prompts, flags=re.M)[1:])


@pytest.mark.snapshot
def test_ch7_prepared_serves_the_ch7_prompts_byte_for_byte(fake_model, fake_chroma,
                                                            quiet_progress, tmp_path):
    """Scenario ``ch7-prepared``: compared to ``ch7``'s golden files, never
    written (``--update-snapshots`` does not apply to it). Entry 1 is prepared
    (prepared-entry1): drawn, picked (the first ranked, as the unsplit run
    keeps it) and reviewed in the prep, so the same calls are served, byte for
    byte, in another order — entry 1's review before entry 2's writing."""
    sc = scenarios.all_scenarios()[0]
    final = scenarios.run_prepared(sc, fake_model, tmp_path)
    folder = HERE / "ch7"
    prompts = scenarios.render_prompts(fake_model.calls)
    golden = (folder / "prompts.md").read_text(encoding="utf-8")
    assert prompts != golden and _calls(prompts) == _calls(golden)
    chapter = assembly.assemble(final["repaired"], **sc.assembly)
    assert chapter == (folder / "chapter.md").read_text(encoding="utf-8")
    # The selection's line becomes the owner's pick; every other warning holds.
    warnings = final.get("warnings") or []
    expected = (folder / "warnings.txt").read_text(encoding="utf-8").splitlines()
    picked = [w for w in warnings if "choisi par l'auteur" in w]
    kept = [w for w in expected if w.startswith("entrée 1 : best-of-")]
    assert len(picked) == 1 and len(kept) == 1 and "variant 1 " in picked[0]
    assert sorted(w for w in warnings if w not in picked) == sorted(
        w for w in expected if w not in kept)
    assert final["prepared_from"] == "prep" and final["leader"]["approved"] is True
    assert final["prepare"] is False
