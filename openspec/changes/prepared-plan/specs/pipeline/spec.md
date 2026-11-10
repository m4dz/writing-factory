# pipeline

## MODIFIED Requirements

### Requirement: Preflight is the first node

The graph SHALL open with a `preflight` node that runs the machine gate when
the state field `preflight` asks for it (`true`, or `{strict, timer}`), notes
its warnings for the operator and returns them in `preflight_warnings`; a
refusal SHALL raise `PreflightError` out of `graph.invoke` before any model
call. Absent or false, the node does nothing. A run resumed from a prepared
plan SHALL pass the same gate again, strict and timed, in a
`live_preflight` node after `leader`; on any other run `live_preflight`
does nothing.

#### Scenario: Calibration and tests never probe the machine
- **WHEN** the state carries no `preflight` field
- **THEN** no probe runs and the plan node is the first to act

#### Scenario: The stage machine is checked, not the prep machine
- **WHEN** a prepared plan is resumed
- **THEN** `live_preflight` runs the strict, timed gate before the first `write` call, whatever gate the prep ran

#### Scenario: No second probe on an unsplit run
- **WHEN** a run that was not prepared reaches `live_preflight`
- **THEN** the node returns without probing

## ADDED Requirements

### Requirement: Leader gate

The graph SHALL carry a `leader` node after `plan` (after `storyboard`
once it exists). With `prepare: true` in the state it SHALL call
`interrupt()` with the plan and its report, store the resume value in
`leader`, and the graph SHALL end there; otherwise it SHALL pass through
to `live_preflight`. The node SHALL make no model call.

#### Scenario: Unsplit runs are unchanged
- **WHEN** chapter 7 runs without `prepare`
- **THEN** the served prompts match the ch7 snapshot

#### Scenario: A prepared thread stops at the gate
- **WHEN** chapter 7 runs with `prepare: true` and the owner approves
- **THEN** the run records no `write` call and its final state holds the plan and the decision

### Requirement: Runs are checkpointed

Every run started by `factory generate`, `factory prepare` or the API SHALL
be compiled with a SQLite checkpointer at `<run dir>/checkpoints.sqlite`,
`thread_id` equal to the run id, durability `sync`, and a serializer that
deserializes only the project's chapter-spec types and never falls back to
pickle. Graphs built for tests, calibration and `stage_runner` SHALL carry
no checkpointer.

#### Scenario: Chapter state round-trip
- **WHEN** a chapter-7 state with its entry specs is checkpointed and read back
- **THEN** the values are equal and no unrestricted type is loaded

### Requirement: Resume a prepared plan as a new run

Resuming a prepared run SHALL create a new run whose graph starts from the
prepared final state as if `leader` had just run, with `prepare` false,
and SHALL record `prepared_from` in its manifest. The prepared run SHALL
stay `prepared`. The seed SHALL be drawn fresh unless the resume gives one;
the manifest SHALL record the prepared seed and the run's seed. The
resumed run SHALL carry a copy of the prepared `plan.md`.

#### Scenario: Prepared then resumed equals unsplit
- **WHEN** chapter 7 is prepared, approved and resumed with the same seed (fake model)
- **THEN** the served prompts equal the ch7 snapshot's, byte for byte

#### Scenario: The stage draws its own seed
- **WHEN** a prepared plan is resumed without a seed
- **THEN** the run's seed is newly drawn and the manifest records it next to the prepared seed

#### Scenario: Two rehearsals from one plan
- **WHEN** one prepared run is resumed twice
- **THEN** two runs exist, each with `prepared_from` naming it, and the prepared run is still `prepared`

### Requirement: Prepared state fingerprint

Approving a prepared plan SHALL record a fingerprint of what the state
depends on and the checkpoint does not hold: commit, a hash of uncommitted
changes under `src/`, a hash of the chapter directory, the resolved
configuration, the Ollama digests of the models it names, and the presence
of the narrative-state chunk. A resume SHALL recompute it and refuse on any
difference, naming each differing item, before any node runs.

#### Scenario: A rehearsal-day edit
- **WHEN** a chapter file changed after the plan was approved
- **THEN** the resume is refused and the refusal names the chapter hash

#### Scenario: Nothing changed
- **WHEN** a prepared plan is resumed with code, chapter, config, models and index unchanged
- **THEN** the fingerprint passes and the run starts at `live_preflight`
