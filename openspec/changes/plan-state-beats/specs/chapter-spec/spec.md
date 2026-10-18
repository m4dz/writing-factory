# chapter-spec

## ADDED Requirements

### Requirement: Beat end condition

A beat of an entry brief's §7 MAY carry a line starting `Finit quand :`; the
loader SHALL read it into the beat's end condition and remove it from the
instruction. Absent, the end condition SHALL be empty.

#### Scenario: Brief without end conditions
- **WHEN** chapter 7 loads with the current brief
- **THEN** every beat's end condition is empty and the instructions are unchanged
