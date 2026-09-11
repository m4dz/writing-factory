"""The refactor invariant: served prompts and assembled chapters do not move.

Each scenario runs the whole graph on the fake model at a fixed seed and is
compared, byte for byte, to the golden files under ``tests/snapshots/<name>/``:

- ``prompts.md``   every (system, user) pair served, in call order;
- ``chapter.md``   the chapter as ``chapitre.assembler`` serves it;
- ``warnings.txt`` the pipeline's own trace of what it did.

A diff here is not necessarily a bug: it is a change to what the model sees or
to what the code composes, and it must be intended and named by the change
that carries it. Regenerate with ``make snapshots`` only then.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from factory.pipeline import assembly as chapitre
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
    chapter = chapitre.assembler(final["repaired"], **scenario.assembly)
    warnings = "\n".join(final.get("warnings") or []) + "\n"

    folder = HERE / scenario.name
    _compare(folder / "prompts.md", prompts, update)
    _compare(folder / "chapter.md", chapter, update)
    _compare(folder / "warnings.txt", warnings, update)

    # The prompts the code kept for the run are the same as what was served.
    served = {u for _, u in final.get("prompts_servis") or []}
    assert served <= {c.user for c in fake_model.calls}


@pytest.mark.snapshot
def test_ch7_structure_is_the_stage_structure(fake_model, fake_chroma, quiet_progress):
    """Two entries the same day, anchor on the second only, fall posed by code,
    switch on the second header, audio ending on the fall."""
    sc = scenarios.all_scenarios()[0]
    final = scenarios.run(sc, fake_model)
    assert len(final["repaired"]) == 2
    e1, e2 = final["repaired"]
    assert e1.startswith("Samedi 14.") and e2.startswith("Samedi 14.")
    assert "« Neuf ans aujourd'hui" not in e1 and "« Neuf ans aujourd'hui" in e2
    assert e2.rstrip().endswith("Constat : anniversaire.")
    chapter = chapitre.assembler(final["repaired"], **sc.assembly)
    before, after = chapter.split(chapitre.BASCULE)
    assert before.count("Samedi 14.") == 1 and after.count("Samedi 14.") == 1
    assert after.split(chapitre.FIN_AUDIO)[0].rstrip().endswith("Constat : anniversaire.")
