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
- **WHEN** the indexer image runs `factory index`
- **THEN** it indexes the mounted bible without any repository checkout

### Requirement: One settings object

Every operator knob SHALL be a field of `factory.settings.Settings` with its
default, overridden once from the environment; modules SHALL read
`settings.<field>` at call time and never `os.environ`.

#### Scenario: A test changes a knob
- **WHEN** a test sets `settings.output_dir` to a temporary directory
- **THEN** the render node writes there without any module reload

### Requirement: One model client

Model calls SHALL go through `factory.infra.ollama.client`, an `OllamaClient`
whose `chat`, `chat_turns` and `unload` the module functions delegate to.

#### Scenario: The fake model
- **WHEN** the test suite replaces the client's three methods
- **THEN** every node, the QA and the actor mode use the fake

### Requirement: One command line

`factory` SHALL expose `doctor`, `index`, `query`, `generate`, `calibrate`,
`eval {lint|grid|seal|journal}`, `serve`, `chat` and a `promote` placeholder,
each delegating to a module `main(argv)`; pipeline imports SHALL be lazy so
`factory index` runs where LangGraph is not installed.

#### Scenario: Chapter without spec
- **WHEN** `factory generate --chapter 2` is called before step 5
- **THEN** the command says no specification exists and exits without calling a model

### Requirement: Dependency groups

Core dependencies SHALL be those of indexing, querying and evaluation; the
graph SHALL be the `pipeline` extra and the voice the `tts` extra; the
indexer image SHALL install core only.

#### Scenario: Container image
- **WHEN** the indexer image is built
- **THEN** LangGraph is not installed and `factory index` runs
