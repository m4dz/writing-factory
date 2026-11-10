# Proposal: xp-author-models-2

## Why

`xp-author-models` (2026-10-19) rejected Ministral 3 14B by a mechanical rule
(one run killed by the term guard, third-person warnings, slower, shorter)
before any reading; the owner set that blind set aside. Since then:

- `beat-instruction-form` measured that nemo recites the beat instruction in
  6–8 variants out of 9; Ministral recited in 1–2 of 9 on the same prompts.
- The owner's reading is the gate, not a defect count (decision of
  2026-10-20); the form stays prose (R).
- `beat-guard-model-text` removes the crash that killed the Ministral run (a
  model-written « grille » re-served as the begun entry). This branch is cut
  from it.

The owner orders a new comparison with Mistral Small 3.2 24B added. ADR-0008
judged Mistral Small the better writer but too slow (~3 tok/s under memory
pressure); at Q3_K_M it fits the Metal budget of this 18 GB host.

## What changes

Nothing in `src/` beyond the guard fix this branch carries. An experiment:
`experiments/runs/20261020-xp-author-models-2/`.

| arm | tag | quant | size |
|---|---|---|---|
| N (reference) | `mistral-nemo:12b-instruct-2407-q8_0` | Q8_0 | 13 GB |
| M | `xp-ministral3-14b-q5` (Modelfile from `xp-author-models`) | Q5_K_M | 10 GB |
| S | `xp-mistral-small32-24b-q3` (Modelfile, see manifest) | Q3_K_M | 11 GB |

One variable: the author tag. Prose beats, `beat_context=plan`, `--no-voice`,
strict preflight, QA unchanged, temperatures unchanged, 3 fresh seeds.

## Risks

- **Q3 quantization** degrades French and fine style; the reading judges it.
- **Template**: the HF GGUF of Mistral Small may inject a default system
  prompt or refuse to continue a begun answer, as Ministral's did; the smoke
  checks both before any counted run.
- **Speed**: Mistral Small was dropped for speed once; time is reported, the
  owner weighs it.
- **Blindness**: third person and length may reveal arms; noted, not fixable.
