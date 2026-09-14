# ADR-0014 — Actor mode: our own `POST /chat` and page, not OpenWebUI

Date: 2026-08-07, extended 2026-08-08. Status: accepted.

## Context

The roleplay memory is STATEFUL on the server: a rolling summary plus indexed
session memories retrieved at session start. The OpenAI-compatible contract
that OpenWebUI speaks is stateless with the full history resent each turn; it
would bypass the summariser.

## Decision

- The API serves `POST /chat {character, message, session?, nom?}` and a
  dedicated page (`/acteur`) that can be embedded in a slide. OpenWebUI is
  removed from the stack. `chat_character.py` stays as CLI plan B.
- Memory has two levels: the last N turns verbatim, older turns fused into a
  rolling summary by the SAME model (no swap mid-dialogue).
- Sessions are REPLAYABLE: the session file has two sections, `## Ce qui
  s'est dit` (the summary, indexed, feeds later sessions) and
  `## Transcription` (verbatim, replayed on stage). Pruning a bad line in the
  transcription does not touch the character's memory. Sessions are
  pre-generated for the stage and curated by hand.
- Out-of-role guard in CODE: `hors_role()` detects assistant markers, `say()`
  relaunches ONCE citing the fault, a still-faulty reply is shown but EXCLUDED
  from memory. The first test recorded "je suis un programme informatique"
  into the summary: an unfiltered slip is a persistent belief.
- Example lines in the actor prompt are formulated as ATTITUDES, not text:
  two spectators asking the same question got the same scripted line.
- Session identifiers in paths are validated by WHITELIST before any file
  access; the server listens on a conference network.

## Consequences

- Residual acting tics are treated by CURATION of the pre-generated sessions,
  not by more prompt rules: each added rule moved the defect elsewhere.
- Chat is refused (`409`) while a chapter generates: same model, one slot.
