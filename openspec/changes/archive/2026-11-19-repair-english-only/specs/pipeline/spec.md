# pipeline

## ADDED Requirements

### Requirement: The language repair touches only detected English

The repair SHALL be served only the sentences of an entry where the lint
detects English (suspect words or corrupted tokens), one sentence per call,
and SHALL put each answer back in place, every other character of the entry
kept. An answer that is empty or spans paragraphs SHALL be refused and the
sentence kept. An entry without a detected leak SHALL cost no repair call.

#### Scenario: French without English
- **WHEN** an entry carries « J'ai décidé de ne pas allumer les bougies du soir. » and no English
- **THEN** no repair call is made and the entry is returned byte for byte

#### Scenario: One leaking sentence
- **WHEN** one sentence of an entry carries « suddenly the door »
- **THEN** only that sentence is served to the repair and only it changes
