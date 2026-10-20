#!/usr/bin/env python3
"""Recital of the beat instructions, over EVERY drawn variant (kept and rejected).

For each variant of `variants.md`, the highest sentence-to-sentence similarity
(difflib ratio, as `lint.prompt_copy`) against the sentences of the beat's
PROSE instruction and of its NOMINAL form, both read from the brief. A variant
recites when that score is ≥ 0.50 (`PROMPT_COPY_THRESHOLD`). Measuring against
both forms in both arms: a nominal arm that recites its nominal form is not a
win.

Usage, from the factory root:
  .venv/bin/python experiments/runs/20261020-beat-instruction-form/recital.py RUN_DIR [RUN_DIR…]
"""

import difflib
import re
import sys
from pathlib import Path

from factory.chapter_spec.loader import read_entry_brief
from factory.eval.lint import PROMPT_COPY_THRESHOLD, sentences

BRIEF = Path("chapters/07-anniversaire/brief-entree-2.md")
NAMES = ("relève", "découverte", "doute")
HEAD = re.compile(r"^## entrée 2 / (\w+) / variant (\d+)( — RETENU)?$", re.MULTILINE)


def forms() -> dict[str, list[str]]:
    beats = read_entry_brief(BRIEF)["beats"]
    return {n: [s for f in (b[0], b[2]) for s in sentences(f) if len(s.split()) >= 4]
            for n, b in zip(NAMES, beats)}


def best(text: str, refs: list[str]) -> float:
    return max((difflib.SequenceMatcher(None, s.lower(), r.lower()).ratio()
                for s in sentences(text) if len(s.split()) >= 4 for r in refs), default=0.0)


def variants(run: Path):
    t = (run / "variants.md").read_text(encoding="utf-8")
    heads = list(HEAD.finditer(t))
    for i, h in enumerate(heads):
        body = t[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(t)]
        text = body.split("```")[1].strip() if "```" in body else ""
        yield h.group(1), int(h.group(2)), bool(h.group(3)), text


def main() -> int:
    refs = forms()
    for arg in sys.argv[1:]:
        run = Path(arg)
        if not (run / "variants.md").exists():
            print(f"{run.name}: no variants.md (run not ready)")
            continue
        rows = [(beat, k, kept, round(best(text, refs[beat]), 2))
                for beat, k, kept, text in variants(run)]
        recite = [r for r in rows if r[3] >= PROMPT_COPY_THRESHOLD]
        kept = [r for r in recite if r[2]]
        print(f"{run.name}: {len(recite)}/{len(rows)} variants recite "
              f"({len(kept)} kept) — " + " ".join(f"{b[:3]}{k}{'*' if s else ''}={v}"
                                                   for b, k, s, v in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
