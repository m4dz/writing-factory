# chapter-spec

## ADDED Requirements

### Requirement: One spec file per chapter

A chapter SHALL be described by `chapters/NN-slug/spec.yaml`, loaded by
`load_chapter(N)` into a typed `ChapterSpec`; a chapter without a spec SHALL
raise `ChapterSpecError`.

#### Scenario: Chapter without spec
- **WHEN** `factory generate --chapter 3` runs and no `chapters/03-*/spec.yaml` exists
- **THEN** the command prints the expected path and exits with code 1

### Requirement: Chapter knowledge reaches the graph through the state

`spec.state()` SHALL carry `stations`, `accumulation_fall`, `drift_bank`,
`assembly` and typed `entry_specs`; the graph SHALL read them and no
chapter-keyed constant.

#### Scenario: Calibration stage without RAG
- **WHEN** `factory calibrate --stage A` builds the chapter 2 state with `rag=False`
- **THEN** the served brief, anchor and calendar are the spec's and no Chroma call is made

### Requirement: Best-of criteria are a registry

The criterion SHALL be named in the spec and resolved in
`factory.pipeline.scorers`; its lexical lists SHALL travel with the spec.

#### Scenario: Entry 1 of chapter 7
- **WHEN** a variant names none of the listed erasure terms
- **THEN** it scores −3 with the defect named

### Requirement: The drift bank is validated at load

Every bank approach SHALL pass `approach_valid` when the spec loads.

#### Scenario: A bad approach in the bank
- **WHEN** an approach shorter than five words is added to a spec
- **THEN** `load_chapter` raises `ChapterSpecError` naming the approach

### Requirement: Chapter material is in no collection

The seal test SHALL assert that no distinctive line of `chapters/` appears in
the `auteur` or `sessions` collections.

#### Scenario: A brief line indexed by mistake
- **WHEN** a chunk carries a line of `chapters/07-anniversaire/brief.md`
- **THEN** the seal report fails on control 6

## MODIFIED Requirements

### Requirement: The brief is read, never copied

The served brief SHALL be a literal in the spec or, by pointer, the blockquote
of a section of the chapter's brief file with fabrication notes stripped;
entry text (trajectory, material, beat instructions, drift) SHALL be read
from the entry brief the spec points at; literal fields win.

#### Scenario: The brief file changes
- **WHEN** the `## 3. Brief machine` section of the chapter brief is edited
- **THEN** the next generation serves the edited text without any code change
