# eval

## Purpose

Current behaviour of the deterministic lint (`factory.eval.lint`), the
grid (`factory.eval.grid`) and the journal archiver
(`factory.eval.journal`). No model is involved (doctrine 3).

## Requirements

### Requirement: The lint decides only what is mechanically decidable

The lint SHALL fill the grid lines that are decidable from text (literal
lists, header format, counts, similarity) with their evidence excerpts, mark
heuristic lines as candidates, and leave the judgement lines empty for the
reader. It SHALL never modify the text.

#### Scenario: A judgement line
- **WHEN** the grid is generated for a run
- **THEN** the line "Le mouvement déclaré est-il accompli ?" is present and empty

### Requirement: Detectors are scoped to the chapter

Material interdicts SHALL be scoped by the first chapter where a term becomes
legitimate; reserved terms SHALL be linted in absence on chapters 1–8; the
chapter-7 quartet SHALL be linted in absence elsewhere; the imposed verdict
SHALL be linted in presence.

#### Scenario: Phone before chapter 5
- **WHEN** a chapter-2 text mentions "mes messages"
- **THEN** the material interdict fires; the same text scored as chapter 5 passes

### Requirement: Two layers of lint

Voice lints (AI tics, named mental states, physiology, drift) SHALL apply
outside quotation marks only; the general prose contract SHALL apply
everywhere, quotations included.

#### Scenario: A tic inside a quotation
- **WHEN** a quoted passage contains an AI tic
- **THEN** the voice lint does not flag it; the prose contract still applies to it

### Requirement: Composed paragraphs are protected

Duplicate detection SHALL skip the dated header, any paragraph carrying the
suspension mark, any fully quoted paragraph, and the fragments the caller
names as composed.

#### Scenario: Drift paragraph
- **WHEN** a paragraph carries the suspension mark
- **THEN** duplicate detection never selects it for removal

### Requirement: The reference is accepted

The lint SHALL pass its own reference excerpts (`--etalons`): no pastiche, no
AI tic, no adverbial incise on them, and exactly one accumulation on the
excerpt that defines it.

#### Scenario: A criterion rejects the reference
- **WHEN** a new detector fires on a reference excerpt
- **THEN** the self-test fails and the detector is not merged

### Requirement: The grid is generated, never transcribed

The session grid SHALL be regenerated from the run files by glob, standard
runs first, then controls, then explorations, with the manual judge line
"Le mouvement déclaré est-il accompli ?" first.

#### Scenario: An extra draw
- **WHEN** a run file is added to the run directory
- **THEN** the regenerated grid includes it without editing the generator

### Requirement: Failed runs are archived unchanged

Any run with at least one automatic failure SHALL be copied verbatim to
`experiments/journal/` with a timestamped name and its grid line as header.

#### Scenario: A run with an automatic failure
- **WHEN** the archiver processes a run directory
- **THEN** each failing run is copied to `experiments/journal/` with a timestamp prefix, its body byte-identical
