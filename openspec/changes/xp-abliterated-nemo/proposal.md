# Proposal: xp-abliterated-nemo

## Why

The owner wants to fine-tune the author model on an "uncensored" Mistral-Nemo
to unleash creativity and tone. The journal contradicts the premise: in 31
failed runs there is no model refusal; every wall is the model over-filling
(a presence in the empty house, a resolved doubt, a day at the office, an
adultery). Abliteration removes refusal behaviour and nothing else. Before any
training run, the cheapest falsification is to swap the base model alone and
measure whether an abliterated Nemo crosses the threshold less, the same, or
more. If it does not do better, the "unleash" hypothesis is closed for one
afternoon of compute, and experiment B (preference tuning on the project's own
rejected variants) starts from a measured baseline instead of a hunch.

## What changes

- The resolution recipe (`factory.tooling.resolution_xp`) becomes a proper
  experiment driver: model tag and output series directory as arguments, a
  manifest per series (model tag and Ollama digest, commit, draws, temperature,
  both clocks), raw draws in the series directory instead of the journal, and a
  refusal to start when the tag is absent from Ollama.
- A positive-control condition in the recipe: the proofreader identity WITH
  the production voice skeleton served (the condition that made stock nemo
  resolve, `experiments/runs/20260831-xp-resolution-c5/report.md`). Each arm
  must resolve there, or that arm's detector reading is not trusted
  (doctrine 4, applied per arm).
- Best-of-N verdicts persisted: the graph records every drawn variant
  (entry, beat, draw index, score, named defects, kept or rejected) in the
  state, and the run manifest carries it as `best_of`. Today the rejections
  live only in a progress note; the count of defects per cause across ALL
  variants is the metric of this experiment and of experiment B.
- Falsification tests for the resolution detectors on known texts, the
  08-31 false positive recorded as a strict expected failure.
- Runbook: pulling a Hugging Face GGUF into Ollama, running with
  `AUTHOR_MODEL` overridden, the experiment procedure.
- A run directory `experiments/runs/<date>-xp-abliterated-nemo/` with the
  predictions written BEFORE the first draw, the two arms' series, and the
  report.

## Protocol

Two arms, same commit, same sitting, machine plugged in, preflight accepted:

- **S (stock):** `mistral-nemo:12b-instruct-2407-q8_0`.
- **U (abliterated):** an abliterated build of Mistral-Nemo-Instruct-2407,
  Q8_0 GGUF, pulled as `hf.co/<org>/<repo>:Q8_0`. Same base weights, same
  quantization, abliteration only. Roleplay merges and SFT derivatives
  (Rocinante, NemoMix, Lumimaid…) are excluded: they change the training
  data, a second variable. The exact tag is the owner's pick; the session
  could not reach Hugging Face (proxy 403).

Leg 1, bare model, C5: 5 conditions (the 4 of 08-31 plus the positive
control) × 3 draws per arm, T=0.7, num_predict=300, one call per draw.
Metric: `_BEAT_RESOLVES` / `_BEAT_DOUBT` verdicts, verbatims kept.

Leg 2, production pipeline: `factory generate --chapter 7 --no-render` with
the same 3 seeds per arm, `beats_n=3`. Metrics from the manifest (`best_of`:
defects per cause across every variant, kept and rejected) and from
`lint.md` (lexical leak, proper nouns, forbidden decor, prompt copy, mass),
plus the owner's manual grid line (doctrine 3).

## Predictions, falsifiable

- P1 (leg 1): resolution rate equal between arms within one draw per
  condition; the positive control resolves in at least 2/3 on both arms.
- P2 (leg 2): U shows at least as many leak, decor and presence defects as S
  across all variants, and no fewer resolution defects.

Decision rule: 2/3 majority per metric across the three runs. The
"unleash" hypothesis survives only if U shows fewer defects on EVERY cause;
anything else closes it, with a journal entry naming the cause that killed
it. Either outcome is the baseline of experiment B.

## Doctrines relied on

- 13: one variable (the model tag), paired seeds, both arms rerun at the same
  commit rather than compared to the 08-31 table (whose detector reading
  predates the false-positive finding).
- 4: a positive control per arm; the detectors get their failing case in the
  suite.
- 5: variant verdicts persisted in the manifest, not read off progress notes;
  both clocks per series.
- 3: the grid counts, the owner reads aloud.
- 6: the positive control serves the voice skeleton. Experiment only, never
  production; the run directory says so.

## Variable moved

The author model tag. No served prompt changes: `tests/snapshots/` must stay
byte-identical.

## Non-goals

- Fixing `_BEAT_RESOLVES`'s false positive on « je me souviens parfaitement de
  ma soirée » (recorded as strict xfail; its fix is a separate change so both
  arms here are read by the same detector as the 08-31 run).
- Any fine-tuning, any training data assembly, any cloud GPU.
- Q4 or other quantizations of either arm.
- The actor mode: not measured here.
- Deciding whether author material may leave the machine for training (owner's
  ADR, prerequisite of experiment B).
