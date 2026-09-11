# Tasks: chapter-spec

- [x] `factory.chapter_spec.model` (ChapterSpec, EntrySpec, BeatSpec, BestOf,
      Drift, DriftBank, Calendar, Defaults) and `loader` (discovery, YAML,
      pointers, assertions).
- [x] `chapters/07-anniversaire/spec.yaml` (structure, caps, criterion lists,
      pointers to brief.md §3 and brief-entree-2.md) and
      `chapters/02-premiere-divergence/spec.yaml` (the calibration constants,
      briefs v4 as literals). Proposed to the owner; the brief files are untouched.
- [x] Graph reads `stations`, `accumulation_fall`, `drift_bank`, `assembly`
      and typed entry specs from the state; `STATIONS`, `_IMPOSED_FALL`,
      `DRIFT_BANK`, `chapter7.py` removed; `factory.pipeline.scorers` registry.
- [x] API, CLI, stage runner and snapshot scenarios build states through
      `load_chapter`; stage runner keeps only the historical briefs v2/v3/C.
- [x] Seal control 6: no `chapters/` line in `auteur` or `sessions`.
- [x] Accumulation validator: language before the last-attempt tolerance;
      the strict xfail of step 2 flipped.
- [x] Specs: `chapter-spec` rewritten to the new behaviour, `pipeline`
      scenarios renamed to the English keys.
- [x] `make check` green; snapshots identical.
