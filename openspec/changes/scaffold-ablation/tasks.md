# Tasks: scaffold-ablation

## 1. Instrument first

- [x] Narrow `_BEAT_RESOLVES` to remembering the gesture; unit test over the
      12 C5 draws (none flagged) and the resolving journal variants (all
      still flagged). Snapshot `ch7` unchanged (the check only scores).
      Found a second false positive on the way: an open hypothesis
      (« si mon esprit me joue des tours ») read as a verdict.
- [x] Tests never load the real voice (autouse fixture): with the `tts`
      extra installed, two CLI tests ran the real synthesizer (256 s).

## 2. Make the arms reproducible

- [x] `factory generate --spec-file PATH`; variant copied into the run,
      diff in the manifest. Stage test with a `strategy: single` variant.
- [x] `factory generate --option KEY=VALUE` (`rag`, `micro_nodes`,
      `segments`); refused outside the whitelist; recorded under `options:`.
- [x] `factory generate --override KEY=VALUE`: the run overrides (machine
      knobs, ADR-0005) were reachable from the API only. Boolean overrides
      now refuse strings (`bool("false")` was `True`).
- [x] `factory generate --no-voice`: `chapitre.md` written, synthesis
      skipped (`--no-render` keeps its contract: no chapter file).
- [x] `variants.md` per run from the best-of log.
- [x] `factory eval ablation` with `--blind`.
- [x] Specs: `chapter-spec` delta (variant spec), `eval` delta (ablation
      table). `make check` green, snapshots identical.

- [x] `accumulation_enabled` override: the accumulation alone, for the A3
      re-run (`micro_nodes=false` also dropped drift, fall and pruning).

## 3. Run

- [x] Experiment directory, seeds drawn and written, A4 variant spec.
- [x] `factory doctor` green; 15 runs interleaved by seed.
- [x] Blind set to the owner (A3 out: invalid arm).
- [ ] A3 re-run with `accumulation_enabled=false`, same seeds.

## 3b. Instruments, after the runs (the arms share the old selection)

- [x] Presence by perception; open hypothesis is not a dismissal; restart
      exempt only in the chapter's first entry; « je décide de » counted
      (doctrine 8). Each falsified both ways on the runs' own sentences
      (`tests/unit/test_beat_checks.py`); `pipeline` delta spec.
- [x] `factory eval ablation` counts with the same checks (`decides` column).

## 4. Conclude

- [x] Owner verdicts in; `report.md` with the decision rule applied per piece.
- [x] ADR proposal for the scaffolding kept or removed; owner decides any
      change to `chapters/07-anniversaire/spec.yaml`. Accepted amended as
      ADR-0026 (2026-10-19); no spec change; `detector-fixes` merged.
- [x] Journal entries for the failed draws (`20261018T120000-scaffold-ablation`).
