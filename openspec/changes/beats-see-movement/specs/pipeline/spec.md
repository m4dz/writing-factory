# pipeline

## ADDED Requirements

### Requirement: Beats may see the whole entry

With the run override `beats_see_movement` on, each beat call SHALL be served
the whole entry as a map — the movement, the matter, the list of its times
with its own marked once, the entry's vetos — before its own instruction,
and SHALL NOT be served the trajectory. Off, the beat prompts SHALL be
byte-identical to production.

#### Scenario: Map on the discovery beat
- **WHEN** chapter 7 runs with `beats_see_movement=true`
- **THEN** every beat prompt carries the movement and exactly one time marked, its own

#### Scenario: Off by default
- **WHEN** chapter 7 runs without the override
- **THEN** the served prompts match the ch7 snapshot
