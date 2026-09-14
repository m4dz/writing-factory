# Tasks: xp-abliterated-nemo

Wiring (this session, no model needed):

- [ ] `resolution_xp`: `--model`, `--out`, `--draws`; Ollama tag check; series
      manifest with both clocks; raw draws in the series directory.
- [ ] `resolution_xp`: positive-control condition served from the sheet's
      `## voix` section, explicit failure on an empty section.
- [ ] `graph.py`: `state["best_of"]` records in both best-of branches (no
      prompt change; snapshot untouched, named: all of `tests/snapshots/`).
- [ ] `runs.py`: `best_of` and `best_of_summary` in the manifest.
- [ ] Tests: recipe with the fake client; detectors on known texts (strict
      xfail for the 08-31 false positive); `record_result` with records;
      chapter-7 scenario asserts the record shape.
- [ ] Runbook: experiments section (HF GGUF pull, `AUTHOR_MODEL`, procedure).
- [ ] `experiments/runs/<date>-xp-abliterated-nemo/report.md` with the
      predictions section only; `manifest.yaml` with `kind: experiment`,
      `variable: author model tag`, `status: planned`.
- [ ] `make check` green.

Owner (stage machine):

- [ ] Pick the U tag: abliteration-only build of Mistral-Nemo-Instruct-2407,
      Q8_0 GGUF. Record tag and digest in the report.
- [ ] `ollama pull hf.co/<org>/<repo>:Q8_0`; `AUTHOR_MODEL=<tag> factory doctor`
      green; one smoke call in French.
- [ ] Leg 1, arm S then arm U, same sitting:
      `factory-xp-resolution --model <tag> --out experiments/runs/<date>-xp-abliterated-nemo/leg1-<arm>`.
- [ ] Leg 2, seeds fixed in the report, 3 runs per arm:
      `AUTHOR_MODEL=<tag> factory generate --chapter 7 --no-render --seed <s>`.
- [ ] Manual grid line on the six chapters, read aloud (doctrine 3).
- [ ] Report: results appended under the predictions; decision per the rule;
      journal entry if the hypothesis is closed; ADR if a decision follows.
