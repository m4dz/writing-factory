"""The deterministic lint, frozen on the runs it was calibrated against.

``lint_style.analyse`` has no model behind it: its report on a given text is a
pure function. Every failed run in `experiments/journal/` and the chapter 7 rehearsal
files are run through it and the reports are compared to golden files. This is
the falsification baseline in both directions: a detector that starts firing
on a run it accepted, or stops firing on one it flagged, shows up here.
"""

from pathlib import Path

import pytest
from lint_style import analyse, rapport

REPO = Path(__file__).resolve().parents[2]
GOLDEN = REPO / "tests" / "snapshots" / "lint"

SOURCES = (sorted(p for p in REPO.glob("experiments/journal/*.md") if p.name != "README.md")
           + sorted(REPO.glob("experiments/runs/20260826-ch7-rehearsal/*.md")))


@pytest.mark.snapshot
@pytest.mark.parametrize("source", SOURCES, ids=lambda p: p.name)
def test_lint_report_is_frozen(source, request):
    produced = rapport(analyse(source.read_text(encoding="utf-8")), titre=source.name)
    golden = GOLDEN / (source.name + ".txt")
    if request.config.getoption("--update-snapshots"):
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(produced, encoding="utf-8")
        return
    assert golden.exists(), f"missing {golden} — run `make snapshots`"
    assert produced == golden.read_text(encoding="utf-8")


def test_the_corpus_is_not_empty():
    """A snapshot over zero files is green by construction (doctrine 4)."""
    assert len(SOURCES) >= 30
