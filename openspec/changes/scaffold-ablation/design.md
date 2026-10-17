# Design: scaffold-ablation

## Protocol

- Chapter 7, full chapter generated (both entries), `--no-render`: the voice
  is not under test. Only entry 2 is compared.
- Seeds: three, drawn once, identical for every arm (paired draws). They are
  written in the experiment manifest before the first run.
- Machine: preflight strict, both clocks recorded, laptop plugged in,
  `caffeinate -is` (runbook §0). Arms run interleaved by seed (R1 A1₁ A2₁ …
  then R2 …), not arm after arm, so machine drift does not line up with an
  arm.
- 5 arms × 3 seeds = 15 runs, ~6 min each, about 1 h 30 including swaps.

## Measures, per run

| Measure | Source | Role |
|---------|--------|------|
| Defects in the final entry 2: resolves, dismisses, restarts, presence, recursion, forbidden decor | existing reading checks (`factory.pipeline.graph`) | veto counts |
| Same defects on every pre-selection variant | `variants.md` | what best-of and pruning were hiding |
| Sentences removed by pruning | pruning log | A2 vs R |
| Words, loop / litany (repeated discoveries) | lint + grid | A4 especially (one call looped in August) |
| Accumulation present / valid | grid | A3 |
| `write` time, total time, both clocks | manifest | record only |
| **Is the declared movement accomplished?** | owner, reading aloud, blind | the verdict |

Blind reading: `factory eval ablation --blind` writes the 15 entries 2 in a
shuffled order with neutral ids; the key stays in the experiment directory
until the owner has written their verdicts.

## Decision rule (written before the runs)

A piece is a removal candidate when, on its arm: the owner's verdict is no
worse than R on at least 2 seeds of 3, AND no veto defect appears in the final
text that R does not have. A piece is load-bearing when its arm shows the
defect it was built against on 2 seeds of 3 or more. Anything in between is
reported as inconclusive; three seeds do not support a finer claim.

## Code

- `cli.generate`: `--spec-file PATH` loads with `load_spec(PATH)` instead of
  `load_chapter(N)`; the loader's anti-leak assertions apply unchanged. The
  run directory gets `spec.yaml` (the variant) and the manifest gets
  `spec: {source, diff}` against the canonical spec of the same chapter.
- `cli.generate`: `--option KEY=VALUE`, whitelist `rag`, `micro_nodes`,
  `segments`, passed to `spec.state()`. Distinct from `overrides` (machine
  knobs, ADR-0005), recorded under `options:` in the manifest.
- `runs.py`: `variants.md` written from the best-of log (variant text, score,
  defects named, winner).
- `factory.eval.ablation`: reads N run directories, groups them by the
  experiment manifest's arm map, prints the table above, `--blind` mode.

## Prior fix: the false positive of the resolution check

`_BEAT_RESOLVES` matched « Je me souviens parfaitement de ma soirée de la
veille » although the draw ends open. The check is narrowed to remembering
the GESTURE (the place settings, the photos, the dish, the music), not any
memory. It must, on the 12 C5 draws: flag none of the 12 (all held, owner
verdict) and still flag every resolving variant in the journal entries of
2026-08-29/31 that it flags today. Both lists become a unit test.

## Tests and snapshots

- Snapshot `ch7` unchanged: arm R is production.
- New stage test: a variant spec with entry 2 `strategy: single` produces one
  write call for entry 2 with the fake model; the manifest records the diff.
- New unit test: `--option` refuses a key outside the whitelist.
- New unit test: the resolution check over the C5 and journal lists above.
- Fake model fixtures: one nominal single-call entry 2 fixture for A4.

## Output

`experiments/runs/<date>-scaffold-ablation/`: `manifest.yaml` (seeds, arms,
commit), `specs/` (the A4 variant), the 15 run directories or links to them,
`blind/` (shuffled entries and key), `report.md` (table, owner verdicts,
decision per piece). Failed or surprising draws go to `experiments/journal/`
(doctrine 13).
