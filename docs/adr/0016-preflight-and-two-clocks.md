# ADR-0016 — Preflight gates on causes measured, not proxies; two clocks per run

Date: 2026-08-06 to 2026-08-25. Status: accepted.

## Context

Every incident of the development was a MACHINE incident: kernel panics from
a disk at 99 % (macOS could not grow the swap under a 13 GB model), 5 to 18
minute holes between two model calls while `mediaanalysisd` ran at 200 % CPU
against a process at `nice 5`, an Ollama daemon alive after sleep but unable
to start `llama-server` (all generations 500 while `/api/ps` answered 200), a
stopwatch that stopped during sleep (374 s of compute reported for 2682 s of
wall time).

## Decision

- `preflight()` refuses to start on: disk < 20 GB; memory pressure critical
  per macOS itself (`kern.memorystatus_vm_pressure_level`), not a hand count
  of pages; a maintenance daemon above 80 % CPU; Ollama failing to GENERATE
  one token (a real probe on the small model with `keep_alive: 0`); two LLMs
  warm at once.
- A consumed swap blocks only in `chrono` mode (runs whose figure is the
  object: the CLI and the API); calibration tooling gets a warning. The guard
  measures what the rule names, the PAGEOUT RATE: `free = total - used` is
  the steady state on macOS, not a symptom. The "one run per reboot" rule was
  wrong and is withdrawn: unloading the model returns pages and shrinks
  swapfiles.
- Two clocks per run, `time.monotonic()` and `time.time()`; the gap is
  recorded as `veille_s` and beyond 30 s the run is marked NOT COMPARABLE.
  `caffeinate -is` does not prevent Maintenance Sleep on battery: machine
  plugged in for any measurement that counts.
- Runs are launched in the FOREGROUND (`nice 0`); zsh's `BG_NICE` puts
  background jobs at `nice 5`, where any daemon overtakes them.
- Method lesson, twice: a threshold that correlates is not a threshold that
  causes. Swap saturation was concomitant, not causal, in run 4 (reproduced
  with swap at zero).

## Consequences

- The preflight gate is tested against fabricated probe results; the macOS
  probes themselves sit behind one interface.
- Preflight becomes a graph node with spec fields at revamp step 4.
