# Architecture

One map of what runs today, kept current at every step of the revamp
(`docs/plans/2026-09-revamp.md`). Decisions are in `docs/adr/`, working rules
in `docs/doctrines.md`, operations in `docs/runbook.md`.

## What it does

The factory writes chapters of *L'Involontaire*, a French novel in the form
of a proofreader's reading notebook: dated entries, one voice, no dialogue.
Inputs are an author-owned bible (`bible/`), a per-chapter brief
(`chapters/`), and a style contract. Outputs are a Markdown chapter with two
markers for the stage (audio switch, end of the read excerpt) and a WAV of the
excerpt in a cloned voice. A second surface, the actor mode, answers in
character with a stateful memory.

Everything runs on one Apple Silicon laptop: Ollama on the host (author model
`mistral-nemo` 12B, QA model `qwen2.5` 7B, embeddings `nomic-embed-text`),
ChromaDB in a Podman container, the `factory` package in a host venv.

## Layout today (step 6 done)

```
src/factory/
  paths.py           repository paths, resolved once (FACTORY_ROOT override)
  settings.py        one Settings object; every knob, env overrides, read at use
  cli.py             the `factory` command: doctor, index, query, generate,
                     runs, promote, calibrate, eval, serve, chat
  runs.py            the run registry: one directory per generation under
                     experiments/runs/, manifest, prompts, lint
  text.py            French guard, delint, sentence detection
  infra/             ollama.py (OllamaClient, one `client`, metrics), preflight.py (machine
                     gate), tts.py (cloned voice, lazy mlx import),
                     notify.py (Telegram, structured fields), progress.py
  retrieval/         context.py (Chroma access, style sections, system
                     prompt), indexer.py (bible → chunks → ChromaDB),
                     query.py (retrieval smoke test)
  pipeline/          graph.py (state, writing nodes, strategies, wiring),
                     nodes/preflight.py, nodes/narrative_state.py and
                     nodes/render.py (the machine nodes), scorers.py
                     (best-of criteria by name),
                     gestures.py (validators, drift draw, placement),
                     assembly.py (audio switch, excerpt bound),
                     qa.py (Qwen roles: repair, facts, violation questions)
  chapter_spec/      model.py (ChapterSpec, EntrySpec, typed), loader.py
                     (spec.yaml → ChapterSpec, pointers into the briefs and
                     the movement table, anti-leak checks), narrative_state.py
  roleplay/          session.py (memory, out-of-role guard), cli.py
  api/               server.py (one-worker queue, per-run routes, actor mode),
                     static/acteur.html
  eval/              lint.py, grid.py, seal.py, journal.py, style.py (countable
                     register marks, best-of tie-break), data/
  tooling/           stage_runner (calibration stages, `factory calibrate`;
                     chapter 2 constants until step 5), bench (the write node
                     alone per model, `factory bench`), interviews (demo
                     sessions), resolution_xp (an experiment's recipe)
docker/              indexer.Dockerfile (installs the package)
bible/               canon, French, author-owned; surface/ and profond/ layers;
                     generated/ (narrative state per chapter, derived, not
                     versioned) and scenes/ (promoted chapters)
chapters/NN-slug/    spec.yaml + briefs per chapter (author-owned, never indexed)
experiments/         runs (with manifests), journal, grids, reports
openspec/            project context, current specs, changes
docs/                architecture, runbook, doctrines, adr/, plans/
tests/               fakes, unit, stages, snapshots
```

Module names, identifiers, comments and docstrings are English (ADR-0001);
the language audit (`tests/unit/test_language.py`) keeps them so. French
stays where it is the author's material or the machine's French face:
prompts, messages, warnings, labels, run frontmatter, lint reports, the JSON
the deck reads.

## The graph

```
preflight ──▶ narrative_state ──▶ plan ──▶ write ──▶ accumulate ──▶ drift ───┐
                                   ▲                                         │ more entries?
                                   └─────────────────────────────────────────┘
                                                                             ▼ no
                    review ──▶ repair ──▶ assemble ──▶ place_gestures ──▶ coherence ──▶ render
```

- **preflight** (no model): the machine gate of ADR-0016, run when the state
  asks for it (`preflight: {strict, timer}`; the API and `factory generate`
  ask, calibration asks in warning mode, tests never do). A refusal raises
  out of the graph before any model call.

- **narrative_state** (no model): when the state asks (`narrative_state:
  true`), derives what chapter N-1 left from the author's pilot table (the
  perceived side only), writes `bible/generated/narrative-state/ch-NN.md`
  and indexes it as `judith::etat_narratif_courant::chNN`; idempotent. The
  writing prompt then serves that chunk instead of the sheet's section 7.
- **plan** (nemo, checked by Qwen): derives bible facts, plans dated entries
  under those facts, verifies the plan by violation questions, replans once.
  Short-circuited for a single-entry brief or when the brief imposes its own
  entries (chapter 7).
