# ADR-0024 — Operational arbitrations of the API and the machine layer

Date: 2026-09-13 (recording arbitrations of 2026-08-06 → 09-12). Status: accepted.

## Context

The API, the progress sink, the model client and the preflight carry small
decisions that were justified only in comments. Each one shapes what the
stage sees.

## Decision

1. The deck is served at the API root, same origin, so its fetches need no
   CORS; the Slidev build directory is a read-only cross-repository
   dependency (`settings.slides_dir`).
2. `Access-Control-Allow-Origin: *` on the conference network: the service
   holds no secret and accepts no sensitive data; a mis-guessed origin on
   stage would break the demo for nothing. Tighten when the deck's origin is
   stable.
3. Per-resource fallback: an absent artifact is `204` (not ready), an
   unknown route `404`, a failure `phase: error`; never a `5xx` to the deck.
   A voice failure leaves the chapter served (ADR-0012).
4. Roleplay sessions inactive for `chat_ttl_s` (2 h) are closed AND written
   to disk, never silently dropped: they are demo material.
5. Cancellation takes effect at node boundaries only (worst delay: one model
   call). Threads are not killed.
6. Progress bands live in `factory.infra.progress`, not in the nodes, and
   are calibrated on the 17.0-minute reference run; accumulation and drift
   deliberately have no band (they hold the writing band's value).
7. Client-side context estimate: 3.3 characters per token (calibrated on a
   4065-token French prompt; 3.5 underestimated by 6 %, and a low estimate is
   the wrong error direction for an alarm); truncation alarm when Ollama read
   less than 75 % of the estimate.
8. Preflight tells an embedder from an LLM in `/api/ps` by size
   (`EMBED_SIZE_LIMIT_GB = 2.0`); the page size is pinned to 16384 bytes
   (Apple Silicon) rather than parsed from `vm_stat`.
9. Actor mode: no preflight (a conversation is watched live and stopped by
   hand), no continuation net (`num_predict = 320`, a cut reply restarts), no
   model swap during a session (the summary is produced by the acting model:
   a 13 GB reload per turn is not worth a summary).

## Consequences

- Items 2 and 8 are machine assumptions; `factory doctor` is where a
  different machine shows them wrong.
- These numbers are configuration or constants, never spec fields.
