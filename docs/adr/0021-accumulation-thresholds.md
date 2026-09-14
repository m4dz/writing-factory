# ADR-0021 — Accumulation thresholds and the asymmetric tolerance

Date: 2026-09-13 (recording arbitrations of 2026-08-09 → 08-25). Status: accepted.

## Context

The accumulation sentence (ADR-0018) is validated by code. Its thresholds
and tolerances were decided run by run and lived only in comments of
`factory.pipeline.gestures` and `factory.eval.lint`; the language pass moved
them here.

## Decision

1. Floor: 60 words and 6 commas in ONE sentence (sheet v3). The lint keeps a
   second, historical pair (45 words, 4 commas) so that the runs of sessions
   1–2 stay comparable; comparability wins over a single constant.
2. Ceiling: 120 words, soft. A hard ceiling at 1.4× (168 words) rejects the
   candidate even on the last attempt: beyond it the sentence is a runaway
   litany, and no accumulation beats a truncated one.
3. Last-attempt tolerance applies to the COUNT only (a little short or a
   little long is a style defect, an absent accumulation a blocking one). A
   broken form — an inner period, a semicolon — is refused to the end.
4. The language is checked first: an English sentence is not "a bit short",
   it is not an accumulation (gap found by the safety net, closed at step 5).
5. Abstraction: at most 20 % of abstract items (`ACC_ABSTRACT_MAX = 0.20`).
   This replaces the protocol's "verbal propositions" criterion, which
   rejected the reference (12 % verbal). Measured: reference 0 %, six stage-C
   accumulations 0 %, the C2 table of contents 47 %.
6. Forbidden decor is BLOCKING in `accumulate` only, a flag in the writing
   text: automating a check and making it blocking are two decisions, and the
   accumulate node was the channel through which generic furniture entered.

## Consequences

- Changing a number here changes a served behaviour; the change names the
  run that motivates it and moves through an openspec change.
- The lint's dual thresholds stay until the pre-v3 runs are no longer read.
