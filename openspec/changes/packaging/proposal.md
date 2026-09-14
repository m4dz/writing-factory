# Proposal: packaging

## Why

The pipeline is three script directories linked by eleven `sys.path`
insertions; production code imports the calibration lint through one of
them; 37 environment variables are the configuration system; preflight and
rendering run around the graph instead of in it. Nothing is installable, and
every module binds the model client by name at import, so it cannot be
swapped in one place.

## What changes

Revamp step 4 (plan §8), delivered in three parts, each green on the prompt
snapshots:

1. **Skeleton and moves.** One installable package `src/factory/` with the
   layout of ADR-0002 (`infra`, `text`, `retrieval`, `pipeline`,
   `chapter_spec`, `roleplay`, `api`, `eval`, `tooling`). Every module moved
   with `git mv` under an English module name; intra-project imports become
   absolute; `sys.path` manipulation removed; repository paths resolved once
   in `factory.paths` (`FACTORY_ROOT` override for containers). Runtime
   dependencies move into `pyproject.toml`; the TTS stack is an extra; the
   indexer container installs the package. Tests import the package.
   Identifiers are NOT renamed yet: tests alias the new modules under the
   old names so the diff is moves and imports only.
2. **Settings and identifiers.** One `Settings` object replaces the
   environment reads scattered over the modules (environment still
   overrides); one injected model client replaces the per-module `chat`
   bindings; French identifiers become English (ADR-0001), tests updated
   with them.
3. **Nodes and CLI.** Preflight and render become graph nodes; the CLI
   (`factory generate | index | eval | serve | doctor`) replaces the drivers
   in `tooling/`; the runbook is rewritten for it.

## Doctrines relied on

- 5 (instruments lie): the snapshot suite is the only proof that a move
  changed nothing; a green suite is required after each part.
- 4: `paths.py` is falsified by running the suite from a directory other
  than the repository root.

## Variable moved

None. Served prompts and assembled chapters are byte-identical to the
golden files after each part.

## Non-goals

- Chapter knowledge extraction (step 5), the per-run API (step 6), the
  language pass on comments (step 7).
- Any behaviour change, including the fixes recorded in plan §9.
