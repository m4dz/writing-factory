# pipeline

## MODIFIED Requirements

### Requirement: Three writing strategies, selected per entry

The write node SHALL write one entry per pass with a single call, three
prefixed segments (opening, reconstruction with stations, closing), or
code-capped beats; the strategy comes from the entry spec (`beats`,
`segments`) or the state. Segments and beats SHALL be prefixed with the text
already written, and exact overlaps removed on reattachment. A beat carrying
an author attack SHALL serve the attack as the end of the text already
written, bound the model's addition to the beat's sentence cap minus the
attack's sentences (at least one), remove an echo of the attack at the head
of the model's segment, score the model's text alone, and pose the attack in
front of the retained variant, reported in a warning.

#### Scenario: Movement method
- **WHEN** the entry spec carries a `movement`
- **THEN** the prompt is assembled in the order intention, trajectory, material, vetos, and the assembled prompt is asserted free of workshop and machinery vocabulary

#### Scenario: A beat with an attack
- **WHEN** the first beat of chapter 7 entry 2 carries a one-sentence attack and the cap is 4
- **THEN** the served block ends with the attack, the model's segment is bounded to 3 sentences, and the entry carries the attack once
