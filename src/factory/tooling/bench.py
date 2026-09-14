"""The writer bench: one entry, several models, N draws each, one variable.

Quality campaign, lever 2 (`docs/plans/2026-09-quality-campaign.md`, ADR-0026).
The bench runs the WRITE NODE ALONE on the calibrated reference (chapter 7,
entry 2 by default) for every model named, with the pipeline exactly as it
is (prompts, beats, best-of, bounds, scorers), and records per draw the text,
the call metrics (tok/s, wall, context need), the lint report and the style
score. It swaps models freely: the single-swap rule does not hold for book
runs.

The judge stays the owner's reading: `report.md` carries one empty line per
draw for the manual grid question ("le mouvement déclaré est-il accompli ?").
The figures rank speed and register; they do not decide.

Usage:
  factory bench --models mistral-small:24b,qwen3:14b --draws 3
  factory bench --models a,b --chapter 7 --entry 2 --seed 424242
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

from factory import runs as run_registry
from factory.settings import settings


def _slug(model: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")[:40] or "model"


def _entry_state(spec, entry: int, seed: int) -> dict:
    """The state the write node needs to write ONE entry of a chapter whose
    plan is imposed by the brief (no plan call)."""
    if not spec.imposed_plan:
        raise SystemExit(f"chapitre {spec.chapter} : le banc exige un plan imposé par le "
                         "brief (plan: entries-of-brief) — aucun appel de plan n'est fait")
    if not 1 <= entry <= len(spec.imposed_plan):
        raise SystemExit(f"entrée {entry} : le chapitre {spec.chapter} en compte "
                         f"{len(spec.imposed_plan)}")
    state = spec.state(seed=seed)
    state.update({"plan": list(spec.imposed_plan), "idx": entry - 1,
                  "scenes": [""] * (entry - 1), "metrics": [], "warnings": [],
                  "served_prompts": []})
    return state


def _draw_summary(out: dict, entry: int) -> dict:
    from factory.eval import style
    from factory.eval.lint import analyze

    text = out["scenes"][-1]
    metrics = [m for m in out.get("metrics") or [] if str(m.get("noeud", "")).startswith("write")]
    gen = sum(m.get("gen_toks", 0) for m in metrics)
    wall = sum(m.get("wall_s", 0.0) for m in metrics)
    lint = analyze(text)
    return {
        "text": text,
        "words": len(text.split()),
        "calls": len(metrics),
        "gen_toks": gen,
        "wall_s": round(wall, 1),
        "gen_tok_s": round(gen / wall, 1) if wall else 0.0,
        "ctx_need_max": max((m.get("ctx_need", 0) for m in metrics), default=0),
        "done_length": sum(1 for m in metrics if m.get("done_reason") == "length"),
        "style": style.score(text),
        "lint_failures": [k for k in ("tics_ia", "pastiche", "passe_simple", "etats_mentaux")
                          if lint.get(k)],
        "warnings": [w for w in out.get("warnings") or [] if f"entrée {entry}" in w],
        "served_prompts": list(out.get("served_prompts") or []),
    }


def run_bench(models: list[str], draws: int, *, chapter: int, entry: int, seed: int,
              root: Path | None = None) -> Path:
    from factory.chapter_spec import load_chapter
    from factory.infra import progress
    from factory.infra.ollama import client, unload
    from factory.pipeline.graph import write_node
    from factory.retrieval import context as retrieval

    spec = load_chapter(chapter)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    directory = run_registry.runs_root(root) / f"{stamp}-ch{chapter:02d}-bench"
    directory.mkdir(parents=True)
    manifest = {
        "id": directory.name, "kind": "bench", "chapter": chapter, "entry": entry,
        "models": list(models), "draws": draws, "seeds": [seed + k for k in range(draws)],
        "created": datetime.now().isoformat(timespec="seconds"),
        "commit": run_registry.git_commit(), "config": run_registry.resolved_config(),
        "variable": "author_model", "status": "running", "results": {},
    }
    (directory / "manifest.yaml").write_text(yaml.safe_dump(run_registry._plain(manifest),
                                                             allow_unicode=True, sort_keys=False),
                                             encoding="utf-8")
    original = settings.author_model
    calls: list[dict] = []
    results: dict[str, list[dict]] = {}
    previous = original
    try:
        for model in models:
            if model != previous:
                unload(previous)                 # never two writers warm at once
            settings.author_model = model
            previous = model
            per_model = []
            for k in range(draws):
                s = seed + k
                progress.phase("Banc", f"{model} — tirage {k + 1}/{draws}", i=k + 1, n=draws)
                client.recording = []
                retrieval.clear_routing()
                clocks = run_registry.Clocks()
                out = write_node(_entry_state(spec, entry, s))
                summary = _draw_summary(out, entry)
                summary.update({"model": model, "seed": s, "clocks": clocks.read()})
                calls += [dict(c, bench_model=model, bench_seed=s) for c in client.recording]
                client.recording = None
                per_model.append(summary)
                _write_draw(directory, model, k, summary)
            results[model] = per_model
    finally:
        settings.author_model = original
        client.recording = None
    manifest["results"] = {m: _aggregate(rs) for m, rs in results.items()}
    manifest["status"] = "ready"
    (directory / "manifest.yaml").write_text(yaml.safe_dump(run_registry._plain(manifest),
                                                             allow_unicode=True, sort_keys=False),
                                             encoding="utf-8")
    (directory / "prompts.md").write_text(run_registry.render_prompts(calls), encoding="utf-8")
    (directory / "report.md").write_text(_report(manifest, results), encoding="utf-8")
    return directory


def _aggregate(rows: list[dict]) -> dict:
    n = len(rows) or 1

    def mean(key):
        return round(sum(float(r[key]) for r in rows) / n, 2)

    return {"draws": len(rows), "words": mean("words"), "gen_tok_s": mean("gen_tok_s"),
            "wall_s": mean("wall_s"), "style": mean("style"),
            "style_min": min((r["style"] for r in rows), default=0.0),
            "ctx_need_max": max((r["ctx_need_max"] for r in rows), default=0),
            "done_length": sum(r["done_length"] for r in rows),
            "lint_failures": sum(len(r["lint_failures"]) for r in rows)}


def _write_draw(directory: Path, model: str, k: int, s: dict) -> None:
    front = {key: s[key] for key in ("model", "seed", "words", "calls", "gen_toks", "wall_s",
                                     "gen_tok_s", "ctx_need_max", "done_length", "style",
                                     "lint_failures", "clocks")}
    body = ["---", yaml.safe_dump(front, allow_unicode=True, sort_keys=False).rstrip(), "---",
            "", s["text"], "", "<!-- avertissements -->"]
    body += [f"<!-- {w} -->" for w in s["warnings"]]
    (directory / f"{_slug(model)}-{k + 1}.md").write_text("\n".join(body) + "\n",
                                                          encoding="utf-8")


def _report(manifest: dict, results: dict[str, list[dict]]) -> str:
    lines = [f"# Banc d'écriture — chapitre {manifest['chapter']}, entrée {manifest['entry']}",
             "",
             f"Une variable : le modèle auteur. {manifest['draws']} tirage(s) par modèle, "
             f"graines {manifest['seeds']}, commit `{manifest['commit']}`. Tout le reste "
             "(prompts, beats, best-of, bornes, scorers) est le pipeline tel qu'il est.",
             "",
             "| modèle | tirages | mots | tok/s | mur (s) | style (moy / min) | ctx_need max "
             "| coupes | lint |",
             "|---|---|---|---|---|---|---|---|---|"]
    for model, agg in manifest["results"].items():
        lines.append(f"| `{model}` | {agg['draws']} | {agg['words']} | {agg['gen_tok_s']} | "
                     f"{agg['wall_s']} | {agg['style']} / {agg['style_min']} | "
                     f"{agg['ctx_need_max']} | {agg['done_length']} | {agg['lint_failures']} |")
    lines += ["", "## Lecture debout — le mouvement déclaré est-il accompli ?", "",
              "Une ligne par tirage, à remplir par l'auteur. Le chiffre classe, il ne juge pas.",
              "", "| tirage | style | accompli ? | remarque |", "|---|---|---|---|"]
    for model, rows in results.items():
        for k, r in enumerate(rows, 1):
            lines.append(f"| `{_slug(model)}-{k}` | {r['style']} | | |")
    lines += ["", "## Tirages", ""]
    for model, rows in results.items():
        for k, r in enumerate(rows, 1):
            lines += [f"### {model} — tirage {k} (graine {r['seed']}, style {r['style']}, "
                      f"{r['words']} mots, {r['gen_tok_s']} tok/s)", "", r["text"], ""]
            if r["warnings"]:
                lines += ["<details><summary>avertissements</summary>", ""]
                lines += [f"- {w}" for w in r["warnings"]]
                lines += ["", "</details>", ""]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="factory bench",
                                description="Banc d'écriture : le nœud write seul, sur une "
                                            "entrée de référence, pour plusieurs modèles.")
    p.add_argument("--models", required=True,
                   help="Modèles Ollama à comparer, séparés par des virgules")
    p.add_argument("--draws", type=int, default=settings.xp_draws)
    p.add_argument("--chapter", type=int, default=7)
    p.add_argument("--entry", type=int, default=2)
    p.add_argument("--seed", type=int, default=None,
                   help="Graine du premier tirage (défaut : l'horloge) ; les suivantes +1")
    p.add_argument("--runs-dir", default=None)
    args = p.parse_args(argv)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        p.error("--models : au moins un modèle")
    seed = args.seed if args.seed is not None else int(time.time()) % 10**6
    root = Path(args.runs_dir) if args.runs_dir else None
    directory = run_bench(models, args.draws, chapter=args.chapter, entry=args.entry,
                          seed=seed, root=root)
    print(f"banc : {directory}\n  rapport : {directory / 'report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
