# ADR-0008 — Model triage: nemo writes, Qwen checks, one swap

Date: 2026-08-06. Status: accepted.

## Context

A chapter must be generated in about 25 minutes on a MacBook M3 Pro with
18 GB of unified memory. Benchmarked candidates: `mistral-small` 24B (better
prose, places both signature lines, zero English leak) at ~3 tok/s under
memory pressure, giving a chapter in about an hour; `mistral-nemo` 12B Q8_0 at
~10 tok/s, chapter in ~20 min, near-zero leak.

## Decision

- **Author and actor:** `mistral-nemo:12b-instruct-2407-q8_0`. Mistral-small
  stays the quality option for writing outside the timed demo.
- **QA and lint:** `qwen2.5:7b-instruct` (Q4_K_M, ~4.7 GB, ~26 tok/s), another
  lineage (no leak tendency), reliable in French, disciplined on format.
- **One swap.** QA runs after all generation; nemo is unloaded (`keep_alive:
  0`) before Qwen loads. `OLLAMA_MAX_LOADED_MODELS=2` would allow both warm
  (17.8 GB on 19.3 GB), which is the pressure that panicked the machine; the
  limit counts models, not gigabytes, so the code enforces the swap.
- `num_ctx` is explicit at 8192: Ollama's 4096 default silently slid the
  window and cut the French guard and the bible facts from the head of the
  prompt. Two reliable signals are recorded per call: `ctx_need` (client
  estimate) and `ctx_truncated` (Ollama read less than 75 % of what was sent);
  `ctx_fill` is capped at 1 by construction and cannot serve as an alarm.

## Consequences

- Gesture micro-nodes (accumulation) run on nemo inside the writing loop: a
  Qwen call there would cost two swaps per entry (139–222 s measured).
- Model names, context window and temperatures are configuration, not
  chapter spec (ADR-0002).
