# pipeline

## Purpose

Current behaviour of the generation graph (`factory.pipeline.graph`). The
served prompts of three reference scenarios are frozen in `tests/snapshots/`.

## Requirements

### Requirement: Plan under the bible's facts

The plan node SHALL derive invariant facts from the world chunks of the
present characters (QA model), plan dated entries under those facts (author
model), verify the plan by violation questions with code-checked citations and
a severe counter-call, and replan once on a confirmed violation. It SHALL be
short-circuited when the brief is single-entry or imposes its own entries.

#### Scenario: Plan imposed by the brief
- **WHEN** the state carries `plan_impose`
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
- **WHEN** the entry spec carries `mouvement`
- **THEN** the prompt is assembled in the order intention, trajectory, material, vetos, and the assembled prompt is asserted free of workshop and machinery vocabulary

### Requirement: Best-of-N by reading criteria

When the entry spec asks for it, the write node SHALL draw N variants and keep
the one with the fewest named defects (resolution, dismissal, restart,
presence, recursion, forbidden decor), ties to the first, recording every
variant's metrics.

#### Scenario: A resolving variant
- **WHEN** one of three beat variants says "je me souviens soudain de tout"
- **THEN** it scores lower than a variant holding the doubt and is not retained

### Requirement: Bounds and continuation

A generation cut by `num_predict` SHALL be continued once unless brevity is
wanted; a text ending mid-sentence SHALL be trimmed to the last complete
sentence when that removes less than a quarter; an entry with `phrases_max`
SHALL be cut to that many sentences after its prefix, reported.

#### Scenario: Two-sentence entry
- **WHEN** the entry spec sets `phrases_max: 2` and the model writes eight sentences
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
- **WHEN** the entry spec sets `gestes: false`
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

### Requirement: Every call is measured

Every model call SHALL record wall time, generated tokens, throughput, the
client-side context estimate (`ctx_need`) and the truncation alarm
(`ctx_truncated`), tagged with its node.

#### Scenario: Truncated prompt
- **WHEN** Ollama reports having read less than 75 % of the estimated prompt
- **THEN** the call's metrics carry `ctx_truncated: true`
