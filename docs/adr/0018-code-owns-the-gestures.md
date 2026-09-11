# ADR-0018 — The code owns the gestures: headers, anchor, accumulation, drift, fall, assembly

Date: 2026-08-22, extended 2026-08-27. Status: accepted.

## Context

Eleven runs and three failure modes: the model never produced the drift
passage (approach a subject, stop before naming the departure). The
accumulation sentence came neither from the sheet (three formulations) nor
from a reproach loop. The anchor quotation was altered when served as an
instruction ("recopie-le à l'identique"), the dated header came back with a
comma, dates went backwards, the fall line was missed three times out of
three. `review` and `repair` rewrite whole entries and dissolved a sixty-word
sentence.

## Decision

- **Headers** are COMPOSED (`Samedi 14. Beau temps.`) from an anchor (weekday
  + number) and derived consecutively; only the weather comes from the plan.
  Any dated header the model emits is parasitic and removed.
- **Anchor quotation** is prefixed by REAL CONCATENATION, never by
  instruction: the code writes the start, the model continues.
- **Accumulation**: the model supplies one sentence on a form instruction
  (twelve to twenty comma steps ending on an imposed fall); the code VALIDATES
  it (thresholds, no inner period, first person, under 20 % abstract items, no
  forbidden decor, no copy of the reference, French) and PLACES it before the
  verdict paragraph.
- **Drift**: the matter is written by hand (a bank of approaches and material
  facts per chapter, or a full passage delivered by the brief); the code
  draws without replacement on a recorded seed, cuts on the suspension,
  appends the fact, and places it in the reconstruction, never adjacent to
  the accumulation, never in the last third, or at a declared frontier.
- **Fall line** imposed word for word ("Constat : anniversaire.") is posed by
  code in last position.
- **Order**: gestures are set aside during writing and posed on the FINAL
  text, after `review` and `repair`, which would rewrite them; header and
  anchor are RE-STAMPED there because repair altered them (a header lost
  entirely once, and with it the audio switch). Deduplication of repeated
  paragraphs runs last and PROTECTS the composed paragraphs.

## Consequences

- Doctrine 1 (`docs/doctrines.md`). Everything the stage depends on word for
  word is composed, not requested.
- Chapter 7's per-entry structure (two same-day entries, entry 1 without
  anchor or gestures) is data in `entrees_spec`, never a loosened rule
  (doctrine 9).
