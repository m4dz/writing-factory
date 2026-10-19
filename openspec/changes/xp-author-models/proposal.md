# Proposal: xp-author-models

## Why

ADR-0008 chose `mistral-nemo` 12B Q8_0 as author for speed: `mistral-small`
24B wrote better (both signature lines, zero leak) but ran at ~3 tok/s under
memory pressure. Two newer models fit the same memory envelope and might close
that gap:

- **Ministral 3 14B Instruct (2512)**, Mistral lineage, distilled from the
  Small generation, Apache 2.0. At Q5_K_M it weighs 9.6 GB, less than nemo's
  13 GB, so it should be as fast or faster.
- **Gemma 4 12B** at Q8_0, 13 GB, the same footprint as nemo; another lineage,
  multilingual.

Rejected before testing (session of 2026-10-18): the DeepSeek family (no small
native model; `deepseek-r1:14b` is a Qwen2.5 reasoning distill that spends
`<think>` tokens and leaks), Phi-4 (weak French, weak fiction), Qwen3 as
author (leak risk; kept for a later QA experiment).

This is step 2 of the owner's sequence: the model kept here carries the
expensive `storyboard-density` runs.

## What changes

Nothing in `src/`. `author_model` is already an override and the gesture
model follows it (`effective_gesture_model`). The change is an experiment:
`experiments/runs/20261019-xp-author-models/` with its recipe, its manifest
(model tags and Ollama digests), the predictions written before the first
draw, and the report.

## Protocol

One variable: the author tag. Same commit, same sitting, machine plugged in,
strict preflight, `--no-voice`, `beat_context=plan` (the owner's reference
since plan-state-beats), QA unchanged (`qwen2.5:7b-instruct`), pipeline
temperatures unchanged (Mistral advises < 0.1 for Ministral 3 in
production and allows higher for creative use; tuning it would be a second
variable).

| arm | tag | quant | size |
|---|---|---|---|
| N (reference) | `mistral-nemo:12b-instruct-2407-q8_0` | Q8_0 | 13 GB |
| M | `xp-ministral3-14b-q5` (see below) | Q5_K_M | 9.6 GB |
| G | `gemma4:12b-it-q8_0` | Q8_0 | 13 GB |

**G dropped** by the owner before any draw (2026-10-19): Gemma 4 thinks by
default (empty answers; `think: false` needs a `src/` change), restarts a begun
answer instead of continuing it, and loads at 14 GB with 12% on CPU at 4k
context. The experiment is N against M, 6 counted runs.

**Packaging of M.** The HF GGUF (`hf.co/mistralai/Ministral-3-14B-Instruct-2512-GGUF:Q5_K_M`)
ships a Jinja template that Ollama runs as-is: it injects Le Chat's ~530-token English
system prompt when no system message is sent (the pipeline folds the system into the
user turn for continuation calls) and does not continue a begun answer. Ollama's
library template for `ministral-3:14b` continues correctly but injects the same
default. Arm M is the same weights under the library template minus that default
(`Modelfile.ministral3-14b-q5`). Checked: 11 prompt tokens for a one-line question,
a begun answer is continued, not restarted.

N is re-drawn rather than reused from plan-state-beats: `detector-fixes`
was merged since, so the selection differs.

1. **Smoke**, seed 111111, M and G only, not counted. Stop rule per arm:
   non-French text, empty or < 2-sentence variants on most beats, broken chat
   template (role tokens or markup in the text), or a chapter over 2× N's
   time. A failing arm is reported and dropped, never tuned in this change.
2. **Arms** × seeds 395959, 528559, 781771 (the P seeds), interleaved by seed,
   the previous model unloaded between runs.
3. **Blind set**: entry 2 of the six final chapters, shuffled, key closed;
   owner verdict per entry (oui / partiel / non + note), as in
   plan-state-beats.

## Decision rule (written before the runs)

A challenger is adopted if, against N: better on ≥ 2 seeds in the blind
reading, AND no veto defect absent from N, AND zero lexical leak, AND mean
chapter time ≤ 1.25 × N's. Rejected if worse on ≥ 2 seeds, or any counted run
not `ready`. Both adopted: the better tally wins, then the faster. Otherwise N
stays (the incumbent keeps ties).

If a challenger is adopted, a short actor-mode check (one character, three
questions) follows before an ADR supersedes ADR-0008.

## Risks

- **The grid was calibrated on nemo's defects** (doctrines 4, 5). A new
  lineage fails differently: Markdown emphasis, English calques, a
  different rhythm of resolution. A clean grid on M or G proves less than
  on N; the blind reading decides (doctrine 3), the grid only vetoes.
- **The served prompts were tuned against nemo** over 31 failed runs. A
  challenger is judged on prompts written for its rival; a loss is "worse
  under nemo's prompts", not "worse". The report names it that way.
- **Template.** The HF GGUF brings its own chat template; a wrong one shows
  as role tokens in the text or a dropped system prompt. The smoke run
  checks `prompts.md` and the first variants for it.

## Out of scope

The QA model (`qwen3:8b` no-think, later, one variable); quantization sweeps;
temperature tuning; the abliterated-nemo design on
`claude/writer-unsloth-experiments-fb7gik` (not merged, separate question).
