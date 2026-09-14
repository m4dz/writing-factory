# ADR-0017 — The indexing firewall: two layers, three barriers, whitelists, name translation

Date: 2026-08-22. Status: accepted.

## Context

*L'Involontaire* reads in two layers: a surface truth the author model may
know, and a deep truth (the narrator is dead, the notebook is her widow's) it
must NEVER reach. The novel holds only if the model does not know what the
reader does not know. The bible carries both layers; the seal cannot be a
matter of discipline.

## Decision

Three independent barriers in the indexer, coarse to fine, each one standing
if another falls:

1. Whole paths never read: `bible/profond/`, `style-auteur.md`.
2. In a mixed file, only `### [SURFACE]` blocks; a `[PROFOND]` block is never
   even loaded. The same bracket convention works at section level
   (`## [RÉSERVÉS — chapitre 7…]` in `objets.md`).
3. In a character sheet, only NUMBERED sections; unnumbered ones are working
   notes (Judith's cites the deep chronology).

Plus: metadata keys copied to Chroma are a WHITELIST (a `depends_on` named
the deep chronology); the narrator's first name is TRANSLATED at index time
("Judith" → "la narratrice", label included), because the novel reserves it
for chapter 8 and run BC wrote it in prose.

The seal test (`etancheite.py`) audits the CONTENT of the collection, not the
routing of queries: inventory against a manifest of allowed sources, lint for
deep markers and a leak lexicon, splitter test on the Judith sheet, a POSITIVE
WITNESS (an injected deep chunk MUST come back, then is removed), and the
routing journal of the runs. It is re-proven at every reindex, never presumed.

Corollaries for served material: the movement column (`bible/profond/
mouvements-chapitres.md`) is deep; only the current chapter's line reaches
the brief. Served briefs must name no bible file (an assertion strips and
checks). Deep material lives in `docs/` and `experiments/`, which the indexer
never reads: the exclusion is structural.

## Consequences

- `chapters/` (author-owned specs) is outside `bible/` and never indexed; the
  seal test gains a control for it at revamp step 5.
- The lint's leak lexicon and deep markers live in `outillage/*.txt`, outside
  `bible/`, so they can never be indexed by accident.
