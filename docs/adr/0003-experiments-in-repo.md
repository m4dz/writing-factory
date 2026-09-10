# ADR-0003 — Experiments are data kept in the repository

Date: 2026-09-10. Status: accepted.

## Context

Seven sessions produced 16 run directories under three naming schemes
(`runs-v2`, `runs-s4-a`, `runs-ch7`…), four incompatible frontmatter schemas,
duplicated reports and grids, and 21 launch logs in one directory. No run
records the commit it ran on. The journal of failed runs (`journal-des-murs/`,
32 entries) is the material of the talk and the evidence behind the
doctrines. None of it is referenced by any document.

The owner considered versioning experiments in a dedicated package. Runs are
Markdown, JSON and WAV: data, about one megabyte without audio. What must be
versioned with the code is the scoring tooling, because production imports
it, and what must be versioned with each run is the commit and configuration
it used.

## Decision

1. Experiments stay in this repository, under `experiments/`, as data:
   `runs/<YYYYMMDD>-<slug>/` (one run or one series), `journal/` (the failed
   runs, unchanged, with the digest as its `README.md`), `grids/`, `reports/`.
2. Every run directory carries `manifest.yaml`: run id, chapter, seed, commit,
   resolved configuration, model tags, timings on both clocks, sleep detected,
   collections queried. Manifests for past runs are reconstructed from their
   frontmatter where the information exists, and marked `reconstructed: true`.
3. One run, one directory. Byte-identical copies are removed; launch logs and
   `nohup` duplicates are dropped; WAV files stay ignored except the archived
   fallback of the runbook.
4. The scoring tooling (lint, grid, seal test, scorers) is code, in
   `factory.eval`. The journal archiver and the grid generator become CLI
   commands that write into `experiments/`.
5. An experiment starts as an openspec change (the variable it moves, the
   expected effect) and ends with a `report.md` in its run directory. The
   digest of the journal is updated when a run enters it.

## Consequences

- `git clone` gives the full evidence base; nothing lives in a second
  repository.
- Past naming is not repaired retroactively beyond the move: `runs-s6-c`
  becomes `experiments/runs/20260821-s6-stage-c/` with a manifest that says
  what it was.
- The repository grows with each run. Audio and logs are excluded; if text
  volume becomes a problem, the decision is revisited, not pre-empted.
