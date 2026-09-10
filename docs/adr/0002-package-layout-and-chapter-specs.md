# ADR-0002 — Single package, chapter knowledge as data

Date: 2026-09-10. Status: accepted.

## Context

The pipeline is three directories of scripts (`orchestrator/`, `outillage/`,
`indexer/`) linked by eleven `sys.path.insert` calls; production code imports
the calibration lint through one of them. There is no `pyproject`, no tests,
and 37 environment variables are the only configuration system.

Chapter knowledge is Python: `ch7.py` builds the chapter 7 state by hand,
`graph.py` and `gestes.py` hold dicts keyed `{2, 7}` (stations, fall line,
drift bank), `state.get("chapitre") or 2` appears seven times, and chapter 2
lives as string constants in a calibration driver. Adding a chapter means
editing four files. The API can generate exactly one chapter.

Preflight and TTS run around the graph, called by the API and the CLI, though
both are stages of what runs on stage.

## Decision

1. One installable package, `src/factory/`, with `pyproject.toml`. Modules:
   `api`, `pipeline` (graph, state, nodes, strategies), `chapter_spec`,
   `prompts` (templates only), `retrieval` (Chroma client and the indexer),
   `eval` (lint, grid, seal test, scorers), `infra` (raw adapters to Ollama,
   MLX, macOS probes, Telegram), `cli`. No `sys.path` manipulation anywhere.
2. Chapter knowledge is data: `chapters/NN-slug/spec.yaml` plus `brief.md`,
   at the repository root, author-owned, never indexed. The spec holds
   everything that names a chapter's content: calendar, entries, movement,
   material, vetos served in world language, anchor, fall, stations, drift
   bank, strategy per entry, beats, assembly and render parameters. A typed
   `ChapterSpec` validates it at load time and applies the anti-leak checks.
3. Code holds how, never what: strategies (`single`, `segments`, `beats`,
   `best_of`), composition primitives, validators parametrised by spec values,
   a scorer registry keyed by name. No chapter number appears in pipeline
   code.
4. Configuration (model names, context window, temperatures, retries,
   thresholds, paths) is one `Settings` object with environment overrides. It
   is not part of the chapter spec: the author decides content, the operator
   decides configuration.
5. Preflight and render (TTS) are graph nodes with spec fields and tests. The
   graph is: preflight → narrative_state → plan → write ⟲ accumulate → drift →
   review → repair → assemble → gestures → coherence → render → publish.
6. Prompt text lives in template files under `src/factory/prompts/`, never as
   string constants in node code. One `render()` fills them from the spec and
   the state.

## Consequences

- The move is done in two steps with a prompt snapshot suite as invariant:
  first the package (pure moves and renames, prompts unchanged), then the
  spec extraction (constants become spec fields, prompts unchanged).
- Chapters 1, 3–6 and 8–11 become author work: writing a spec file. The
  factory runs any chapter that has one.
- The seal test gains a control: no `chapters/` content in any collection.
- `outillage/` disappears as a directory; its scoring code is `factory.eval`,
  its drivers are replaced by the CLI, its data files (`lexique-fuite.txt`,
  `manifeste-auteur.txt`, `marqueurs-profonds.txt`) move next to the seal
  test.
