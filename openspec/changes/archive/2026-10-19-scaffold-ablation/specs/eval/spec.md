# eval

## ADDED Requirements

### Requirement: Pre-selection variants are kept

A run that draws best-of-N variants SHALL write `variants.md` in its directory:
every variant, its score, the defects named and the winner.

#### Scenario: Best-of-3 on a beat

- **WHEN** a beat is drawn three times
- **THEN** `variants.md` holds three variants for that beat, one marked as the winner

### Requirement: Ablation table

`factory eval ablation RUN...` SHALL count the reading-check defects per run
on the final entry and on the pre-selection variants, group runs by arm from
the experiment manifest, and print both clocks. With `--blind` it SHALL write
the entries in a shuffled order under neutral ids, the key kept apart.

#### Scenario: Blind set

- **WHEN** `factory eval ablation --blind` runs over 15 runs
- **THEN** 15 entries are written under neutral ids and the arm of each is recorded only in the key file
