# eval

## ADDED Requirements

### Requirement: Countable style marks rank, never judge

`factory.eval.style` SHALL compute countable marks of the style contract
(sentence regime with the accumulation exempt, concrete verbs, exact
figures, inventory lines, closing cleavers) and of the genre's furniture
(thriller physiology, named emotions, telling, surprise adverbs, questions,
named mental states, narrated mind, AI tics), blank quotations before
counting, and return a composite score, higher is better. The score SHALL
never be blocking and SHALL never replace the manual grid line.

#### Scenario: The instrument is falsified offline
- **WHEN** the four étalons of the style sheet, the 33 journal files and the drafts read aloud as generic are scored
- **THEN** every étalon outranks every generic draft and the étalons' mean outranks the journal's mean

#### Scenario: A genre paragraph
- **WHEN** a text carries "battre la chamade", "intriguée", a rhetorical question and "alors"
- **THEN** its score is negative and each mark is reported in `features`
