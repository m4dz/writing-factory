# ADR-0029 — The writer is Ministral 3 14B

Date: 2026-11-10. Status: accepted (author); actor mode pending its check.
Supersedes the author and actor line of ADR-0008; the rest of ADR-0008
(Qwen checks, one swap, explicit `num_ctx`) stands.

## Context

ADR-0008 chose `mistral-nemo` 12B Q8_0 on speed under the 25-minute stage
budget. Since then, nemo was measured reciting its served instructions in 6
to 8 variants out of 9 (`beat-instruction-form`). `xp-author-models` rejected
Ministral 3 14B by a mechanical rule, on a run killed by a harness defect
(the term guard applied to re-served model prose, fixed by
`beat-guard-model-text`). `xp-author-models-2` compared nemo (N), Ministral 3
14B Q5_K_M (M) and Mistral Small 3.2 24B Q3_K_M (S) on chapter 7, three
seeds, judged by the owner's blind reading of entry 2
(`experiments/runs/20261020-xp-author-models-2/report.md`).

| arm | yes / partial / no | recite (variants) | leaks read | mean time |
|---|---|---|---|---|
| N | 1 / 2 / 0 | 6, 7, 8 / 9 | 3 | 345 s |
| M | 3 / 0 / 0 | 4, 1, 1 / 9 | 0 | 365 s |
| S | 1 / 1 / 1 | 1, 1, 1 / 9 | 1 | 562 s |

Rule written before the runs: M at least equal to N on 3 seeds, worse on
none, replaces N; S worse on 2 seeds is dropped.

## Decision

- **Author:** `ministral3-14b-q5`, the HF GGUF
  `Ministral-3-14B-Instruct-2512` Q5_K_M under the library template without
  its default system prompt (`docker/Modelfile.ministral3-14b-q5`, digest
  `87501e5270dc`, measured as `xp-ministral3-14b-q5`). Default of
  `Settings.author_model`; gestures follow it (`gesture_model` empty).
- **Actor:** the same model, once the actor-mode check passes (one session
  in character, French throughout, memory written and reloaded). Until
  then, `factory chat` with nemo stays available through `AUTHOR_MODEL`.
- **Stage and book alike.** 365 s per chapter fits the 25-minute budget.
  nemo stays a valid override, for replaying earlier runs.

## Consequences

- 10 GB loaded against nemo's 13 GB: more room for the QA swap.
- Defects M brings, each with its guard: entry 1 transposed to the third
  person or opened on a quotation (`entry1-notebook-checks`, plus the
  owner's rewrite of the entry-1 matter); the quotation recopied in
  Markdown italics (to strip in code before the stage); third person
  retained on some beats (as nemo; watched).
- A prepared plan fingerprints the author digest: re-creating the tag from
  another GGUF refuses the resume.
- Density stays low on most entries whatever the model: the next variable
  (`storyboard-density`, after the stage).
