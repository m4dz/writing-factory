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

## Layout today (step 5 done)

```
src/factory/
  paths.py           repository paths, resolved once (FACTORY_ROOT override)
  settings.py        one Settings object; every knob, env overrides, read at use
  cli.py             the `factory` command: doctor, index, query, generate,
                     calibrate, eval, serve, chat, promote (step 6)
  text.py            French guard, delint, sentence detection
  infra/             ollama.py (OllamaClient, one `client`, metrics), preflight.py (machine
                     gate), tts.py (cloned voice, lazy mlx import),
                     notify.py (Telegram, structured fields), progress.py
  retrieval/         context.py (Chroma access, style sections, system
                     prompt), indexer.py (bible → chunks → ChromaDB),
                     query.py (retrieval smoke test)
  pipeline/          graph.py (state, writing nodes, strategies, wiring),
                     nodes/preflight.py and nodes/render.py (the machine
                     nodes), scorers.py (best-of criteria by name),
                     gestures.py (validators, drift draw, placement),
                     assembly.py (audio switch, excerpt bound),
                     qa.py (Qwen roles: repair, facts, violation questions)
  chapter_spec/      model.py (ChapterSpec, EntrySpec, typed), loader.py
                     (spec.yaml → ChapterSpec, pointers into the briefs and
                     the movement table, anti-leak checks), narrative_state.py
  roleplay/          session.py (memory, out-of-role guard), cli.py
  api/               server.py (HTTP surface), static/acteur.html
  eval/              lint.py, grid.py, seal.py, journal.py, data/
  tooling/           stage_runner (calibration stages, `factory calibrate`;
                     chapter 2 constants until step 5), interviews (demo
                     sessions), resolution_xp (an experiment's recipe)
docker/              indexer.Dockerfile (installs the package)
bible/               canon, French, author-owned; surface/ and profond/ layers
chapters/NN-slug/    spec.yaml + briefs per chapter (author-owned, never indexed)
experiments/         runs (with manifests), journal, grids, reports
openspec/            project context, current specs, changes
docs/                architecture, runbook, doctrines, adr/, plans/
tests/               fakes, unit, stages, snapshots
```

Module names and identifiers are English (ADR-0001); comments and docstrings
are still French until the language pass of step 7. Data keys stay French
where they are data: run frontmatter, lint reports, the entry-spec dicts that
step 5 turns into YAML, the JSON the keynote deck reads.

## The graph

```
preflight ──▶ plan ──▶ write ──▶ accumulate ──▶ drift ───┐
               ▲                                         │ more entries?
               └─────────────────────────────────────────┘
                                                         ▼ no
        review ──▶ repair ──▶ assemble ──▶ place_gestures ──▶ coherence ──▶ render
```

- **preflight** (no model): the machine gate of ADR-0016, run when the state
  asks for it (`preflight: {strict, timer}`; the API and `factory generate`
  ask, calibration asks in warning mode, tests never do). A refusal raises
  out of the graph before any model call.

- **plan** (nemo, checked by Qwen): derives bible facts, plans dated entries
  under those facts, verifies the plan by violation questions, replans once.
  Short-circuited for a single-entry brief or when the brief imposes its own
  entries (chapter 7).
- **write** (nemo): one entry per pass, header and anchor prefixed by code.
  Three strategies selected per entry: a single call, three segments
  (opening, reconstruction with stations, closing), or code-capped beats with
  best-of-N selection by reading criteria. Continuation on a cut generation,
  trim to the last sentence as a net, sentence bound when the brief sets one.
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
  state asks (`render: true`) writes `output/chapitre.md`, unloads the QA
  model and renders `output/chapitre.wav`. A voice failure leaves the chapter
  on disk and `audio` at None, with an operator note.

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
- **State → artifacts.** The render node writes `output/chapitre.md` and
  `output/chapitre.wav` (`factory generate`, `POST /generate`); calibration
  runs (`factory calibrate`) write frontmatter Markdown under
  `experiments/runs/`.
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

`docs/plans/2026-09-revamp.md` §4: one package `src/factory/`, chapter
knowledge in `chapters/NN-slug/spec.yaml`, per-run API, narrative state per
chapter, English identifiers. Steps 4 to 7.
