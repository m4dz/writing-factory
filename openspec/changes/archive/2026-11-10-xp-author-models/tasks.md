# Tasks: xp-author-models

## 1. Setup

- [x] Worktree `factory-xp-models`, branch `xp-author-models` from `main`
      (`487fcf0`); `make check` green (335 tests).
- [x] Pull M and G; M packaged as `xp-ministral3-14b-q5` (template fix).
- [x] G dropped by the owner before any draw (thinking, no continuation, CPU spill).
- [x] Owner validates the predictions and the decision rule (`report.md`).

## 2. Smoke

- [x] M, seed 111111: passed the stop rules on the 2nd attempt (1st: ChromaDB down).
- [x] ~~G, seed 111111~~: dropped.

## 3. Run

- [x] N, M × 395959, 528559, 781771, interleaved by seed (M/781771 errored:
      the term guard on re-served model text, fixed by `beat-guard-model-text`).
- [x] Grid table per arm (veto defects, words, litany, variants with defect,
      time, tok/s).
- [x] Blind set: entry 2 of the five ready runs, shuffled, key closed.

## 4. Conclude

- [x] Rule applied in `report.md`: M rejected (errored run, third person).
- [x] ~~Owner verdicts; journal entry~~: the owner set the blind set aside;
      superseded by `xp-author-models-2` (guard fixed, Mistral Small added).
- [x] ~~If adopted: actor-mode check, ADR superseding ADR-0008~~: not adopted.
