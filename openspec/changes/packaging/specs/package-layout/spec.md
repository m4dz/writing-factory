# package-layout

## ADDED Requirements

### Requirement: One installable package

The code SHALL live in one installable package `factory` under `src/`,
importable with absolute imports and without any `sys.path` manipulation;
`pip install -e ".[test]"` SHALL install it with its runtime dependencies.

#### Scenario: Fresh environment
- **WHEN** a fresh venv runs `make venv && make check`
- **THEN** the package installs, every module imports, and the suite is green

### Requirement: Repository paths are resolved once

Author material (`bible/`, `chapters/`), experiments and outputs SHALL be
located through `factory.paths`, derived from the package location or
`FACTORY_ROOT`; no module SHALL depend on the working directory.

#### Scenario: Suite from another directory
- **WHEN** pytest runs from a directory that is not the repository root
- **THEN** the suite is green and the lint finds its data files

### Requirement: Data files travel with the package

Lint data (leak lexicon, source manifest, deep markers, grid template) and
the actor page SHALL be package data addressed from the package, never from
a repository directory.

#### Scenario: Installed container
- **WHEN** the indexer image runs `python -m factory.retrieval.indexer`
- **THEN** it indexes the mounted bible without any repository checkout
