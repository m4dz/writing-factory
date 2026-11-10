# pipeline

## ADDED Requirements

### Requirement: An entry best-of rejects the notebook's own defects

Every entry drawn as best-of SHALL be scored, on its served bounded text, for
the notebook's defects in addition to its spec criterion: third person (no
first-person mark, and two « elle » or a sentence opening on « Elle ») and,
for an entry without anchor, quotation (a quotation opening the entry, or a
quoted span of five words or more). Each SHALL weigh more than the
criterion's own terms.

#### Scenario: An invented quotation opens entry 1
- **WHEN** entry 1 (no anchor) draws a quoting variant and a clean one
- **THEN** the clean variant is retained and the warnings name the quoting one's defect

#### Scenario: Romane next to the narrator
- **WHEN** a variant writes « Les photos où elle rit, où elle est belle, je les range »
- **THEN** no third-person defect is counted
