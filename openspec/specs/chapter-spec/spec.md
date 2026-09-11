# chapter-spec

## Purpose

Current behaviour: how a chapter's structure reaches the pipeline. Today
chapter 7 is Python (`factory.chapter_spec.chapter7`) reading the briefs in
`chapters/07-anniversaire/`; chapter 2 is constants in `factory.tooling.stage_runner`.
Revamp step 5 replaces both with `chapters/NN-slug/spec.yaml` and a loader.

## Requirements

### Requirement: The brief is read, never copied

The machine brief served to the model SHALL be read from the chapter's brief
file (the blockquoted `## 3. Brief machine` section), and a modified brief
SHALL have one truth.

#### Scenario: The brief file changes
- **WHEN** the `## 3. Brief machine` section of the chapter brief is edited
- **THEN** the next generation serves the edited text without any code change

### Requirement: Served material names no bible file

Any brief or prompt fragment served to the model SHALL be stripped of
fabrication notes and asserted free of `*.md` file names, workshop terms
(couperet, squelette, beat, ancre, matériau, brief…) and machinery terms
(L1–L4, lint, grille, pipeline, vétos…).

#### Scenario: A brief cites a deep sheet
- **WHEN** the brief text contains "pré-écrite selon `fiche-romane.md` §1"
- **THEN** the served brief drops the note and the assertion passes

### Requirement: Per-entry structure is data

A chapter SHALL be able to declare, per entry: weekday and number, weather,
word range, sentence cap, anchor quotation (possibly none), gestures on or
off, strategy (single, segments, beats with names, token caps and sentence
caps), best-of-N and its criterion, movement, trajectory, material, served
vetos, form (accumulation, verdict), drift passage with its frontier, imposed
fall. Absent fields SHALL leave the default pipeline behaviour unchanged.

#### Scenario: Two entries the same day
- **WHEN** the entry spec fixes `Samedi 14` on both entries, the first without anchor and gestures
- **THEN** the pipeline produces two entries with that header, anchor and gestures on the second only

### Requirement: The movement line is extracted, never the file

The chapter's movement SHALL be the single row of `bible/profond/
mouvements-chapitres.md` matching the chapter (and entry) number; the file is
deep and is never served.

#### Scenario: Chapter 7 entry 2
- **WHEN** the state is built for chapter 7
- **THEN** the movement served is the table row `7 — entrée 2` alone; rows of chapters 9–11 appear in no served prompt

### Requirement: Assembly parameters belong to the chapter

The chapter SHALL declare how the audio switch is placed (sentence count or
second dated header) and where the audio excerpt ends (word bound or fall
line).

#### Scenario: Chapter 7 assembly
- **WHEN** the chapter declares the switch on the second header and the excerpt ending on the fall
- **THEN** the served chapter has the switch before the second `Samedi 14.` and the audio marker after `Constat : anniversaire.`

### Requirement: The seed is recorded

The state SHALL carry a seed, random by default for live runs, that drives the
drift draw and is written to the run's frontmatter.

#### Scenario: Replaying a run
- **WHEN** a run is invoked with the seed of a previous run's frontmatter
- **THEN** the drift draw picks the same approach
