# chapter-spec

## ADDED Requirements

### Requirement: Beat end condition

A beat of an entry brief's §7 MAY carry a line starting `Finit quand :`; the
loader SHALL read it into the beat's end condition and remove it from the
instruction. Absent, the end condition SHALL be empty.

#### Scenario: End conditions do not reach production
- **WHEN** chapter 7 loads with `Finit quand :` lines in its brief
- **THEN** each beat carries its end condition, the instructions are unchanged, and the
  production prompts match the ch7 snapshot

#### Scenario: Brief without end conditions
- **WHEN** a brief has no `Finit quand :` line
- **THEN** every beat's end condition is empty
