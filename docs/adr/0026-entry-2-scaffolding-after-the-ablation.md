# ADR-0026 — Chapter 7 entry 2 scaffolding after the ablation

Date: 2026-10-18 → 19. Status: accepted (amended after `plan-state-beats`).
Amends ADR-0020.

## Context

`scaffold-ablation` removed one piece of the entry 2 scaffolding per arm,
three seeds each, read blind by the owner
(`experiments/runs/20261018-scaffold-ablation/report.md`). Production
accomplished the declared movement on no seed (0 yes, 1 partial, 2 no); the
only two "yes" came from entry 2 in one call (A4), which is a bundle: no
pruning, the verdict skeleton served, the whole movement, no beat suffix.

Rule written before the runs, applied per piece:

| piece | rule | note |
|---|---|---|
| best-of-3 per beat | removable | no worse than R on 3/3 |
| deterministic pruning | load-bearing | resolution 2/3 without it |
| accumulation | removable by the letter | floor effect: R is "no" on those seeds; half the entry's mass |
| code-capped beats | removable | better than R on 2/3 |

`plan-state-beats` then served each beat the entry with each time's state
and its answer begun on the text already written (arm P,
`experiments/runs/20261019-plan-state-beats/report.md`): P 2 yes / 1
partial, R 1 / 2 on the same reading; rule inconclusive; the owner keeps P
as the reference. P's checks (recopy, empty beat, third person) only act
through the best-of: with one draw they can only warn.

## Decision

1. **Keep the pruning.**
2. **Keep the accumulation**, against the letter of the rule: the rule had
   no density criterion, and the owner's notes on A3 are about density. Its
   paragraph resolved the doubt in the two `plan-state-beats` smoke runs;
   deferred by the owner to a later change.
3. **Keep best-of-3 per beat** while P is the reference: P's progress gate
   needs variants to choose between (smoke v2: 6/9 empty variants). The
   ablation's "removable" is measured again after the model XP.
4. **Do not flip entry 2 to `strategy: single`** on three seeds. The
   reference arm of the next experiments is P (`--override
   beat_context=plan`); production keeps `beat_context: blind` until a
   series decides otherwise.
5. **Doctrine 8 (« je décide de ») is a tie-breaker in the selection**
   (−2), not a veto: E03, the best draw of the ablation, holds eight.
   Merged with the other selection fixes of `detector-fixes`: perceived
   presence by hearing, open hypotheses not counted as dismissals, the
   restart exemption limited to the chapter's first entry.

## Consequences

- No change to `chapters/07-anniversaire/spec.yaml`; `beats_n` stays 3.
- The production selection changes with item 5 (`detector-fixes`): runs
  drawn before it are compared with that in mind.
- The model XP runs on P; `storyboard-density` serves its actions through
  the plan state, its R arm being P on the model kept.
- Every decision rule now carries a density criterion: "no worse than R"
  means little when R fails.
