# pipeline

## ADDED Requirements

### Requirement: Storyboard planner

When a run names a planner model, a `storyboard` node SHALL generate the
action list of each beat before `write`, with the author model unloaded, and
SHALL pass every action through the material interdicts and reading checks.
A vetoed action SHALL trigger one re-plan with the defect named; a second
failure SHALL end the run in `error` with the list kept.

#### Scenario: A presence in the plan

- **WHEN** the planner returns an action in which someone else is in the house
- **THEN** no prose is written for that beat until a re-plan passes the veto
