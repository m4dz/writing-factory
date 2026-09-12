# pipeline

## Purpose

Current behaviour of the generation graph (`factory.pipeline.graph`). The
served prompts of three reference scenarios are frozen in `tests/snapshots/`.

## Requirements

### Requirement: Preflight is the first node

The graph SHALL open with a `preflight` node that runs the machine gate when
the state field `preflight` asks for it (`true`, or `{strict, timer}`), notes
its warnings for the operator and returns them in `preflight_warnings`; a
refusal SHALL raise `PreflightError` out of `graph.invoke` before any model
call. Absent or false, the node does nothing.

#### Scenario: Calibration and tests never probe the machine
- **WHEN** the state carries no `preflight` field
- **THEN** no probe runs and the plan node is the first to act

### Requirement: The narrative state is generated second

The graph SHALL carry a `narrative_state` node after preflight that, when the
state field `narrative_state` is true, derives the state of the chapter being
written from the author's pilot table (row N-1, perceived side only), writes
`bible/generated/narrative-state/ch-NN.md`, indexes it as
`{doc_id}::etat_narratif_courant::chNN` with the metadata `chapter: N`, and
returns `narrative_state_path`; a chapter beyond the table SHALL note it and
continue with the sheet alone. Idempotent: an unchanged state is not rewritten.

#### Scenario: Chapter 7 through the API
- **WHEN** a run of chapter 7 starts
- **THEN** `ch-07.md` exists, its chunk is in the author collection, and the writing prompt serves it instead of the sheet's section 7

### Requirement: Plan under the bible's facts

The plan node SHALL derive invariant facts from the world chunks of the
present characters (QA model), plan dated entries under those facts (author
model), verify the plan by violation questions with code-checked citations and
a severe counter-call, and replan once on a confirmed violation. It SHALL be
short-circuited when the brief is single-entry or imposes its own entries.

#### Scenario: Plan imposed by the brief
- **WHEN** the state carries `imposed_plan`
- **THEN** no model is called for the plan and the report says so

### Requirement: Headers and anchors are composed by code

Each entry SHALL start with a header of the form `Jour N. Météo.` composed by
code from a weekday and number anchor, dates consecutive unless the entry
spec fixes them, and with the anchor quotation concatenated after it when the
brief gives one. Any dated header or suspension mark produced by the model
SHALL be removed and reported.

#### Scenario: Model re-emits a header
- **WHEN** the model output starts with `Samedi 14, beau temps.`
- **THEN** the parasitic header is removed, the composed one stands, and a warning names the removal

### Requirement: Three writing strategies, selected per entry

The write node SHALL write one entry per pass with a single call, three
prefixed segments (opening, reconstruction with stations, closing), or
code-capped beats; the strategy comes from the entry spec (`beats`,
`segments`) or the state. Segments and beats SHALL be prefixed with the text
already written, and exact overlaps removed on reattachment.

#### Scenario: Movement method
- **WHEN** the entry spec carries a `movement`
- **THEN** the prompt is assembled in the order intention, trajectory, material, vetos, and the assembled prompt is asserted free of workshop and machinery vocabulary

### Requirement: Best-of-N by reading criteria

When the entry spec asks for it, the write node SHALL draw N variants and keep
the one with the fewest named defects (resolution, dismissal, restart,
presence, recursion, forbidden decor for beats; the named criterion of
`factory.pipeline.scorers` for a whole entry), ties to the first, recording
every variant's metrics.

#### Scenario: A resolving variant
- **WHEN** one of three beat variants says "je me souviens soudain de tout"
- **THEN** it scores lower than a variant holding the doubt and is not retained

### Requirement: Bounds and continuation

A generation cut by `num_predict` SHALL be continued once unless brevity is
wanted; a text ending mid-sentence SHALL be trimmed to the last complete
sentence when that removes less than a quarter; an entry with `sentences_max`
SHALL be cut to that many sentences after its prefix, reported.

#### Scenario: Two-sentence entry
- **WHEN** the entry spec sets `sentences_max: 2` and the model writes eight sentences
- **THEN** the entry is cut after the second sentence past the prefix and a warning quotes what was removed

### Requirement: Gestures are validated and posed by code, last

The accumulation SHALL be produced by the model on a form instruction and
validated by code (thresholds, single sentence, French, first person, under
20 % abstract items, no forbidden decor, not the reference); the drift SHALL
be taken from the chapter bank or the brief and validated; both SHALL be set
aside and inserted on the final text after review and repair, with header,
anchor and imposed fall re-stamped, and repeated paragraphs removed while
protecting composed ones.

#### Scenario: Entry without gestures
- **WHEN** the entry spec sets `gestures: false`
- **THEN** no accumulation call is made and an empty gesture set keeps indices aligned

### Requirement: Review and repair cannot destroy an entry

A rewrite SHALL be rejected if it moves the entry away from its word target
below 60 % of the original; a cut that lands in or approaches the target is
accepted whatever its depth. Repair SHALL run on the QA model after the author
model is unloaded.

#### Scenario: Deep cut towards the target
- **WHEN** review shortens an entry from 1033 to 495 words with a 450–600 target
- **THEN** the rewrite is accepted and the depth is noted

### Requirement: Coherence by facts

The coherence node SHALL check the facts derived at plan time, scene by
scene, with violation questions; a fact is contradicted only with a citation
found in the scene and confirmed by the counter-call.

#### Scenario: Citation not in the scene
- **WHEN** the QA model answers YES with a quotation absent from the scene
- **THEN** the finding is listed as to be checked by hand, not as a contradiction

### Requirement: Render is the last node

The graph SHALL close with a `render` node that assembles the chapter Markdown
with both stage markers into `chapter_md` from the state field `assembly`,
always; when the state field `render` is true it SHALL write `chapitre.md`
into `artifacts_dir` (the run directory; `output/` without a run), unload the
QA model and render `chapitre.wav` next to it, returning the voice metrics in
`audio`. A voice failure SHALL leave the
chapter on disk, set `audio` to None and note it for the operator.

#### Scenario: Voice unavailable
- **WHEN** `render` is true and the synthesizer raises
- **THEN** `chapitre.md` is written, `audio` is None, and a note says the reading is unavailable

### Requirement: Every call is measured

Every model call SHALL record wall time, generated tokens, throughput, the
client-side context estimate (`ctx_need`) and the truncation alarm
(`ctx_truncated`), tagged with its node.

#### Scenario: Truncated prompt
- **WHEN** Ollama reports having read less than 75 % of the estimated prompt
- **THEN** the call's metrics carry `ctx_truncated: true`
