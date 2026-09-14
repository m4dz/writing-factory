# Proposal: hygiene

## Why

Sixteen run directories under three naming schemes, sixteen loose Markdown
files at the root, a 657-line `CLAUDE.md` that is a third history and a
quarter decision records, four of seven documents referenced by nothing, a
README and a compose file describing a frontend rejected a month ago. Nothing
told a newcomer, or the assistant, where anything was or why.

## What changes

- `experiments/`: every run directory moved to `experiments/runs/<date>-<slug>/`
  with a reconstructed `manifest.yaml`; the journal to `experiments/journal/`
  with the digest as its README; grids and session reports under
  `experiments/{grids,reports}/`. Byte-identical copies, launch logs and
  discarded draws already in the journal removed (`experiments/REMOVED.txt`).
- Chapter 7 briefs moved to `chapters/07-anniversaire/`; `ch7.py` reads them
  there. Prompt snapshots unchanged.
- Documentation extracted then deleted: `docs/doctrines.md`,
  `docs/architecture.md`, `docs/runbook.md`, ADRs 0006–0020 with their
  original dates, `CLAUDE.md` reduced to routing and conventions, README
  rewritten. Deleted after extraction: the old RUNBOOK, the handover, the
  deck contract, the SSE front spec, the 2026-08-10 pipeline doc, the movement
  implementation note, the two tooling READMEs.
- `openspec/specs/` written for the current behaviour of seven capabilities.
- OpenWebUI removed from `podman-compose.yml`; `query_test.py` default
  collection aligned with the indexer's.

## Doctrines relied on

- 13: failed runs are material; nothing is thrown away, nothing duplicated.
- 5: the manifests say they are reconstructed and what they do not know.

## Variable moved

None in generation. `make check` and the prompt snapshots are unchanged.

## Non-goals

- Renaming or translating code (step 4 and 7).
- Editing the content of any run, grid, journal entry or bible file.
- Writing chapter specs (step 5).
