# pipeline

## ADDED Requirements

### Requirement: Preflight is the first node

The graph SHALL open with a `preflight` node that runs the machine gate when
the state field `preflight` asks for it (`true`, or `{strict, timer}`), notes
its warnings for the operator and returns them in `preflight_warnings`; a
refusal SHALL raise `PreflightError` out of `graph.invoke` before any model
call. Absent or false, the node does nothing.

#### Scenario: Calibration and tests never probe the machine
- **WHEN** the state carries no `preflight` field
- **THEN** no probe runs and the plan node is the first to act

#### Scenario: Stage path
- **WHEN** the API invokes the graph with `preflight: {strict: true, timer: true}` on a machine with a saturated swap
- **THEN** `PreflightError` is raised, no model is called, and the job ends in `error`

### Requirement: Render is the last node

The graph SHALL close with a `render` node that assembles the chapter Markdown
with both stage markers into `chapter_md` from the state field `assembly`,
always; when the state field `render` is true it SHALL write
`output/chapitre.md`, unload the QA model and render `output/chapitre.wav`,
returning the voice metrics in `audio`. A voice failure SHALL leave the
chapter on disk, set `audio` to None and note it for the operator.

#### Scenario: Voice unavailable
- **WHEN** `render` is true and the synthesizer raises
- **THEN** `chapitre.md` is written, `audio` is None, and a note says the reading is unavailable
