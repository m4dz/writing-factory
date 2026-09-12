# Proposal: factory-runs

## Why

The API generated one hardcoded chapter into singleton routes, the server
held the job in memory, and the narrative state of a chapter was a section of
the narrator sheet rewritten by a script between chapters. A factory
generates many chapters, several runs of one chapter, and must go from
chapter N to N+1 with no manual step.

## What changes

Revamp step 6 (plan §6, §8; ADR-0003, ADR-0005):

- **Runs.** `factory.runs`: one directory per generation under
  `experiments/runs/<stamp>-chNN-<slug>/` with `manifest.yaml` (chapter,
  seed, commit, resolved configuration, overrides, status, both clocks,
  metrics, warnings, collections queried), `chapitre.md`, `chapitre.wav`,
  `prompts.md` (every prompt served, recorded by the model client),
  `lint.md`. The registry is the directory; the API reads it.
- **API per run.** `POST /generate {chapter, seed?, overrides?}` → `202
  {run_id}`, `400` without payload; one worker and a queue; `/runs`,
  `/runs/<id>/status|events|chapter|audio|prompts|manifest`,
  `POST /runs/<id>/cancel`, `/runs/latest/…`; the keynote's singleton routes
  answer `410`. `/chat` keeps its `409` during generation.
- **Narrative state per chapter.** A `narrative_state` node after preflight
  writes `bible/generated/narrative-state/ch-NN.md` from the author's table
  and indexes it as `judith::etat_narratif_courant::chNN`; retrieval serves
  the chapter's chunk and falls back to the sheet. The indexer knows the
  `chapter` metadata and id suffix. The script that rewrote the sheet is
  gone.
- **`factory generate --chapters 2,7`**, `factory runs`, and **`factory
  promote <run>`**: a read chapter is copied into `bible/scenes/` (`type:
  scene`) and indexed; only promoted scenes enter semantic retrieval.
- Seal manifest entries may be globs (generated states, promoted scenes);
  control 6 exempts promoted scenes, which carry their anchor by construction.

## Doctrines relied on

- 5: the three prompt snapshots are unchanged — the scenarios set neither
  `narrative_state` nor `render`, and the fake index has no chapter chunk,
  so the state served is the sheet's.
- 4 (one variable): the one prompt change of this step is the narrative
  state chunk served for chapter N; a dedicated test shows the chapter chunk
  replacing the sheet's section and the fallback when absent.

## Variable moved

In served prompts: the `etat_narratif_courant` chunk becomes the state of
chapter N (from row N-1) when the node has run; otherwise nothing.

## Non-goals

- Serving promoted scenes during writing (measured: the model copies them).
- The deck client: rewritten by the owner against `/runs/<id>/…`.
- Reports per run (`report.md`): written by hand when a run is an experiment.
