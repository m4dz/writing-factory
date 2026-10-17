# api

## ADDED Requirements

### Requirement: The payload is mandatory and names a chapter

`POST /generate {chapter, seed?, overrides?}` SHALL create a run and answer
`202 {run_id}`; without a body or with an unknown chapter it SHALL answer `400`.

#### Scenario: Empty POST
- **WHEN** a client POSTs `/generate` without a body
- **THEN** the server answers `400` naming the expected payload and the available chapters

### Requirement: One worker, a queue

Runs SHALL execute one at a time in POST order; a POST during a run SHALL be
queued, never refused.

#### Scenario: Second POST during a run
- **WHEN** a client POSTs `/generate` while a run is generating
- **THEN** the server answers `202 {state: queued, position: 1}`

### Requirement: Artifacts per run, read from disk

`/runs/<id>/chapter|audio|prompts|manifest` SHALL serve the run directory's
files (`204` while absent); `/runs` SHALL list newest first; `latest` SHALL
alias the newest run.

#### Scenario: TTS failed
- **WHEN** the chapter was written but the voice rendering raised
- **THEN** `/runs/<id>/chapter` is `200` and `/runs/<id>/audio` is `204`

## REMOVED Requirements

### Requirement: Generation is a single idempotent job

**Reason**: replaced by the run queue of ADR-0005. The singleton routes
answer `410` with a pointer.

**Migration**: the deck client POSTs `{chapter: 7}` and follows
`/runs/<id>/…` or `/runs/latest/…`.
