# pipeline

## MODIFIED Requirements

### Requirement: Best-of-N by reading criteria

When the entry spec asks for it, the write node SHALL draw N variants and keep
the one with the fewest named defects (resolution, dismissal, restart,
presence, recursion, stated intention, forbidden decor for beats; the named
criterion of `factory.pipeline.scorers` for a whole entry), ties to the first,
recording every variant's metrics. Presence includes perception ("j'ai
entendu", "j'entends"); a dismissal stated as an open hypothesis
("peut-être… sans y penser") is not one; the restart is exempt only in the
first beat of the chapter's first entry.

#### Scenario: A resolving variant
- **WHEN** one of three beat variants says "je me souviens soudain de tout"
- **THEN** it scores lower than a variant holding the doubt and is not retained

#### Scenario: A restart in a later entry
- **WHEN** the first beat of entry 2 says "Je me suis réveillée ce matin"
- **THEN** it is scored as a restart

#### Scenario: A stated intention
- **WHEN** a beat variant says "Je décide de vérifier une dernière fois la cuisine"
- **THEN** it carries the defect "décide" and scores lower than the same variant without it
