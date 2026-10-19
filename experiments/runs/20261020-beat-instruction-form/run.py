#!/usr/bin/env python3
"""Recipe of the beat-instruction-form runs: arms R (prose) and F (nominal) x 3 seeds.

One variable: the served form of the beats. nemo, `beat_context=plan` in both
arms. Models are unloaded before each run (runbook: one warm LLM).

Resumable: a (seed, arm) pair with a `ready` run in the manifest is skipped.
A preflight refusal is not a result: the run is listed under `excluded` with
its reason, and the same pair is retried after a pause (runbook §0). Any
other failure is kept in its arm, as material (doctrine 13).

Usage, from the factory root:
  caffeinate -is .venv/bin/python experiments/runs/20261020-beat-instruction-form/run.py
  caffeinate -is .venv/bin/python experiments/runs/20261020-beat-instruction-form/run.py --smoke
"""

import subprocess
import sys
import time
from pathlib import Path

import yaml

X = Path(__file__).resolve().parent
RUNS = X / "runs"
SMOKE = X / "smoke"
AUTHOR = "mistral-nemo:12b-instruct-2407-q8_0"
FORMS = {"R": "prose", "F": "nominal"}
SMOKE_ARMS = ("F",)
PAUSE_S, MAX_REFUSALS = 120, 30


def manifest() -> dict:
    return yaml.safe_load((X / "manifest.yaml").read_text(encoding="utf-8"))


def save(data: dict) -> None:
    (X / "manifest.yaml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                                     encoding="utf-8")


def run_status(runs: Path, run_id: str) -> tuple[str, int]:
    m = yaml.safe_load((runs / run_id / "manifest.yaml").read_text(encoding="utf-8"))
    return str(m.get("status")), int(m.get("seed") or 0)


def done(runs: Path, ids: list[str], seed: int) -> bool:
    return any(run_status(runs, r) == ("ready", seed) for r in ids)


def unload_all() -> None:
    for tag in (AUTHOR, "qwen2.5:7b-instruct"):
        subprocess.call(["ollama", "stop", tag], stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)


def draw(arm: str, seed: int, runs: Path) -> tuple[str, bool]:
    """One generation; returns (run id, refused by preflight)."""
    runs.mkdir(parents=True, exist_ok=True)
    before = set(p.name for p in runs.iterdir())
    log = X / "logs" / f"{runs.name}-{seed}-{arm}.log"
    print(f"=== {time.strftime('%H:%M:%S')} seed {seed} arm {arm}", flush=True)
    unload_all()
    code = subprocess.call(
        [".venv/bin/factory", "generate", "--chapter", "7",
         "--override", "beat_context=plan", "--override", f"beat_form={FORMS[arm]}",
         "--seed", str(seed), "--no-voice", "--quiet", "--runs-dir", str(runs)],
        stdout=log.open("w"), stderr=subprocess.STDOUT)
    new = sorted(set(p.name for p in runs.iterdir()) - before)
    run_id = new[-1] if new else ""
    refused = "Préflight refusé" in log.read_text(encoding="utf-8")
    print(f"    exit {code} run {run_id}{' (preflight refused)' if refused else ''}", flush=True)
    return run_id, refused


def loop(data: dict, key: str, runs: Path, pairs: list[tuple[int, str]]) -> int:
    for seed, arm in pairs:
        if done(runs, data[key][arm], seed):
            continue
        for _ in range(MAX_REFUSALS):
            run_id, refused = draw(arm, seed, runs)
            data = manifest()
            if refused:
                data.setdefault("excluded", []).append(
                    {"run": run_id, "arm": arm, "seed": seed, "reason": "preflight refused"})
                save(data)
                time.sleep(PAUSE_S)
                continue
            if run_id:
                data[key][arm].append(run_id)
                save(data)
            break
        else:
            print(f"    gave up on seed {seed} arm {arm}: preflight kept refusing", flush=True)
            return 1
    unload_all()
    print(f"=== {time.strftime('%H:%M:%S')} done", flush=True)
    return 0


def main() -> int:
    data = manifest()
    if "--smoke" in sys.argv:
        seed = data["smoke"]["seed"]
        arms = [a for a in sys.argv[2:] if a in SMOKE_ARMS] or list(SMOKE_ARMS)
        return loop(data, "smoke_runs", SMOKE, [(seed, arm) for arm in arms])
    arms = list(FORMS)
    return loop(data, "arms", RUNS, [(s, a) for s in data["seeds"] for a in arms])


if __name__ == "__main__":
    sys.exit(main())
