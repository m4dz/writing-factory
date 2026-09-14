# pipeline

## MODIFIED Requirements

### Requirement: Best-of-N by reading criteria

When the entry spec asks for it, the write node SHALL draw N variants and keep
the one with the fewest named defects (resolution, dismissal, restart,
presence, recursion, forbidden decor for beats; the named criterion of
`factory.pipeline.scorers` for a whole entry); among variants with the same
defect score it SHALL keep the highest style score (`factory.eval.style`),
then the first drawn; it SHALL record every variant's metrics and name the
tie-break in a warning when the style marks, not the defects, chose.

#### Scenario: A resolving variant
- **WHEN** one of three beat variants says "je me souviens soudain de tout"
- **THEN** it scores lower than a variant holding the doubt and is not retained whatever its style score

#### Scenario: Two clean variants
- **WHEN** two beat variants carry no named defect and one reads in the genre's register
- **THEN** the drier one is retained and the warning names the tie-break with both style scores
