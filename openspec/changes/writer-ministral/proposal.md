# Proposal: writer-ministral

## Why

`xp-author-models-2` (owner's blind reading, 2026-11-10): Ministral 3 14B Q5
replaces nemo by the rule written before the runs. ADR-0029 records the
decision; this change applies it.

## What changes

- `Settings.author_model` defaults to `ministral3-14b-q5`; the Modelfile is
  versioned at `docker/Modelfile.ministral3-14b-q5` (same digest as the
  measured `xp-ministral3-14b-q5`).
- Runbook (pull and create, variable table, memory), architecture, client
  docstring.
- ADR-0029.

## Variable moved

The model. No served prompt text moves: the three snapshots change only in
the `model=` header of the gesture calls (the only calls that name the
model explicitly). Regenerated and named here.

## Non-goals

- QA model, swap, context window: ADR-0008 stands.
- The actor-mode check: a task, not code.
