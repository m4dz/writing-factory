# ADR-0022 — Arbitrations of the lint and the grid

Date: 2026-09-13 (recording arbitrations of sessions 1 → 7). Status: accepted.

## Context

The lint (`factory.eval.lint`) and the grid (`factory.eval.grid`) judge a
run by counting named defects. Several of their rules are arbitrations, not
measurements; they were justified only in comments. Recorded here so they
can be contested as decisions.

## Decision

1. **Passé simple**: only unambiguous forms are detected; the three ambiguous
   detectors emit CANDIDATES, never a verdict. A false positive on the sheet's
   first prohibition costs more than a miss.
2. **Meta terms** (workshop vocabulary) are a frozen list; `constat` and
   `verdict` are exempt as the narrator's own trade words. **Machinery
   terms** (what may never appear in a served context: `le code`, `grille`,
   `pipeline`, `lexiques`, …) are a second list; `la table` is exempt.
3. **« je décide de »** is capped at one occurrence per entry (owner
   arbitration, 2026-08-18). The near future (« je vais ») is not a decision;
   notebook operations (noter, reprendre, relire…) are excluded from the
   decision → execution pairing.
4. **Repetition** is measured in characters, no length floor: two paragraphs
   are repeats at ≥ 0.50 similarity with a common block ≥ 30 characters;
   paragraphs composed by the code (header, anchor, drift, accumulation) are
   protected from removal. Tabulated against S6-3 before adoption.
5. **Prompt copy**: a paragraph at ≥ 0.50 similarity with a served
   instruction is a recopy (chapter 2 legitimately peaks at 0.37).
6. **Two layers**: voice lints run outside quotations, the prose contract
   everywhere.
7. **Decision rule of a series**: 2 runs out of 3; a failure is triaged as
   mechanical (the sheet) or structural (the prompt).
8. **Dates**: two entries the same day are legitimate; only a date going
   backwards fails.
9. **Leak lexicon**: `disparue` and `tombe` are ambiguous after a homograph
   false positive; the seal lexicon (ADR-0017) keeps them as hard words, the
   lint demotes them to a warning.

## Consequences

- Any of these numbers moves through an openspec change that names the run.
- The lists of items 2 and 9 are eval data; the owner is asked before a word
  is added to or removed from them.
