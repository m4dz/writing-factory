# Proposal: safety-net

## Why

The pipeline is about to be moved into a package (step 4) and its chapter
knowledge extracted into data (step 5). Its correctness was proven by runs,
never by tests: there is no test in the repository. Moving 2,000 lines whose
wording was calibrated over seven sessions, without an instrument that says
whether the model sees the same prompts afterwards, would be a refactor judged
by hope. Doctrine 4 applies to us: the instrument comes first, and it must be
shown to fail on a known defect before it is trusted.

## What changes

- A test suite on the CURRENT layout (no code moves, no behaviour change),
  runnable with `make check` (ruff + pytest), needing no model, no Chroma, no
  macOS.
- A fake model (`tests/fakes/llm.py`) that recognises each node from the
  prompt it receives and answers with crafted French text conforming to the
  pipeline's own validators, so the graph walks its nominal path
  deterministically. Failing variants exercise retries and rejections.
- A fake vector store (`tests/fakes/chroma.py`) built from the indexer's own
  chunker over `bible/`, firewall rules included.
- Prompt snapshots (`tests/snapshots/`): for chapter 7 as the API generates
  it, and for chapter 2 stage S7 (scored single entry, and full chapter), every
  served prompt and the assembled chapter are frozen as golden files. This is
  the invariant steps 4 and 5 must preserve byte for byte.
- Lint snapshots: the deterministic lint's report on the 34 journal and
  rehearsal files, frozen. The falsification baseline in both directions.
- Unit tests on every pure function (style, chapter assembly, graph helpers,
  gestures, QA parsers, notifier, roleplay, chapter 7 spec parsers, indexer
  chunking) and stage tests with fakes (preflight gate, render, API, retrieval).
- `pyproject.toml` (test dependencies only), ruff configuration, `Makefile`.

## Doctrines relied on

- 4 (falsify in both directions): fixtures have a failing twin; the lint
  snapshot covers accepted and refused runs alike.
- 5 (instruments lie): the snapshot compares what was SERVED, recorded at the
  model boundary, not what the code says it served.
- 6 (shown is recited): the snapshot is what protects the wording.

## Variable moved

None. This change is measured by the absence of behaviour change: the golden
files are generated from the code as it ran on stage (`v0-keynote`).

## Non-goals

- Fixing what the tests reveal. Three findings are recorded (plan §9) and
  routed to later steps; one is a strict expected failure that will flip.
- Testing the real macOS probes or the real MLX synthesis (`factory doctor`,
  runbook).
- Moving, renaming or translating any code.
