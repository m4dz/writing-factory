# ADR-0013 — Audio switch posed by code; clone reading bounded in seconds

Date: 2026-08-07, revised 2026-08-08 and 2026-08-26. Status: accepted.

## Context

On stage the speaker reads the chapter aloud, then the cloned voice takes
over. The deck needs a reproducible marker and an excerpt of 2'30–3'00 played
in full. A marker placed by the model would land elsewhere at every draw.

## Decision

- The switch (`<!-- BASCULE -->`) is inserted by code after the SECOND
  SENTENCE; a paragraph boundary depended on nemo's paragraphing and varied
  per run. For chapter 7 the switch is on the SECOND DATED HEADER: two
  entries the same day, the speaker reads the one where she resists, the
  clone the one where the day has won.
- The excerpt read by the clone is bounded in SECONDS (`AUDIO_SECONDES=165`),
  the unit of the need, converted to words through the clone's MEASURED rate
  (177 words/min on a 540-word excerpt; the first estimate of 190 came from a
  117-word sample). The deck reasoned at ~150 words/min: its 450 words would
  have given 2'22, below its own floor.
- The fall line is ALWAYS read: the bound must not cut "Constat :
  anniversaire.", the sentence the clone speaks for. `<!-- FIN AUDIO -->`
  marks where the voice stops; the served chapter stays WHOLE.
- Both markers are GUARANTEED present: the deck treats a chapter missing
  either as not ready and falls back silently.

## Consequences

- A dated header counts as two sentences, so the sentence-mode switch on a
  one-sentence first entry lands after the header (finding of the safety
  net); the switch rule becomes a chapter spec field.
- The header format is owned by code (`Samedi 14. Beau temps.`), because the
  switch depends on recognising it.
