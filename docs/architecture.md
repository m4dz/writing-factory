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

## Layout today (step 4, part 2)

```
src/factory/
  paths.py           repository paths, resolved once (FACTORY_ROOT override)
  settings.py        one Settings object; every knob, env overrides, read at use
  text.py            French guard, delint, sentence detection
  infra/             ollama.py (OllamaClient, one `client`, metrics), preflight.py (machine
                     gate), tts.py (cloned voice, lazy mlx import),
                     notify.py (Telegram, structured fields), progress.py
  retrieval/         context.py (Chroma access, style sections, system
                     prompt), indexer.py (bible → chunks → ChromaDB),
                     query.py (retrieval smoke test)
  pipeline/          graph.py (state, nodes, strategies, wiring),
                     gestures.py (validators, drift bank, placement),
                     assembly.py (audio switch, excerpt bound),
                     qa.py (Qwen roles: repair, facts, violation questions)
  chapter_spec/      chapter7.py (chapter 7 as Python, reads chapters/07-*/),
                     narrative_state.py (state chunk from the pilot table)
  roleplay/          session.py (memory, out-of-role guard), cli.py
  api/               server.py (HTTP surface), static/acteur.html
  eval/              lint.py, grid.py, seal.py, journal.py, data/
  tooling/           drivers: stage_runner (calibration stages), ch2_runner,
                     scene_runner, interviews, resolution_xp, modelfile,
                     run_chapter — replaced by the CLI in part 3
docker/              indexer.Dockerfile (installs the package)
bible/               canon, French, author-owned; surface/ and profond/ layers
chapters/07-*/       chapter 7 briefs (author-owned, never indexed)
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
plan ──▶ write ──▶ accumulate ──▶ drift ───┐
  ▲                                        │ more entries?
  └────────────────────────────────────────┘
                                           ▼ no
                   review ──▶ repair ──▶ assemble ──▶ place_gestures ──▶ coherence
```

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

Around the graph, called by the API and the CLI: **preflight** before,
**assembly** of the chapter Markdown (`assembly.assemble`) and **render**
(TTS) after. Both become graph nodes at step 4.

## Data flows

- **Bible → index.** `factory.retrieval.indexer` chunks each Markdown file by `## `
  section under three firewall barriers (ADR-0017), embeds, upserts to the
  `auteur` collection; orphan chunks are purged. Never touches the `sessions`
  collection.
- **Index → prompt.** Writing chunks (voice, current state, psychology) by
  deterministic id; world chunks for fact derivation; style sections from
  disk with example lines stripped; no previous entries during writing.
- **Chapter 7 spec → state.** `factory.chapter_spec.chapter7` reads `chapters/07-anniversaire/
  brief.md` and `brief-entree-2.md` by section, the movement line of the
  chapter from the deep table, and builds the `graph.invoke` state
  (`entry_specs`, beats, anchor, fall). Chapter 2 is built the same way in
  `factory.tooling.stage_runner`. Both become a YAML spec and a loader at step 5.
- **State → artifacts.** The API writes `output/chapitre.md` and
  `output/chapitre.wav`; calibration runs write frontmatter Markdown under
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
- Machine boundary: preflight probes, TTS synthesizer, Telegram, faked.

## Target

`docs/plans/2026-09-revamp.md` §4: one package `src/factory/`, chapter
knowledge in `chapters/NN-slug/spec.yaml`, per-run API, narrative state per
chapter, English identifiers. Steps 4 to 7.
