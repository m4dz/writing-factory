#!/usr/bin/env python3
"""Recipe of the scaffold-ablation runs: 5 arms x 3 seeds, interleaved by seed.

Resumable: a (seed, arm) pair with a `ready` run in the manifest is skipped.
A preflight refusal is not a result: the run is listed under `excluded` with
its reason, and the same pair is retried after a pause (runbook §0: wait for
macOS maintenance to fall back). Any other failure is kept in its arm, as
material (doctrine 13).

Usage, from the factory root:
  caffeinate -is .venv/bin/python experiments/runs/20261018-scaffold-ablation/run.py
"""

import subprocess
import sys
import time
from pathlib import Path

import yaml

X = Path(__file__).resolve().parent
RUNS = X / "runs"
ARMS = {
    "R": ["--chapter", "7"],
    "A1": ["--chapter", "7", "--override", "beats_n=1"],
    "A2": ["--chapter", "7", "--override", "pruning_enabled=false"],
    "A3": ["--chapter", "7", "--option", "micro_nodes=false"],
    "A4": ["--spec-file", str(X / "specs" / "a4-single.yaml")],
}
PAUSE_S, MAX_REFUSALS = 120, 30


def manifest() -> dict:
    return yaml.safe_load((X / "manifest.yaml").read_text(encoding="utf-8"))


def save(data: dict) -> None:
    (X / "manifest.yaml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                                     encoding="utf-8")


def run_status(run_id: str) -> tuple[str, int]:
    m = yaml.safe_load((RUNS / run_id / "manifest.yaml").read_text(encoding="utf-8"))
    return str(m.get("status")), int(m.get("seed") or 0)


def done(data: dict, arm: str, seed: int) -> bool:
    return any(run_status(r) == ("ready", seed) for r in data["arms"][arm])


def main() -> int:
    data = manifest()
    for seed in data["seeds"]:
        for arm, extra in ARMS.items():
            if done(data, arm, seed):
                continue
            for _ in range(MAX_REFUSALS):
                before = set(p.name for p in RUNS.iterdir()) if RUNS.exists() else set()
                log = X / "logs" / f"{seed}-{arm}.log"
                print(f"=== {time.strftime('%H:%M:%S')} seed {seed} arm {arm}", flush=True)
                code = subprocess.call(
                    [".venv/bin/factory", "generate", *extra, "--seed", str(seed),
                     "--no-voice", "--quiet", "--runs-dir", str(RUNS)],
                    stdout=log.open("w"), stderr=subprocess.STDOUT)
                new = sorted(set(p.name for p in RUNS.iterdir()) - before)
                run_id = new[-1] if new else ""
                refused = "Préflight refusé" in log.read_text(encoding="utf-8")
                print(f"    exit {code} run {run_id}{' (preflight refused)' if refused else ''}",
                      flush=True)
                data = manifest()
                if refused:
                    data.setdefault("excluded", []).append(
                        {"run": run_id, "arm": arm, "seed": seed, "reason": "preflight refused"})
                    save(data)
                    time.sleep(PAUSE_S)
                    continue
                if run_id:
                    data["arms"][arm].append(run_id)
                    save(data)
                break
            else:
                print(f"    gave up on seed {seed} arm {arm}: preflight kept refusing", flush=True)
                return 1
    print(f"=== {time.strftime('%H:%M:%S')} done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
