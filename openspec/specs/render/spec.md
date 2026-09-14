# render

## Purpose

Current behaviour of chapter assembly (`factory.pipeline.assembly`) and voice
rendering (`factory.infra.tts`). Decisions: ADR-0012, ADR-0013.

## Requirements

### Requirement: Both markers, always

Assembly SHALL insert `<!-- BASCULE -->` after the configured number of
sentences, or before the second dated header when the chapter asks for it,
falling back to the sentence rule then to the head; it SHALL insert
`<!-- FIN AUDIO -->` after the excerpt, at the end of text if no bound can be
computed. The chapter served stays whole.

#### Scenario: One-sentence chapter
- **WHEN** the assembled text has a single sentence
- **THEN** the switch marker is placed at the head and the audio marker at the end

### Requirement: The excerpt is bounded in time and ends on a sentence

The excerpt SHALL be the text after the switch up to the word count derived
from `AUDIO_SECONDS` and the measured rate, cut on a sentence end, or up to
and including the imposed fall line when the chapter names one.

#### Scenario: Fall line beyond the word bound
- **WHEN** the fall line sits past the word budget
- **THEN** the excerpt still ends on the fall line

### Requirement: Rendering is segmented and measured

Rendering SHALL split the excerpt into segments under a character cap without
cutting a sentence, synthesise each with the reference voice in French,
insert a pause between segments, write one WAV, and return audio duration,
compute duration, real-time factor and measured words per minute. A gap above
the tolerance against the target SHALL emit an operator note with the rate to
recalibrate.

#### Scenario: Off-target duration
- **WHEN** the rendered audio differs from the target by more than the tolerance
- **THEN** an operator note gives the measured words per minute to recalibrate

### Requirement: Failure is ordinary

A missing voice reference, missing dependencies or an empty excerpt SHALL
raise an ordinary exception (`TTSIndisponible`), never `SystemExit`; the
caller keeps the chapter and leaves the audio absent.

#### Scenario: Missing voice reference
- **WHEN** the voice WAV or transcript is absent
- **THEN** `TTSIndisponible` is raised and the API keeps the chapter with `/audio` at `204`
