# repository-layout

## ADDED Requirements

### Requirement: Experiments are data under one root

Run artifacts SHALL live under `experiments/runs/<YYYYMMDD>-<slug>/`, each
directory with a `manifest.yaml`; failed runs under `experiments/journal/`;
grids and session reports under `experiments/grids/` and
`experiments/reports/`. No run artifact SHALL live at the repository root.

#### Scenario: A new run
- **WHEN** a driver writes a run
- **THEN** it lands under `experiments/runs/` and the archiver writes failures to `experiments/journal/`

### Requirement: Nothing duplicated, nothing thrown away

A file SHALL exist once in the repository; a removed copy SHALL be listed with
the path of its surviving twin.

#### Scenario: A byte-identical copy is found
- **WHEN** a run artifact exists twice in the tree
- **THEN** one copy is kept and the removed path is listed in `experiments/REMOVED.txt` with its surviving twin

### Requirement: Documentation has one home per role

Doctrines in `docs/doctrines.md`, decisions in `docs/adr/`, the map in
`docs/architecture.md`, operations in `docs/runbook.md`, current behaviour in
`openspec/specs/`, proposals in `openspec/changes/`; `CLAUDE.md` SHALL be
routing and conventions only.

#### Scenario: A newcomer
- **WHEN** someone opens `README.md`
- **THEN** every question in its table has one destination and every destination exists
