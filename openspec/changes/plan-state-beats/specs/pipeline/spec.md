# pipeline

## ADDED Requirements

### Requirement: Beat context

The run override `beat_context` SHALL select what each beat call is served:
`blind` (default) — its instruction, the prefix and the beat suffix, as in
production; `map` — the whole entry (movement, matter, times with its own
marked, vetos) before its instruction; `plan` — as `map`, with each time
in its state (done: label, do not resume; current: instruction and end
condition; next: label, do not write). The trajectory SHALL NOT be served
in any context. `beats_see_movement=true` SHALL be accepted as `map`.

#### Scenario: Default is production
- **WHEN** chapter 7 runs without the override
- **THEN** the served prompts match the ch7 snapshot

#### Scenario: Plan state on the doubt beat
- **WHEN** chapter 7 runs with `beat_context=plan`
- **THEN** the doubt beat's prompt lists times 1 and 2 as done, by label only, and itself as current

### Requirement: Progress gate

When `beat_context` is not `blind`, a beat variant sharing two or more
sentences with the prefix of its entry (the served quotation excepted) SHALL
carry the veto defect « recopie ». When every variant of a beat carries a
veto defect, the least bad SHALL be kept and the run SHALL record a warning.

#### Scenario: A recopied doubt
- **WHEN** a doubt variant repeats four sentences of the discovery
- **THEN** it carries « recopie » and loses to a variant that continues
