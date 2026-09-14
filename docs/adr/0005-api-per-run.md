# ADR-0005 — API: mandatory payload, artifacts per run

Date: 2026-09-10. Status: accepted. Supersedes the frozen contract of
2026-08-07 (`remote-integration-contract`, revisions 2–5) once the deck is
updated.

## Context

The API was written to a contract frozen by the talk's deck: `POST /generate`
with an empty body, idempotent, one job, artifacts at `/chapter`, `/audio`,
`/status`, `/events`. The chapter it generated was hardcoded. The keynote has
happened; a second run is scheduled in about 2.5 months and the owner
maintains the deck, so the contract can change.

A factory generates many chapters, possibly several runs of the same chapter
with different seeds. Singleton artifact routes cannot address them.

## Decision

```
POST /generate              {chapter, seed?, overrides?} → 202 {run_id}; 400 without body
GET  /runs                  list, newest first
GET  /runs/<id>/status
GET  /runs/<id>/events      SSE, status payload about once a second, closes on terminal state
GET  /runs/<id>/chapter     text/markdown with both markers; 204 until written
GET  /runs/<id>/audio       audio/wav; 204 until rendered
GET  /runs/<id>/prompts     prompts served to the model, per node and entry
POST /runs/<id>/cancel
GET  /runs/latest/...       alias of the most recent run
POST /chat, GET /characters, GET /sessions, GET /session/<c>/<ts>   unchanged
GET  /health
```

- The payload is mandatory. `chapter` must name an existing spec; `seed`
  defaults to random and is recorded; `overrides` is a whitelist of
  configuration keys (never spec fields).
- One worker: the machine holds one model. A `POST` during a run is queued,
  not refused. `/chat` keeps its `409` during generation, for the memory
  reason documented in the current code.
- A run's artifacts are read from its directory on disk (ADR-0003); the
  server holds no chapter in memory.
- `/prompts` exists for the stage (the projected brief and the served prompt
  must be the same text) and for the recopy measure of the movement method.
- Artifacts return `204` while absent, `200` when present, never `404` for a
  known run; `404` is for an unknown run id. Errors surface as `phase: error`
  in status, never as `5xx` to the client.
- Identifiers in paths are validated against a whitelist pattern before any
  file access. The server listens on a conference network.

## Consequences

- The deck's client is rewritten against `/runs/<id>/...` with the `run_id`
  returned by `/generate`, or against `/runs/latest/...`.
- The single-job lock becomes a one-worker queue; cancellation targets a run.
- The former "empty POST generates the default chapter" behaviour is gone;
  the runbook shows the payload for chapter 7.
