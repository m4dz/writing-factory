# writing-factory

A local-only pipeline that writes the chapters of *L'Involontaire*, a French
novel in the form of a proofreader's reading notebook, from an author-owned
bible and per-chapter briefs, on one Apple Silicon laptop. It renders an
excerpt in a cloned voice and serves an "actor mode" (in-character chat). It
was the live demonstration of the keynote *L'IA devant soi*; a second run is
scheduled and the codebase is being restructured for it.

**Golden rule:** everything runs locally. Ollama on the host, ChromaDB in a
container, no cloud API, no external logging. The one accepted exception is
the operator's Telegram pager, which can never carry text of the work
(ADR-0015).

## Where things are

| You want | Go to |
|---|---|
| How it is built, one map | `docs/architecture.md` |
| Run it, prepare the stage, fix the machine | `docs/runbook.md` |
| Why it is built this way | `docs/adr/` |
| The working rules every change is checked against | `docs/doctrines.md` |
| What the system must do (current behaviour) | `openspec/specs/` |
| The revamp in progress, step by step | `docs/plans/2026-09-revamp.md` |
| The evidence: runs, failed draws, grids, reports | `experiments/` |
| The novel's canon (French, author-owned) | `bible/` |
| Chapter briefs (French, author-owned) | `chapters/` |

## Quick start (development)

```bash
make venv     # python3 -m venv .venv && pip install -e ".[pipeline,test]"
make check    # ruff + pytest; needs no model, no Chroma, no macOS
```

Running the pipeline for real needs Ollama, ChromaDB and the models; see the
runbook. The entry point is one command:

```bash
.venv/bin/factory doctor       # machine, backends, models, voice
.venv/bin/factory index        # bible → ChromaDB
.venv/bin/factory generate     # chapter 7, artifacts in output/
.venv/bin/factory serve        # the API the deck talks to
```

## Layout

```
src/factory/    the package: cli (the `factory` command), pipeline, API,
                actor mode, retrieval and indexer, eval (lint, grid, seal),
                infra, settings
docker/         the indexer image (installs the package)
bible/          canon; surface/ is indexed, profond/ never is
chapters/       per-chapter briefs, never indexed
experiments/    runs with manifests, journal of failed draws, grids, reports
openspec/       project context, specs, change proposals
docs/           architecture, runbook, doctrines, ADRs, plans
tests/          fakes, unit, stage and snapshot tests
```

Code, comments and engineering documents are in English; prompts, bible,
briefs and the journal are in French (ADR-0001).
