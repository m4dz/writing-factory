# ADR-0025 — Served constants that remain in code

Date: 2026-09-13. Status: accepted (revisit at the next chapter spec batch).

## Context

Doctrine: the model supplies matter, the code holds the gesture; chapter
knowledge is data. A few phrases and lists served to the model are still
Python constants, each for a reason recorded here so that nobody presumes
they are spec fields:

- `EPISTEMIC_LINE` (« Le texte fait foi : l'entrée relue a toujours raison
  contre la mémoire. ») — the rule of the whole novel, not of a chapter.
- `PREAMBLE` — the reading-notebook framing; ADR-0011 said it would become a
  spec field at step 5; it did not, because it is the same for every chapter.
- `NEGATIVE_FACTS` (she does not leave the house, no other person enters, no
  screen, nothing from a shop) — world invariants added to derived facts.
- `PILOT_VOCAB` — production vocabulary filtered from derived facts.
- `_FRONTIER_ANCHORS` — the lexical anchors that place a drift passage at a
  declared frontier (plat, musique, photos, couverts, marge, verdict).
- `HEADER_LINE` in `factory.pipeline.assembly`, a copy of the lint's
  `ENTRY_HEADER`: the served module was to stay independent of the eval
  package; `factory.pipeline.gestures` imports the eval package anyway, so
  the copy is a relic.

## Decision

1. Novel-wide constants (`EPISTEMIC_LINE`, `PREAMBLE`, `NEGATIVE_FACTS`,
   `PILOT_VOCAB`) stay in code: they belong to the bible's world, and the
   owner has not asked for them per chapter. Any change is the owner's, by
   openspec change with the prompt snapshot updated.
2. `_FRONTIER_ANCHORS` is chapter lexicon; it moves to the chapter spec
   (`drift.anchors`) when the next spec is written. Until then it stays where
   the frontier is resolved.
3. `HEADER_LINE` is replaced by an import of `ENTRY_HEADER` at the next
   change touching assembly; the duplication is not a decision anymore.

## Consequences

- The seal control on `chapters/` (step 5) and the prompt snapshots are the
  guards: a served constant cannot change silently.

## Note, 2026-09-14

Items 2 and 3 done: `drift_anchors` is a chapter spec field (chapters/07-anniversaire/spec.yaml), `factory.pipeline.gestures.frontier_position` takes it from the state; `HEADER_LINE` is the lint's `ENTRY_HEADER` (case-sensitive weekday, optional bold markers — the two regexes differed in those edge cases; headers are composed by code, so neither case arises in served text). The pruning pass is `_prune_residue`, its progress label no longer says Qwen.
