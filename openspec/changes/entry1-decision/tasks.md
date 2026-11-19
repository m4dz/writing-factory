# Tasks: entry1-decision

## 1. Evidence

- [x] 24 raw draws of entry 1 (M, served prompt of main), kept whole:
  `experiments/runs/20261119-entry1-decision/raw-a.json`, `raw-b.json`
  (`draw.py`).
- [x] Offline comparison of the selection rules on the same draws
  (`sim.py`): 0 / 3 / 5 groups of 8 serve the decision.

## 2. Code

- [x] `scorers.unquote_own_line`; applied in the best-of of an entry
  without anchor, the unquoted variant served, warned.
- [x] `BestOf.decision` (loader, model), scored by `names-erasure`.
- [x] Day's word in `scorers.notebook` (`day_word`), from the chapter
  verdict when `form.verdict: absent`; selection and review guard.
- [x] Both apostrophes in criterion terms.
- [x] Entry 1's variants in `variants.md`.
- [x] Tests on verbatim draws, both ways (`test_entry1_decision.py`); the
  quoting fixtures of `entry1-notebook-checks` keep their marks.
  `make check` green, snapshots unchanged.

## 3. Measure

- [x] Chapter 7 × 3 seeds with the variant spec; report (`report.md`):
  1 of 3 serves the decision; the selection took it whenever a draw held it.
- [ ] Owner reads entry 1 of the three `chapitre.md`.
- [ ] Owner decides the four spec questions of the proposal (decision list,
  « anniversaire » in names, album/cadre, `n`).
