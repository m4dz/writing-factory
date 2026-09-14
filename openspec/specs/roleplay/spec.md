# roleplay

## Purpose

Current behaviour of the actor mode (`factory.roleplay.session`). Decision:
ADR-0014.

## Requirements

### Requirement: The character is validated at construction

Creating a session for a character with no indexed sheet SHALL fail
immediately with a `ValueError` (the API maps it to `404`).

#### Scenario: Unknown character
- **WHEN** a session is created for a doc_id with no indexed sheet
- **THEN** `ValueError` is raised before any turn

### Requirement: Two-level memory

A session SHALL keep the last N turns verbatim and fuse older turns into a
rolling summary written by the same model, injected as the start of the
conversation; summaries of earlier sessions SHALL be retrieved by character
at construction and served as memories, apart from the sheet.

#### Scenario: Window overflow
- **WHEN** the turns exceed twice the kept window
- **THEN** the oldest turns are summarised by the model and removed from the verbatim window

### Requirement: Out-of-role is caught by code

A reply carrying an assistant marker SHALL trigger one relaunch citing the
fault; a still-faulty reply SHALL be shown, flagged in the transcript, and
EXCLUDED from the turns and the summary.

#### Scenario: Persistent slip
- **WHEN** both the reply and its relaunch say "je suis un programme informatique"
- **THEN** the reply is returned, the transcript marks it `hors_role`, the turn is removed from memory, a warning is recorded

### Requirement: Sessions are written first, indexed second

Closing a session SHALL fold the remaining turns into the summary, write
`sessions/<character>/<timestamp>.md` with `## Ce qui s'est dit` and
`## Transcription`, then index the summary in the `sessions` collection. A
session too short to remember SHALL not be written.

#### Scenario: Closing
- **WHEN** a session with two turns is closed
- **THEN** the Markdown file exists before the summary appears in the `sessions` collection

### Requirement: Sessions are replayable and editable

A recorded session SHALL be readable back into roles and lines with a
tolerant parser, so that hand-pruned transcripts still replay.

#### Scenario: Pruned transcript
- **WHEN** a line is deleted by hand from `## Transcription`
- **THEN** the replay returns the remaining lines with their roles
