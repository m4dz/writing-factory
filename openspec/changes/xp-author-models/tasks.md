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

- [ ] N, M × 395959, 528559, 781771, interleaved by seed.
- [ ] Grid table per arm (veto defects, words, litany, variants with defect,
      time, tok/s).
- [ ] Blind set: entry 2 of the six chapters, shuffled, key closed.

## 4. Conclude

- [ ] Owner verdicts; rule applied in `report.md`; journal entry.
- [ ] If adopted: actor-mode check, ADR superseding ADR-0008.
