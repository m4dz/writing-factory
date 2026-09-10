# ADR-0001 — Code in English, author material in French

Date: 2026-09-10. Status: accepted. Supersedes the convention "le code et ses
commentaires aussi [en français]" written in `CLAUDE.md` on 2026-08-05.

## Context

The codebase was written in French over seven measurement sessions, by an
assistant working in French with a French-speaking owner. Identifiers are
mixed within single modules (`derive_facts` next to `valider_accumulation`),
directory names are French (`outillage/`, `journal-des-murs/`), and comments
are dense (27–34 % of lines in the core modules) because they carry the
rationale of every threshold and every retry: dates, measurements, the run
that motivated the rule.

The project is about to be restructured into a package and opened to a longer
life than one keynote. Mixed-language identifiers cost every reader a
translation step and make grep unreliable. Comments that hold decision history
cannot be translated without loss, and they are not where decision history
belongs.

## Decision

1. Code, comments, docstrings, identifiers, module and directory names, test
   names, commit messages and engineering documents are written in English.
2. The author's material stays French and is never translated: prompts and
   prompt templates, the bible, chapter specifications and briefs, the journal
   of failed runs, lint grids, generated chapters, roleplay sessions.
3. Comments state what the code does and the one-line reason. The history
   behind a rule (which run, which measurement, which session) moves to an
   ADR when it is a decision, or to the journal entry of the run when it is a
   measurement. A comment may cite the ADR or the journal entry by name.
4. The translation is done module by module during the packaging step
   (identifiers, names) and finished in a dedicated language pass (comments,
   docstrings), with a grep audit as exit criterion.

## Consequences

- Every French identifier is renamed once, during the move into the package,
  so history stays readable (`git log --follow` across the rename).
- Prompt templates are French text files inside the package; the code that
  renders them is English. The boundary is the file extension.
- The doctrines document and the ADRs absorb the rationale that comments
  carry today. Until that extraction is complete, the French comments stay
  where they are; nothing is deleted before it has a new home.
- Reviewers of a change that adds a French identifier or an English string
  inside a prompt template reject it.
