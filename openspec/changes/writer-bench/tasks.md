# Tasks: writer-bench

- [x] Settings: `write_temperature`, `min_p`, `top_p`, `repeat_penalty`,
      `sampling_options()`, env table; client merges the options; graph's
      four writing calls read `settings.write_temperature`; run overrides
      and resolved configuration; runbook variable table.
- [x] `factory.tooling.bench`, `factory bench` in the CLI.
- [x] `tests/unit/test_sampling.py`, `tests/unit/test_bench.py`.
- [x] Docs: runbook (bench section, budget note), architecture, ADR-0026,
      plan.
- [x] Snapshots unchanged.
- [ ] Owner: pull the candidates, run the bench, read aloud, fill the judge
      column, `report.md` conclusion; then run 2 on the retained model.
