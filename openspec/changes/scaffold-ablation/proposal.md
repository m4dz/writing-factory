# Proposal: scaffold-ablation

## Why

Entry 2 of chapter 7 is held by four pieces of scaffolding, all built while
fighting the resolution of the doubt (ADR-0020): beats capped by code,
best-of-3 per beat scored by reading criteria, deterministic pruning, and the
accumulation micro-node. The falsification experiment C5
(`experiments/runs/20260831-xp-resolution-c5/`) then showed the resolution
came from the served voice skeleton, not from the model: 12/12 bare draws held
the doubt once steps 5 (verdict) and 7 (couperet) were no longer served.

The skeleton amputation shipped in the same decision as best-of-3 and
pruning. No run has measured the scaffolding against the fixed root cause.
Each piece costs time on stage and creates its own defect where it touches
(doctrine 12); some may now compensate for nothing.

The next experiments (`storyboard-density`) change what is served to the
beats. They need to know which scaffolding is still load-bearing before they
build on it.

## What changes

An experiment, not a feature. Five arms on chapter 7, entry 2, same three
seeds per arm (paired), everything else at the production configuration:

| Arm | Moves | How |
|-----|-------|-----|
| R | nothing (reference, today's production) | — |
| A1 | best-of-N off | override `beats_n: 1` |
| A2 | pruning off | override `pruning_enabled: false` |
| A3 | accumulation micro-node off | run option `micro_nodes: false` |
| A4 | code-capped beats off: entry 2 written in one call | variant spec, entry 2 `strategy: single` |

One variable per arm against R; no arm combines two removals. A combined
"bare" arm (A1+A2) is run only if both A1 and A2 come out neutral, as a
confirmation, never as a first measure.

Code needed, the smallest that makes the arms reproducible:

- `factory generate --spec-file <path>`: generate from a variant spec that
  lives outside `chapters/`. The variant is copied into the run directory and
  its diff against the canonical spec is recorded in the manifest. The
  canonical `chapters/` files stay untouched (owner-owned).
- `factory generate --option micro_nodes=false` (and `rag`, `segments`): the
  run options `spec.state()` already accepts as keyword overrides, now
  reachable from the CLI and recorded in the manifest.
- Pre-selection capture: when best-of-N is on, every variant drawn and its
  score are already logged; the run directory gains `variants.md` so the
  defect rate BEFORE selection and pruning is measurable on every arm.
- `factory eval ablation <run>...`: one table per arm, defects counted by the
  existing reading checks on the final text AND on the pre-selection
  variants, timings from both clocks.

Variant specs live in `experiments/runs/<date>-scaffold-ablation/specs/`.

## Single variable

Per arm, the presence of one piece of scaffolding. The served prompts of R are
the production prompts (snapshot `ch7` unchanged).

## Doctrines relied on or challenged

- 12 (every device creates a defect where it touches): challenged in reverse.
  If the cause is gone, the device may now only cost.
- 13 (one variable between two measurements): one removal per arm, paired
  seeds.
- 3 (counting is not reading): the grid is a veto; the verdict per arm is the
  owner reading aloud, blind to the arm.
- 5 (instruments lie): the reading checks scored 1 false positive out of 12
  in C5 (`je me souviens de [contexte]`). Fixing that check comes first,
  falsified both ways on the 12 labelled C5 draws, or every arm inherits it.
- 1 (the code holds the gesture): untouched. Header, quotation, drift, fall
  and assembly stay posed by code in every arm.

## Non-goals

- Changing the brief, the spec, the bible or the served voice. The skeleton
  stays amputated as in production.
- Changing chapter 1 entry 1 (two sentences, its own best-of on erasure).
- Shipping a new production configuration. The outcome is an ADR proposal to
  the owner (keep, remove or retune each piece); `chapters/07-*/spec.yaml`
  changes only if the owner decides so.
- Stage timing. Arms are timed for the record, but timing is not the
  criterion.
