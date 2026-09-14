# ADR-0026 — The book pipeline drops the stage constraints: no time budget, swaps as needed, one machine

Date: 2026-09-14. Status: accepted (owner decision, brainstorm session).

## Context

Every generation decision since August was taken under the keynote's
constraints: a chapter in about 25 minutes on stage, one model swap per run
(ADR-0008), everything on one MacBook with 18 GB of unified memory. Those
constraints chose the writer: `mistral-nemo` 12B was retained on speed alone,
`mistral-small` 24B having measured better prose and zero leak at 3 tok/s.
They also fixed the shape of the QA phase (one swap, nemo unloaded before
Qwen) and made every extra draw a cost against the budget.

The revamp is done and the pipeline is now a veto machine that has reached
what vetoes can give: the remaining defects of the retained chapter-7 draw
(register, sentence length, genre physiology) are the model's, and no
selection among three nemo draws produces a different register. The goal has
moved from a stage demonstration to writing the book. The stage run remains a
use of the factory, not its measure.

## Decision

1. **Two regimes, one pipeline.** A *stage* run keeps the budget, the
   countdown and the single swap (`stage_budget_min`, the API's countdown,
   ADR-0008). A *book* run has no time budget: it runs unattended, overnight
   if needed, and the countdown is informative only.
2. **The single-swap rule is withdrawn for book runs.** Models are loaded and
   unloaded as many times as the graph needs; the memory ceiling stays the
   only constraint. The rule that two models are never warm together stands
   (it is the pressure that panicked the machine, ADR-0016), the rule that
   there is only one swap does not.
3. **One machine.** No second local machine. The 18 GB ceiling is the hard
   constraint of every model choice: a candidate writer must fit with its
   context window with the QA model unloaded.
4. **The writer is reopened.** Model choice is an experiment (one variable),
   run through the bench of the quality campaign, judged on the calibrated
   reference (chapter 7, entry 2) by the manual grid line and the offline
   style metrics.

## Consequences

- `docs/plans/2026-09-quality-campaign.md` carries the ordered experiments.
- Sampling and writer parameters become configuration (Settings, run
  overrides), not constants in node code.
- The review/repair pair may use the writer model instead of the 7B QA model
  once swaps are free; that is its own experiment.
- ADR-0008 stays valid for the stage regime; its "one swap" clause no longer
  applies to book runs.
