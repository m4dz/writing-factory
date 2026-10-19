# ADR-0026 (proposal) — Chapter 7 entry 2 scaffolding after the ablation

Date: 2026-10-18. Status: **superseded** by `docs/adr/0026-entry-2-scaffolding-after-the-ablation.md` (accepted, amended, 2026-10-19). Was: proposed; nothing in
`chapters/07-anniversaire/spec.yaml` changes without their go.

## Context

`scaffold-ablation` removed one piece per arm, 3 seeds each, and the owner
read the 15 entries blind (`report.md`). Production (R) accomplished the
declared movement on no seed (0 yes, 1 partial, 2 no). The only two "yes"
of the series came from A4, entry 2 in one call instead of code-capped beats.
The beat arms carry most of the owner's "invents" notes; the beats are served
alone, without the whole movement.

Rule written before the runs, applied per piece:

| piece | rule | note |
|---|---|---|
| best-of-3 per beat | removable | no worse than R on 3/3 |
| deterministic pruning | load-bearing | resolution 2/3 without it |
| accumulation | removable by the letter | floor effect: R is "no" on those seeds; half the entry's mass |
| code-capped beats | removable | better than R on 2/3 |

## Decision (proposed)

1. **Keep the pruning.**
2. **Keep the accumulation**, against the letter of the rule: the rule has no
   density criterion, and the owner's notes on A3 are about density.
3. **Best-of off for beats** (`beats_n: 1`) wherever the beats stay. It
   divides beat calls by three and the reading does not miss it.
4. **Do not flip entry 2 to `strategy: single` on three seeds alone.** Make
   the single call the reference arm of `storyboard-density` XP A, against
   beats that see the whole movement and their own actions. Three draws
   reverse the presumption that the beats are needed; they do not yet
   establish the replacement.
5. **Doctrine 8 ("je décide de")**: measured and penalised in the selection
   (branch `detector-fixes`), not a veto. E03, the best draw, holds eight.

## Consequences

- `storyboard-density` XP A arms become: single (new reference), R-long,
  storyboard beats seeing the whole movement — the old R is reported, not
  re-run.
- Run cost drops with `beats_n: 1` (a machine override, ADR-0005; no spec
  change needed for experiments).
- The decision rule needs a density criterion before the next ablation;
  "no worse than R" means little when R fails.
