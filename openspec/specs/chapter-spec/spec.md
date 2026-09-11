# chapter-spec

## Purpose

How a chapter's structure reaches the pipeline: one `chapters/NN-slug/spec.yaml`
per chapter, loaded by `factory.chapter_spec.load_chapter` into a typed
`ChapterSpec`, next to the owner's brief files it points at. No chapter number
appears in pipeline code (ADR-0002).

## Requirements

### Requirement: One spec file per chapter

A chapter SHALL be described by `chapters/NN-slug/spec.yaml` (number, slug,
narrator, brief, calendar, verdict, active objects, prefix, stations,
accumulation fall, drift bank, assembly, defaults, entry count, entries).
`load_chapter(N)` SHALL return its `ChapterSpec`; a chapter without a spec
SHALL raise `ChapterSpecError` and `factory generate --chapter N` SHALL say
so without calling a model.

#### Scenario: Chapter without spec
- **WHEN** `factory generate --chapter 3` runs and no `chapters/03-*/spec.yaml` exists
- **THEN** the command prints the expected path and exits with code 1

### Requirement: The brief is read, never copied

The served brief SHALL be either a literal in the spec or, by pointer
(`brief: {file, section}`), the blockquote of that section of the chapter's
brief file, with fabrication notes stripped; `plan: entries-of-brief` SHALL cut
one imposed beat per entry on the brief's own `**Entrée N` headings. An entry
`source:` SHALL read trajectory, material, beat instructions and the drift
passage from the entry brief's sections; literal fields in the spec win.

#### Scenario: The brief file changes
- **WHEN** the `## 3. Brief machine` section of `chapters/07-anniversaire/brief.md` is edited
- **THEN** the next generation serves the edited text without any code change

### Requirement: Served material names no bible file

Every served text the loader assembles SHALL be asserted free of `*.md` file
names; a literal brief SHALL be asserted free of workshop and machinery
vocabulary; workshop vocabulary in the owner's brief file SHALL be reported
(`spec.workshop_terms`), never rewritten.

#### Scenario: A brief cites a deep sheet
- **WHEN** the brief text contains "pré-écrite selon `fiche-romane.md` §1"
- **THEN** the served brief drops the note and the assertion passes

### Requirement: Per-entry structure is data

An entry SHALL be able to declare weekday and number, weather, word range,
sentence cap, anchor quotation (possibly none), gestures on or off, strategy
(`single`, `segments`, `beats` with names, token caps and sentence caps),
best-of with its criterion name and lexical lists, movement, trajectory,
material, served vetos, form (accumulation, verdict), drift passage with its
frontier, imposed fall. Absent fields SHALL leave the default pipeline
behaviour unchanged (`EntrySpec()` is the empty entry).

#### Scenario: Two entries the same day
- **WHEN** the entry specs fix `Samedi 14` on both entries, the first without anchor and gestures
- **THEN** the pipeline produces two entries with that header, anchor and gestures on the second only

### Requirement: Chapter knowledge reaches the graph through the state

`spec.state()` SHALL build the `graph.invoke` state, carrying `stations`,
`accumulation_fall`, `drift_bank`, `assembly` and the typed `entry_specs`;
run options (RAG, micro-nodes, segments, a single-entry brief, prefix) SHALL
be keyword overrides, never spec content. The graph SHALL read these fields
and no chapter-keyed constant.

#### Scenario: Calibration stage without RAG
- **WHEN** `factory calibrate --stage A` builds the chapter 2 state with `rag=False`
- **THEN** the served brief, anchor and calendar are the spec's and no Chroma call is made

### Requirement: Best-of criteria are a registry

The criterion of a best-of selection SHALL be named in the spec
(`best_of.criterion`) and resolved in `factory.pipeline.scorers`; its lexical
lists (`names`, `drift`) SHALL travel with the spec. An unknown name SHALL
raise.

#### Scenario: Entry 1 of chapter 7
- **WHEN** a variant names none of `photos, playlist, musique, le plat, anniversaire, couverts`
- **THEN** it scores −3 with the defect named and loses to a variant that names one

### Requirement: The movement line is extracted, never the file

The movement SHALL be the single row of `bible/profond/mouvements-chapitres.md`
matching the chapter (and entry) number, requested by `movement: {entry: N}`
or `movement: table`; the file is deep and is never served.

#### Scenario: Chapter 7 entry 2
- **WHEN** the state is built for chapter 7
- **THEN** the movement served is the table row `7 — entrée 2` alone; rows of chapters 9–11 appear in no served prompt

### Requirement: The drift bank is validated at load

Every approach of `drift_bank.approaches` SHALL pass `approach_valid` when the
spec loads; the drift draw SHALL take the bank from the state, seeded, without
replacement, and a chapter without a bank SHALL draw nothing.

#### Scenario: A bad approach in the bank
- **WHEN** an approach shorter than five words is added to a spec
- **THEN** `load_chapter` raises `ChapterSpecError` naming the approach

### Requirement: Assembly parameters belong to the chapter

The chapter SHALL declare in `assembly` how the audio switch is placed
(sentence count or second dated header) and where the audio excerpt ends
(word bound or fall line); the render node SHALL assemble with them.

#### Scenario: Chapter 7 assembly
- **WHEN** the spec declares `{on_second_header: true, fall: "Constat : anniversaire."}`
- **THEN** the served chapter has the switch before the second `Samedi 14.` and the audio marker after `Constat : anniversaire.`

### Requirement: Chapter material is in no collection

The seal test SHALL collect the distinctive lines of every file under
`chapters/` and assert none appears in the `auteur` or `sessions` collections.

#### Scenario: A brief line indexed by mistake
- **WHEN** a chunk carries a line of `chapters/07-anniversaire/brief.md`
- **THEN** the seal report fails on control 6 naming the count of leaked lines

### Requirement: The seed is recorded

The state SHALL carry a seed, random by default for live runs, that drives the
drift draw and is written to the run's frontmatter.

#### Scenario: Replaying a run
- **WHEN** a run is invoked with the seed of a previous run's frontmatter
- **THEN** the drift draw picks the same approach
