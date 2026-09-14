# Design: language-pass

## Three bins

For each French comment: translate (what explains the code: a threshold, an
order of operations, a guard and its reason), compress (a session narrative
becomes the measured fact in one to three lines, run ids and numbers kept),
or point (a decision recorded in `docs/adr/` becomes `(ADR-00NN)`). Stale
references to the pre-step-4 layout are corrected or deleted. Nothing that a
maintainer needs to keep a guard alive is erased.

## What must not move

Only COMMENT tokens and docstrings change. String literals (prompts, French
messages, labels, regexes, word lists) are byte-identical; the prompt
snapshots (`tests/snapshots/*/prompts.md`, `chapter.md`, `warnings.txt`) and
the lint snapshots prove it after the pass.

## The audit

`tests/unit/test_language.py` tokenises every `.py` under `src/factory/` and
`tests/`, strips quoted spans (« … », “ … ”, `…`, "…", '…') from comments and
docstrings, and fails on a French stopword regex or on an accented letter
outside those spans. It is falsified in the test itself on a French sample
and an English sample with a quoted French term.

## Scaffolding closed

`conftest.py` loses its `sys.path` line (`pythonpath = ["tests"]` in
`pyproject.toml`); the suite has no xfail; every test file names a subject
that exists; docstrings no longer announce a step that "rewrites this later".

## Execution

Six parallel passes, one per file group (graph; lint; gestures, assembly,
QA, scorers, nodes; API and infra; eval, tooling, CLI, runs; retrieval,
roleplay, text, chapter spec, tests), each verified by the audit on its
files, ruff and the full suite; then one audit over everything.
