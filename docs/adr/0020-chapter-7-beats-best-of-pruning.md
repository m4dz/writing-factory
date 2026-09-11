# ADR-0020 — Chapter 7 entry 2: code-capped beats, best-of-N by reading criteria, deterministic pruning

Date: 2026-08-29 to 2026-08-31. Status: accepted.

## Context

Entry 2 of chapter 7 written in three segments produced THREE ARCS: each
segment received the whole brief with a third of the budget, tried to
accomplish the entire movement, overflowed, was relaunched, and started
again. Written in one call it looped (~400 words of "a noise in the living
room / I found"). Ten draws made the same defects recurrent: resolution of
the doubt, perceived presence, restart, metafictional recursion, forbidden
decor. The falsification experiment (C5) then showed the resolution came
from the served voice skeleton ("5. verdict … 7. couperet"), not from the
model: 12/12 draws held the doubt without it.

## Decision

- Entry 2 is served as THREE BOUNDED BEATS, each a short call that receives
  only its own instruction and the common veto, never the whole movement;
  the code bounds each in SENTENCES (4, 5, 4) and tokens, the previous text
  becomes the prefix of the next.
- BEST-OF-N per beat (N=3): the code draws N variants and keeps the one
  with the fewest NAMED defects, scored by deterministic READING checks
  (resolves, dismisses, restarts, presence, recursion, forbidden decor; open
  doubt scores positive). A selection by reading, not by taste; falsified
  both ways. Entry 1 (two sentences read aloud) uses best-of-3 on a criterion
  naming the erasure of the anniversary.
- The voice skeleton served to the beats is AMPUTATED of steps 5 and 7 in the
  served prompt only; the fall stays posed by code.
- A deterministic PRUNING pass removes sentences matching named motifs
  (outing, presence, recursion, resolution), protects header, quotation,
  drift and fall, and refuses to remove more than half.
- The seed is random per live run (owner decision 2026-09-02): true variance
  of the best-of-3 and of the drift draw on stage.

## Consequences

- Chapter 7's spec (`ch7.py`, then `chapters/07-anniversaire/spec.yaml` at
  revamp step 5) carries beats with names, token caps and sentence caps.
- Doctrine 12: every device creates a defect where it touches; the pruning
  is a whack-a-mole, reliable but to be watched.
