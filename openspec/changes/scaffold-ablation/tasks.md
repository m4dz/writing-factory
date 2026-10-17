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

## 3. Run

- [ ] Experiment directory, seeds drawn and written, A4 variant spec.
- [ ] `factory doctor` green; 15 runs interleaved by seed.
- [ ] Blind set to the owner.

## 4. Conclude

- [ ] Owner verdicts in; `report.md` with the decision rule applied per piece.
- [ ] ADR proposal for the scaffolding kept or removed; owner decides any
      change to `chapters/07-anniversaire/spec.yaml`.
- [ ] Journal entries for the failed draws.
