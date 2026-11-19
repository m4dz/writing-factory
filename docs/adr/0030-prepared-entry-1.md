# ADR-0030 — Entry 1 is written the day before, picked by the owner

Date: 2026-11-19. Status: accepted (owner). Amends ADR-0028: « a prepared
thread never writes » holds for chapters without a prepared entry.

## Context

Entry 1 of chapter 7 — two sentences, read with the bare voice — is a draw
of M on stage. `entry1-decision` showed the selection takes the decision
whenever a draft holds it, and that a draft holds it in ~27 % of cases:
best-of-6 serves it ~85 % of the time, never always. A sentence the speaker
reads aloud cannot be a 15 % gamble, and the code cannot score into a draft
what the model did not write.

## Decision

A spec entry may be `prepared` (the first one, with a best-of). An approved
prep then writes it: the drafts are drawn, the owner picks one at the
terminal (Enter: the first ranked), it is finished, reviewed and repaired,
and the thread ends. A resumed run keeps it (`frozen`) and writes the rest.
The pick is an interrupt node (`prep_pick`) that holds no model call before
its interrupt; the finishing of a draft is one function for the winner and
the pick.

## Consequences

- The stage run no longer writes, reviews or repairs entry 1: shorter, and
  entry 1 is read before the event.
- The owner picks, never edits: to change entry 1, prepare again (the
  fingerprint already refuses a resume after a spec edit).
- The unsplit run is unchanged; a prepared run serves the same calls in
  another order.
- Entry 1's prompts and drafts live in the prepared run (`prompts.md`,
  `variants.md`), not in the stage run's.
