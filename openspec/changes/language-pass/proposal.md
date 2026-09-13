# Proposal: language-pass

## Why

ADR-0001 put code, comments and docstrings in English and the author's
material in French. Steps 4 to 6 renamed every identifier and module; the
comments and docstrings — dense, French, carrying the rationale of every
threshold — stayed where they were until they had a home. The ADRs and the
journal now exist; the comments can be translated, compressed or replaced by a
pointer without loss.

## What changes

Revamp step 7 (plan §8), the last step:

- Every French comment and docstring under `src/factory/` and `tests/` is
  rewritten in English: translated when it explains the code at hand,
  compressed to the measured fact when it narrates a session, replaced by a
  one-line ADR pointer when it restates a recorded decision, deleted when it
  is stale (old module names, keys renamed at steps 4–6).
- Prompts, French messages, warnings, labels and fixtures are untouched: the
  prompt and lint snapshots are the proof.
- A language audit becomes a test (`tests/unit/test_language.py`): French
  stopwords in a comment or docstring fail the suite; quoted French (« », back
  ticks) is allowed, since comments legitimately name prompt text.
- The safety net's scaffolding is closed: no `sys.path` wiring in
  `conftest.py` (pytest's `pythonpath` does it), no xfail, no test whose
  subject no longer exists, no reference to the old layout.

## Doctrines relied on

- 5 (instruments lie): the snapshots are the only proof that a comment pass
  changed no served text.
- 7 (falsify both ways): the audit test is shown to fire on a French comment
  before it is trusted to pass.

## Variable moved

None. Served prompts, chapters and lint output are byte-identical.

## Non-goals

- Translating the author's material (bible, chapter specs and briefs,
  journal, prompts): never.
- Rewriting the historical ADRs or the plan.
