# ADR-0011 — Two retrieval strategies; the style sheet is served by sections, examples stripped

Date: 2026-08-06, extended 2026-08-19. Status: accepted.

## Context

Writing an entry needs the narrator's voice and current state every time;
places and previous scenes are matter to look up. Serving the whole style
sheet (~4200 tokens) pushed the French guard out of the 8192 window. Served
examples were recited verbatim: run B′2 wrote "perplexe", the counter-example
of the lexicon section; the model copied entire previous entries when they
were in context.

## Decision

- **Deterministic by id** for the writing chunks of present characters
  (`voice`, `current narrative state`, `psychology`); **semantic top-k** for
  places and previous scenes. World chunks (`psychology`, `history`,
  `relations`) feed fact derivation, never the pilot table.
- The style sheet is read from DISK by section, never retrieved: it is an
  instruction served whole or not at all. Writing gets *Narration*, *Lexique
  et registre*, *Interdits*; review gets *Interdits*, *Phrase et rythme*; the
  planner gets none. The "Écrire / Ne pas écrire" example lines are removed
  from what is served, not from the sheet. Reference excerpts are served to
  no node.
- Previous entries are NOT served during writing (`include_scenes=False`):
  continuity goes through the narrative state and the annotated plan.

## Consequences

- The preamble (world, tense, single voice) is a constant in `retrieval.py`
  and contradicts the style sheet v3 on one point; it becomes a chapter spec
  field at revamp step 5.
- A routing journal records every collection queried during a run; the seal
  test reads it.