- **write** (nemo): one entry per pass, header and anchor prefixed by code.
  Three strategies selected per entry: a single call, three segments
  (opening, reconstruction with stations, closing), or code-capped beats with
  best-of-N selection by reading criteria, the countable style marks breaking
  ties. A beat may carry the author's attack: posed as the head of the beat,
  counted against its sentence cap, the model continues it. Continuation on a
  cut generation, trim to the last sentence as a net, sentence bound when the
  brief sets one. Sampling (temperature, min_p, top_p, repeat penalty) is
  configuration (ADR-0026).
- **accumulate** (nemo): one long enumerative sentence, validated by code
  (thresholds, language, person, abstraction, decor), set aside.
- **drift** (no model): the drift passage, from the chapter bank or the
  brief, validated and set aside.
- **review** (nemo) and **repair** (Qwen, after nemo is unloaded): rewrite
  each entry; a guard rejects a rewrite that moves away from the entry's word
  target.
- **assemble**: deterministic pruning of named residue motifs on beat entries.
- **place_gestures**: re-stamps header and anchor, poses the fall line, inserts
  accumulation and drift on the FINAL text, deduplicates repeated paragraphs
  while protecting composed ones.
- **coherence** (Qwen): facts → violation questions → answers per scene, with
  code-verified citations and a severe counter-call.
- **render** (no model, then the voice): assembles the chapter Markdown with
  both stage markers into `chapter_md` (kwargs from the state field
  `assembly`: switch on the second header, imposed fall), always; when the
  state asks (`render: true`) writes `chapitre.md` into the run directory
  (`artifacts_dir`; `output/` without a run), unloads the QA model and renders
  `chapitre.wav` next to it. A voice failure leaves the chapter on disk and
  `audio` at None, with an operator note.

## Data flows

- **Bible → index.** `factory.retrieval.indexer` chunks each Markdown file by `## `
  section under three firewall barriers (ADR-0017), embeds, upserts to the
  `auteur` collection; orphan chunks are purged. Never touches the `sessions`
  collection.
- **Index → prompt.** Writing chunks (voice, current state, psychology) by
  deterministic id; world chunks for fact derivation; style sections from
  disk with example lines stripped; no previous entries during writing.
- **Chapter spec → state.** `load_chapter(N)` reads `chapters/NN-slug/spec.yaml`
  (calendar, verdict, objects, stations, accumulation fall, drift bank,
  assembly, per-entry structure and caps, best-of criterion name) and follows
  its pointers: the served brief is a section of the owner's `brief.md`, an
  entry's trajectory, material, beat instructions and drift passage come from
  its entry brief, the movement is one row of the deep table. `spec.state()`
  builds the `graph.invoke` state; run options (RAG, micro-nodes, segments,
  single-entry brief) are keyword overrides. No chapter number appears in
  pipeline code: the graph reads `state["stations"]`, `state["accumulation_fall"]`,
  `state["drift_bank"]` and the typed `entry_specs`.
- **Runs.** `factory generate` and `POST /generate` create a run directory
  (`factory.runs`: `experiments/runs/<stamp>-chNN-<slug>/`, whitelisted id)
  with its manifest (chapter, seed, commit, resolved configuration, status,
  both clocks, metrics, warnings, collections queried), then invoke the graph
  with `preflight`, `narrative_state`, `render` and `artifacts_dir` set. The
  render node writes `chapitre.md` and `chapitre.wav` there; the run closes
  with `prompts.md` (every prompt served, recorded by the model client) and
  `lint.md`. The API serves artifacts from disk and holds no chapter in
  memory; calibration runs (`factory calibrate`) write their frontmatter
  Markdown under `experiments/runs/` as before.
- **Promotion.** `factory promote <run>` copies a run's chapter into
  `bible/scenes/ch-NN-<run>.md` (`type: scene`, `chapter`, `promoted_from`)
  and indexes it; only promoted scenes enter semantic retrieval.
- **Roleplay.** `sessions/<character>/<timestamp>.md` (summary + transcript)
  is written first, then its summary is indexed in the `sessions` collection
  and retrieved at the next session start.

## Configuration

`factory.settings.Settings` is the one configuration object: model names,
Ollama and Chroma endpoints, API host and port, audio and TTS calibration,
roleplay memory, Telegram, preflight thresholds, experiment knobs. Defaults
live in the dataclass; the environment overrides them once at import
(`settings = Settings.from_env()`); modules read `settings.<field>` at call
time, so a test or a CLI changes a value and sees it applied. Chapter
knowledge is not configuration (`chapters/`, ADR-0002); repository paths are
not either (`factory.paths`). The variable table is in the runbook, §1.6.

## Boundaries that are tested

- Model boundary: `factory.infra.ollama.client`, one `OllamaClient` whose
  `chat` / `chat_turns` / `unload` the module-level functions delegate to;
  the fake replaces its three methods in one place. Served prompts frozen in
  `tests/snapshots/`.
- Store boundary: Chroma client, faked from the indexer's chunker.
- Machine boundary: preflight probes, TTS synthesizer, Telegram, faked; the
  two machine nodes are tested with those fakes, and `factory doctor` runs
  the real probes on the owner's machine.

## Target

`docs/plans/2026-09-revamp.md` §4: reached. The seven steps of the revamp
are done; experiments resume on this layout, each as an openspec change plus
a run directory with its manifest and report (ADR-0003).
