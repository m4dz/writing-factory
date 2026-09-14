# api

## Purpose

Current behaviour of the HTTP surface (`factory.api.server`): one worker, a
queue of runs, artifacts per run read from the run registry on disk
(ADR-0005, ADR-0003). The actor mode is unchanged.

## Requirements

### Requirement: The payload is mandatory and names a chapter

`POST /generate {chapter, seed?, overrides?}` SHALL create a run for a chapter
that has a spec and answer `202 {run_id, chapter, seed, position, state}`.
Without a body, with an unknown chapter, a non-integer seed or an override
outside the whitelist it SHALL answer `400` with the reason (and the list of
chapters when relevant). `seed` defaults to random and is recorded.

#### Scenario: Empty POST
- **WHEN** a client POSTs `/generate` without a body
- **THEN** the server answers `400` naming the expected payload and the available chapters

### Requirement: One worker, a queue

Runs SHALL execute one at a time, in the order of their `POST`; a `POST`
during a run SHALL be queued (`state: queued`, `position ≥ 1`), never
refused. `/chat` SHALL answer `409` while a run is generating.

#### Scenario: Second POST during a run
- **WHEN** a client POSTs `/generate` while a run is generating
- **THEN** the server answers `202 {state: queued, position: 1}` and the run starts when the first ends

### Requirement: Artifacts per run, read from disk

`GET /runs/<id>/chapter` SHALL serve the run's `chapitre.md` as
`text/markdown`, `GET /runs/<id>/audio` its `chapitre.wav` as `audio/wav`,
`GET /runs/<id>/prompts` its `prompts.md`, `GET /runs/<id>/manifest` its
manifest; while a file is absent or empty the route SHALL answer `204`.
`GET /runs` SHALL list runs newest first; `latest` SHALL alias the newest
run. The server SHALL hold no chapter in memory.

#### Scenario: TTS failed
- **WHEN** the chapter was written but the voice rendering raised
- **THEN** `/runs/<id>/chapter` is `200`, `/runs/<id>/audio` is `204`, status is `ready`, and the manifest records `audio: null`

### Requirement: Identifiers are whitelisted

A run id in a path SHALL match `^\d{8}-\d{6}-ch\d{2}-[a-z0-9-]{1,40}$` (or be
`latest`) before any file access; otherwise `400`. An unknown run SHALL
answer `404`. Session path components keep their whitelist.

#### Scenario: Traversal in a run id
- **WHEN** a request path is `/runs/../etc/status`
- **THEN** the server answers `400` before touching the filesystem

### Requirement: Status and events

`GET /runs/<id>/status` SHALL return `{run_id, chapter, seed, phase, ready,
progress, label, detail, elapsed_s, budget_s, gen_toks, notes, state}` with
`state` in `queued | generating | ready | error | cancelled`, from the
progress sink while the run generates and from the manifest afterwards.
`GET /runs/<id>/events` SHALL stream the same payload as server-sent events
about once a second and SHALL close after a terminal state.

#### Scenario: Finished run after a server restart
- **WHEN** a client asks the status of a run that finished before the server started
- **THEN** the payload comes from the manifest, `state: ready`, `ready: true` while `chapitre.md` exists

### Requirement: Failures never reach the client as errors

A preflight refusal, a model failure or any exception in the graph SHALL set
`state: error` with the reason in `error` and in the manifest, SHALL notify
the operator, and SHALL leave the artifact routes at `204`.

#### Scenario: Preflight refuses
- **WHEN** the preflight node raises before any model call
- **THEN** `/runs/<id>/status` reports `state: error` with the reason, `/runs/<id>/chapter` and `/runs/<id>/audio` answer `204`, the operator is notified

### Requirement: Cancellation

`POST /runs/<id>/cancel` SHALL remove a queued run (`state: cancelled`) or
request the stop of the running one at the next node boundary.

#### Scenario: Cancel a queued run
- **WHEN** `POST /runs/<id>/cancel` names a run still in the queue
- **THEN** the run is removed, its manifest says `cancelled`, the running run is untouched

### Requirement: The keynote's routes are gone

`/status`, `/events`, `/chapter`, `/audio`, `/cancel` SHALL answer `410` with
a pointer to the per-run routes.

#### Scenario: Unmigrated client
- **WHEN** a client GETs `/status`
- **THEN** the server answers `410` and names `/runs/<id>/status`

### Requirement: Actor mode

`POST /chat {character, message, session?, nom?}` SHALL answer with the
character's reply, the session key and operator warnings. It SHALL answer
`409` while a run generates, `400` on missing fields, `404` on an unknown
character. `{session, close: true}` SHALL write and index the session.
`GET /characters`, `GET /sessions?character=`, `GET /session/<c>/<ts>` SHALL
list and replay recorded sessions.

#### Scenario: Path components are whitelisted
- **WHEN** a session route carries a component outside `[a-z0-9-]{1,64}` / `[0-9A-Za-z:_-]{1,40}`
- **THEN** the server answers `400` before touching the filesystem

### Requirement: The deck is served from the same origin

Any route not owned by the API SHALL be served from the Slidev build
directory with a fallback to `index.html`, refusing (`403`) any path that
resolves outside that directory; hashed assets are cached long, everything
else revalidated. `GET /health` SHALL report the machine, the active and
queued runs and the available chapters.

#### Scenario: Path traversal on the slides root
- **WHEN** a request path resolves outside the slides directory
- **THEN** the server answers `403`
