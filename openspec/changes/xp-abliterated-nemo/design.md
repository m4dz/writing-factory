# Design: xp-abliterated-nemo

## Recipe as driver

`factory.tooling.resolution_xp.main(argv)` gains `--model TAG` (default
`settings.author_model`, applied to `settings` for the process), `--out DIR`
(a series directory under `experiments/runs/`, created), `--draws N` (default
`settings.xp_draws`). Before the first call it queries Ollama's tag list and
refuses with a clear message when the tag is absent, so no series is ever
recorded against a model that was silently substituted. The series directory
receives `raw.md` (the table and verbatims of today) and `manifest.yaml`:
`kind: experiment-series`, `model` (tag and Ollama digest), `commit`,
`draws`, `temperature`, `num_predict`, `conditions`, `timings` on both clocks
(`Clocks` from the runs module), `verdicts` per condition. Nothing is written
to `experiments/journal/`; a failed series is moved there by hand with its
cause (doctrine 13).

The `CONDITIONS` table gains `("correctrice·porte·squelette", identity +
skeleton, door)`, where the skeleton is the `## voix` section of
`bible/fiche-judith.md` read from disk at run time (no copy in code, doctrine
6 and ADR-0025). The recipe fails explicitly if that section is missing or
empty, never on an empty control.

## Persisted best-of-N verdicts

Both best-of branches of the write node (beats, whole entry) append to
`state["best_of"]` one record per drawn variant:
`{entry, beat (or null), k, score, defects: [...], kept: bool}`. The record
carries no text: the text of the winner is in the chapter, rejected variants
are already discarded today and stay so. `record_result` copies the list into
the manifest under `best_of` and adds `best_of_summary`: counts of variants
drawn, kept, and defects grouped by label. No prompt is touched, so the
snapshot suite is unchanged; the chapter-7 scenario's fake model already
exercises the beats branch, so the record shape is asserted there.

## Tests

- `tests/unit/test_resolution_xp.py`: with the fake client, three draws per
  condition, verdicts and manifest fields; the recipe refuses an unknown tag;
  the recipe refuses an empty skeleton section.
- `tests/unit/test_graph_helpers.py`: `_BEAT_RESOLVES` fires on « Verdict :
  coquille. Ma mémoire m'a joué un tour. » and on « cela me revient
  maintenant »; `_BEAT_DOUBT` fires on « ma mémoire ne revient pas »; the
  08-31 false positive « Je me souviens parfaitement de ma soirée de la
  veille… pour l'instant, je n'ai pas de réponse » is `xfail(strict=True)`.
- `tests/unit/test_runs.py`: `record_result` writes `best_of` and its summary
  from a final state carrying records.
- `tests/snapshots/`: unchanged, asserted by `make check`.

## What the fakes and the snapshot must show

The fake model fixture for the chapter-7 scenario produces a manifest with
`best_of` records whose count equals entries × beats × `beats_n`, exactly one
`kept: true` per beat. Served prompts identical to the golden files.

## Runbook addition

Section "experiments": pulling a Hugging Face GGUF
(`ollama pull hf.co/<org>/<repo>:Q8_0`), checking the template and context
(`ollama show`), `AUTHOR_MODEL=<tag> factory doctor`, the two legs with their
commands, disk budget (two 13 GB models on disk, one warm, preflight's 20 GB
floor still applies), and where the series and the report land.

## Report

`experiments/runs/<date>-xp-abliterated-nemo/report.md` follows the C5
report: one-line verdict, protocol as executed, results table per leg and per
arm, verbatims, what stays open. Its "Predictions" section is committed
before the first draw and never edited afterwards; results are appended.
