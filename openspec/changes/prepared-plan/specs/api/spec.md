# api

## MODIFIED Requirements

### Requirement: The payload is mandatory and names a chapter

`POST /generate {chapter, seed?, overrides?, prepared?}` SHALL create a run
for a chapter that has a spec and answer `202 {run_id, chapter, seed,
position, state}`. Without a body, with an unknown chapter, a non-integer
seed or an override outside the whitelist it SHALL answer `400` with the
reason (and the list of chapters when relevant). `seed` defaults to random
and is recorded. With `prepared`, the run SHALL resume that prepared run:
the id SHALL pass the run-id whitelist or be `latest` (the newest prepared
run of that chapter), name a run with status `prepared` for the same
chapter, and `overrides` SHALL be refused (the configuration is the
prepared one); otherwise `400` with the reason. `seed` stays random by
default.

#### Scenario: Empty POST
- **WHEN** a client POSTs `/generate` without a body
- **THEN** the server answers `400` naming the expected payload and the available chapters

#### Scenario: Resume a prepared plan
- **WHEN** a client POSTs `/generate {chapter: 7, prepared: <id>}` and `<id>` is a prepared chapter-7 run
- **THEN** the server answers `202` and the new run's manifest records `prepared_from: <id>`

#### Scenario: The deck resumes without an id
- **WHEN** a client POSTs `/generate {chapter: 7, prepared: "latest"}` and two chapter-7 runs are prepared
- **THEN** the newer one is resumed, and with none prepared the server answers `400`

#### Scenario: Not a prepared run
- **WHEN** `prepared` names a run whose status is `ready`
- **THEN** the server answers `400` saying the run is not prepared

## ADDED Requirements

### Requirement: Prepared runs are listed, never generated

A prepared run SHALL appear in `GET /runs` with `state: prepared` and
`ready: false`; its `GET /runs/<id>/status` SHALL come from the manifest.
The API SHALL NOT prepare a run: preparation needs the owner's approval at
the terminal.

#### Scenario: Status of a prepared run
- **WHEN** a client asks the status of a prepared run
- **THEN** the payload says `state: prepared`, `ready: false`, and `/runs/<id>/chapter` answers `204`

### Requirement: The plan is served

`GET /runs/<id>/plan` SHALL serve the run's `plan.md` as `text/markdown`
for a prepared run and for a run resumed from one, as soon as the run
exists; for a run without a plan it SHALL answer `204`. The check report
(`plan-report.md`) SHALL NOT be served by this route.

#### Scenario: The deck shows the plan while the chapter is written
- **WHEN** the deck has just resumed a prepared plan and asks `/runs/<run_id>/plan`
- **THEN** the server answers `200` with the approved plan, while the run's status is `generating`

### Requirement: A fingerprint refusal is a failure, not an error response

When a resumed run's fingerprint differs, the run SHALL end with
`state: error`, the differing items in `error` and in the manifest, the
operator notified, and the artifact routes at `204`, as for a preflight
refusal.

#### Scenario: Model re-pulled since the prep
- **WHEN** the author model's digest differs from the prepared fingerprint
- **THEN** `/runs/<id>/status` reports `state: error` naming the model digest, and no model is called
