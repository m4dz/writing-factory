# api

## Purpose

Current behaviour of the HTTP surface (`factory.api.server`), as frozen for
the keynote deck. ADR-0005 replaces it at revamp step 6 (mandatory payload,
artifacts per run); this spec is rewritten then.

## Requirements

### Requirement: Generation is a single idempotent job

`POST /generate` SHALL start the chapter-7 generation if no job is running and
SHALL answer `202` in every case, with `started` telling whether this call
started it. The body is ignored. One job runs at a time.

#### Scenario: Second POST during a run
- **WHEN** a client POSTs `/generate` while a job is generating, rendering or ready
- **THEN** the server answers `202 {started: false}` and nothing is relaunched

### Requirement: Artifacts are read from disk and absent means 204

`GET /chapter` SHALL serve `output/chapitre.md` as `text/markdown` and
`GET /audio` SHALL serve `output/chapitre.wav` as `audio/wav`; while a file is
absent or empty the route SHALL answer `204`, never `404` or `5xx`.

#### Scenario: TTS failed
- **WHEN** the chapter was written but the voice rendering raised
- **THEN** `/chapter` is `200`, `/audio` is `204`, status is `ready`, and a note says the reading is unavailable

### Requirement: The served chapter carries both stage markers

The served chapter SHALL contain `<!-- BASCULE -->` and `<!-- FIN AUDIO -->`,
in that order, whatever the generated text.

#### Scenario: Chapter 7
- **WHEN** chapter 7 is assembled
- **THEN** the switch marker precedes the second dated header and the audio excerpt ends on the fall line

### Requirement: Status and events

`GET /status` SHALL return `{phase, ready, progress, label, detail, elapsed_s,
budget_s, gen_toks, notes}` with `phase` in `generating | tts | ready | error |
idle`. `GET /events` SHALL stream the same payload as server-sent events about
once a second and SHALL close after a terminal state.

#### Scenario: Idle server
- **WHEN** a client opens `/events` with no job running
- **THEN** one event with `state: idle` is sent and the stream closes

### Requirement: Failures never reach the client as errors

A preflight refusal, a model failure or any exception in the graph SHALL set
`phase: error` with the reason in `error`, SHALL notify the operator, and
SHALL leave the artifact routes at `204`.

#### Scenario: Preflight refuses
- **WHEN** the preflight raises before the graph starts
- **THEN** `/status` reports `phase: error` with the reason, `/chapter` and `/audio` answer `204`, the operator is notified

### Requirement: Cancellation

`POST /cancel` SHALL request the stop of a running job; the stop takes effect
at the next node boundary and returns the server to `idle`.

#### Scenario: Cancel during writing
- **WHEN** `POST /cancel` arrives while an entry is being written
- **THEN** the job stops at the next node boundary, `/status` returns to `idle`, and the operator is notified

### Requirement: Actor mode

`POST /chat {character, message, session?, nom?}` SHALL answer with the
character's reply, the session key and operator warnings. It SHALL answer
`409` while a generation runs, `400` on missing fields, `404` on an unknown
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
else revalidated.

#### Scenario: Path traversal on the slides root
- **WHEN** a request path resolves outside the slides directory
- **THEN** the server answers `403`
