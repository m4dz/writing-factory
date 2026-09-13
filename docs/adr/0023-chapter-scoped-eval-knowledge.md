# ADR-0023 — Chapter-scoped reading rules stay in the eval package

Date: 2026-09-13. Status: accepted.

## Context

ADR-0002 puts chapter knowledge in `chapters/NN-slug/spec.yaml`. Three
reading rules of the lint are scoped by chapter number and live in eval code:
material prohibitions with a `chapter_min` (phone messages become legitimate
from chapter 5), reserved terms (`la tierce`, `l'errata`, `le bon à tirer`)
linted for absence in chapters 1–8, and the chapter-7 quartet (photos,
playlist, plat des anniversaires, couverts) forbidden everywhere else. Two
served constants are of the same kind: `NEGATIVE_FACTS` and `PILOT_VOCAB` in
the QA, `_FRONTIER_ANCHORS` in the gestures.

## Decision

These are rules of READING derived from the canon (the pilot table, the
objects sheet), not the content of one chapter; they stay in
`factory.eval.lint` and the QA as data tables, scoped by chapter number, and
the pipeline passes the chapter number to them. They are the one place where
a chapter number is legitimate outside `chapters/`. Moving them into the
specs (a `lint:` block per chapter) is deferred until the owner writes the
specs of chapters 1, 3–6 and 8–11; the tension with ADR-0002 is acknowledged,
not resolved by moving lists nobody has re-read.

## Consequences

- `material_forbidden(text, chapter)`, `chapter_constraints(n)` and the
  quartet keep their signatures; `chapter = 0` means "every rule applies".
- A new chapter with a spec but no row in these tables is linted with the
  default scope; the grid says so rather than staying silent.
