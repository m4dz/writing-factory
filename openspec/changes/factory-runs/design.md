# Design: factory-runs

## Runs

`Run(id, dir, chapter, slug, seed, overrides, created, status, manifest)`.
`create_run` writes the queued manifest with `commit` (git) and the resolved
configuration; `record_result` closes it (status, timings from `Clocks`
— monotonic and wall, sleep as their gap —, metrics, warnings, coherence,
plan report, audio, collections) and writes `prompts.md` from the client's
recording and `lint.md` from `eval.lint`. Ids match
`^\d{8}-\d{6}-ch\d{2}-[a-z0-9-]{1,40}$` and are validated before any file
access; listing sorts on `created` (microseconds) then id, newest first;
directories of step-3 series (other names, `kind ≠ run`) are ignored.

## Worker

`Worker` holds a condition-guarded queue and one daemon thread started at the
first submit. `_execute` installs a progress sink with the Telegram observer,
applies the run's overrides to `settings` for its duration (one worker, so no
overlap), records prompts through `client.recording`, invokes the graph with
`preflight {strict, timer}`, `narrative_state`, `render` and `artifacts_dir`,
then records the result whatever happened (`ready`, `cancelled`, `error`).
`snapshot(run)` reads the sink for the running run, the queue position for a
queued one, the manifest otherwise. Cancel removes a queued run or flags the
sink of the running one.

## Narrative state

`chapter_spec.narrative_state`: `state_text(N)` narrates row N-1 with the
anchor of the `[VALEURS]` block, `write_state_file(N)` renders a frontmatter
(`doc_id: judith`, `type: character`, `chapter: N`, `layer: SURFACE`) and a
`## 7. État narratif courant` section, idempotently. The node indexes the file
with the indexer's own `index_file` (so a reindex converges on the same
chunk) and `retrieval.embed`. `character_context(doc_id, chapter)` asks for
the scoped id and substitutes it for the sheet's state chunk when found.

## Promotion

`factory promote <run>`: requires `status: ready` and `chapitre.md`; writes
`bible/scenes/ch-NN-<run>.md` with `doc_id: scene-chNN`, `type: scene`,
`chapter`, `promoted_from`; indexes it (`scene-chNN::preambule::chNN`);
records `promoted_to` in the manifest. The owner's act, never the pipeline's.

## What the fakes show

`test_api`: payload `400`s, `202 {run_id}`, artifacts on disk, `204` audio on
a voice failure, `410` legacy routes, a queued second run held by a gated
preflight, cancel of a queued run, `latest`, `404`/`400` on ids, SSE
terminal event. `test_runs`: manifests, whitelists, ordering, result
recording. `test_narrative_state`: file, chunk, idempotence, retrieval
preference and fallback. `test_cli`: `--chapters 2,7` back to back with both
states generated, `promote` into a temporary bible with the scene indexed.
The fake model mirrors the client's recording so `prompts.md` is exercised;
`fake_chroma` now hands each test its own copy of the index.
