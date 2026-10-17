#!/usr/bin/env python3
"""Compare the arms of an experiment, run by run (openspec `scaffold-ablation`).

The experiment manifest maps each arm to its runs:

    arms:
      R:  [20261018-101500-ch07-anniversaire, ...]
      A1: [...]

For every run, the LAST entry of the chapter (entry 2 of chapter 7) is read
with the same deterministic checks the best-of selection uses, on the final
text; the pre-selection variants are counted from the run manifest. Counting
is not reading (doctrine 3): the table is a veto, the verdict is the owner's,
read blind with `--blind`.

Usage:
  factory eval ablation experiments/runs/20261018-scaffold-ablation
  factory eval ablation experiments/runs/20261018-scaffold-ablation --blind
"""

from __future__ import annotations

import argparse
import random
import re
import sys
from pathlib import Path

import yaml

from factory import runs as run_registry
from factory.pipeline import graph

HEADER = re.compile(r"^[A-ZÉ][a-zéèêûôî]+ \d{1,2}\. [^\n]*\.$", re.MULTILINE)
MARKER = re.compile(r"<!--.*?-->", re.DOTALL)
SENTENCE = re.compile(r"[^.!?…]+[.!?…]+")
PRUNED = re.compile(r"pruning : (\d+) phrase")

CHECKS = {
    "resolves": graph._BEAT_RESOLVES,
    "dismisses": graph._BEAT_DISMISS,
    "recursion": graph._BEAT_RECURSION,
    "presence": graph._BEAT_PRESENCE,
    "restarts": graph._BEAT_WAKING,
}


def last_entry(chapter_md: str) -> str:
    """The text of the last dated entry, markers removed, header excluded."""
    text = MARKER.sub("", chapter_md)
    heads = list(HEADER.finditer(text))
    body = text[heads[-1].end():] if heads else text
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def litany(text: str) -> float:
    """Share of sentences opening on the most frequent two-word start."""
    starts = [" ".join(s.split()[:2]).lower() for s in SENTENCE.findall(text) if s.split()]
    if len(starts) < 4:
        return 0.0
    top = max(starts.count(s) for s in set(starts))
    return round(top / len(starts), 2)


def measure(run: run_registry.Run) -> dict:
    manifest = run.manifest
    text = run.chapter_path.read_text(encoding="utf-8") if run.chapter_path.is_file() else ""
    entry = last_entry(text) if text else ""
    row = {"run": run.id, "status": run.status, "words": len(entry.split())}
    for name, check in CHECKS.items():
        row[name] = len(check.findall(entry))
    row["decor"] = len(graph.material_forbidden(entry, run.chapter))
    row["litany"] = litany(entry)
    variants = manifest.get("variants") or {}
    row["variants"] = f"{variants.get('with_defects', 0)}/{variants.get('drawn', 0)}"
    pruned = [int(m.group(1)) for w in manifest.get("warnings") or []
              for m in [PRUNED.search(str(w))] if m]
    row["pruned"] = sum(pruned)
    timings = manifest.get("timings") or {}
    row["wall_s"] = timings.get("wall_s", "")
    row["entry"] = entry
    return row


COLUMNS = ("run", "words", "resolves", "dismisses", "presence", "recursion", "restarts",
           "decor", "litany", "variants", "pruned", "wall_s")


def table(arms: dict[str, list[dict]]) -> str:
    out = ["| arm | " + " | ".join(COLUMNS) + " |",
           "|" + "---|" * (len(COLUMNS) + 1)]
    for arm, rows in arms.items():
        for r in rows:
            out.append(f"| {arm} | " + " | ".join(str(r.get(c, "")) for c in COLUMNS) + " |")
    out.append("")
    out.append("| arm | runs | veto defects (final) | mean words | mean litany |")
    out.append("|---|---|---|---|---|")
    for arm, rows in arms.items():
        ok = [r for r in rows if r["status"] == "ready"]
        defects = sum(r["resolves"] + r["dismisses"] + r["presence"] + r["recursion"]
                      + r["restarts"] + r["decor"] for r in ok)
        words = round(sum(r["words"] for r in ok) / len(ok)) if ok else 0
        lit = round(sum(r["litany"] for r in ok) / len(ok), 2) if ok else 0
        out.append(f"| {arm} | {len(ok)}/{len(rows)} | {defects} | {words} | {lit} |")
    return "\n".join(out) + "\n"


def blind(experiment: Path, arms: dict[str, list[dict]], seed: int) -> Path:
    """Shuffled entries under neutral ids; the key is written apart."""
    rows = [(arm, r) for arm, rs in arms.items() for r in rs if r["entry"]]
    random.Random(seed).shuffle(rows)
    out = experiment / "blind"
    out.mkdir(exist_ok=True)
    key, sheet = {}, ["# Verdicts — lecture à l'aveugle", "",
                      "Une ligne par entrée : le mouvement déclaré est-il accompli ? "
                      "(oui / non / partiel), puis une note libre.", ""]
    for n, (arm, r) in enumerate(rows, 1):
        tag = f"E{n:02d}"
        (out / f"{tag}.md").write_text(r["entry"] + "\n", encoding="utf-8")
        key[tag] = {"arm": arm, "run": r["run"]}
        sheet.append(f"- {tag} : ")
    (out / "verdicts.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    key_path = experiment / "blind-key.yaml"
    key_path.write_text(yaml.safe_dump(key, sort_keys=True), encoding="utf-8")
    return key_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="factory eval ablation")
    p.add_argument("experiment", help="Experiment directory holding manifest.yaml (arms)")
    p.add_argument("--runs-dir", default=None, help="Run root (default: settings.runs_dir)")
    p.add_argument("--blind", action="store_true", help="Write the blind reading set")
    p.add_argument("--seed", type=int, default=None, help="Shuffle seed for --blind")
    args = p.parse_args(argv)
    experiment = Path(args.experiment)
    data = yaml.safe_load((experiment / "manifest.yaml").read_text(encoding="utf-8")) or {}
    root = Path(args.runs_dir) if args.runs_dir else None
    arms: dict[str, list[dict]] = {}
    for arm, ids in (data.get("arms") or {}).items():
        arms[arm] = []
        for run_id in ids or []:
            run = run_registry.find_run(run_id, root)
            if run is None:
                print(f"run introuvable : {run_id}", file=sys.stderr)
                return 1
            arms[arm].append(measure(run))
    print(table(arms))
    if args.blind:
        seed = args.seed if args.seed is not None else random.randrange(1, 10**6)
        key = blind(experiment, arms, seed)
        print(f"lecture à l'aveugle : {experiment / 'blind'} (clé : {key}, graine {seed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
