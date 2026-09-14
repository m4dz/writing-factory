# Proposal: writer-bench

## Why

ADR-0008 chose `mistral-nemo` on speed under the 25-minute stage budget;
`mistral-small` 24B measured better prose and zero leak. ADR-0026 withdraws
the budget and the single-swap rule for book runs and reopens the writer.
Comparing writers needs one instrument that moves one variable, on the
calibrated reference, and records everything as data (ADR-0003), and it
needs the sampling parameters to be configuration rather than constants in
node code.

## What changes

- **Sampling knobs.** `Settings.write_temperature` (default 0.7, the former
  constant), `min_p`, `top_p`, `repeat_penalty` (default unset, sent to
  Ollama only when set); env `WRITE_TEMPERATURE`, `MIN_P`, `TOP_P`,
  `REPEAT_PENALTY`; all four are run overrides (`runs.OVERRIDABLE`) and are
  recorded in the resolved configuration. The four writing calls read
  `settings.write_temperature`.
- **`factory bench --models a,b --draws N [--chapter 7 --entry 2 --seed S]`**
  (`factory.tooling.bench`): runs the write node alone on an entry of a
  chapter whose plan is imposed, N draws per model with consecutive seeds,
  swapping models between series (unloading the previous one). One directory
  `experiments/runs/<stamp>-chNN-bench/` with `manifest.yaml` (`kind: bench`,
  models, seeds, commit, resolved configuration, per-model aggregates), one
  file per draw (frontmatter: model, seed, words, tok/s, wall, context need,
  cuts, style score, lint failures, both clocks; then the text and the
  warnings), `prompts.md`, and `report.md` with the comparison table and one
  empty line per draw for the manual grid question. The registry and the
  API ignore `kind: bench` directories.

## Doctrines relied on

- 13 (one variable): the bench moves `author_model` and nothing else; seeds
  and commit are recorded.
- 5 (instruments lie): both clocks per draw, tok/s from Ollama's counters,
  `ctx_need` and cuts reported per model.
- 3: the report's judge column is empty by design; the figures rank.

## Variable moved

None in served prompts: the snapshots are byte-identical (the default
request carries the same options as before). Run 2 of the protocol moves
`author_model` on the bench's retained candidate.

## Non-goals

- Choosing the model here: the bench runs on the owner's machine; the
  candidates must fit under 18 GB with the QA model unloaded.
- Benchmarking the QA model or review/repair (lever 6, its own change).
