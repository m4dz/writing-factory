# Tasks: prepared-entry1

## 0. Owner

- [x] Entry 1 prepared the day before, the owner picks among 6 (2026-11-19).

## 1. Code

- [x] `EntrySpec.prepared`, loader checks (first entry, ≥ 2 entries,
      `best_of.n ≥ 2`); chapter 7 entry 1 `prepared: true`.
- [x] `write`: in a prep, a prepared entry's drafts go to `entry_draws`
      unfinished; `_finish_entry` extracted from `write`.
- [x] `prep_pick` (interrupt, nothing before it calls a model), routes
      `route_after_leader`, `route_after_draw`, `route_after_write`,
      `route_after_repair`.
- [x] `frozen` from `seed_resumed`; `review` / `repair` keep frozen entries.
- [x] `factory prepare`: second question, re-asked on a non-rank, Enter / EOF
      = first ranked; `entry_pick` in the manifest.

## 2. Tests

- [x] Graph: drafts, pick of draft 4, reviewed and repaired, thread ends; a
      refused plan draws nothing; chapter 2 prep unchanged.
- [x] CLI end to end: pick re-asked on « x » and « 9 », rank 3 served; the
      stage run draws no entry-1 draft, reviews once, keeps entry 1.
- [x] Snapshot `ch7-prepared`: same calls as `ch7`, reordered; chapter
      byte-equal; warnings equal but the pick line.
- [x] Loader refusals. `make check` green.

## 3. Docs

- [x] ADR-0030; `docs/runbook.md` (D-1, the pick); `docs/architecture.md`.

## 4. Measure

- [x] One real `factory prepare --chapter 7` + `factory generate --from` on
      M: prep time, stage time against an unsplit run, entry 1 untouched.
      2026-11-20: prep 141 s, stage 292 s (unsplit 337–384 s), no entry-1
      write on stage, entry 1 verbatim
      (`experiments/runs/20261120-prepared-entry1/report.md`).
