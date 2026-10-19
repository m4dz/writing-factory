# pipeline

## ADDED Requirements

### Requirement: Beat context

The run override `beat_context` SHALL select what each beat call is served:
`blind` (default) — its instruction, the prefix and the beat suffix, as in
production; `map` — the whole entry (movement, matter, times with its own
marked, vetos) before its instruction; `plan` — the entry with each time in
its state, computed by the code from the beat order (done: label, do not
resume; current: marked, with its end condition when the brief gives one;
next: label, do not write). The trajectory SHALL NOT be served in any
context. `beats_see_movement=true` SHALL be accepted as `map`; any value
other than `blind`, `map` or `plan` SHALL be refused before the run.

#### Scenario: Default is production
- **WHEN** chapter 7 runs without the override
- **THEN** the served prompts match the ch7 snapshot

#### Scenario: Plan state on the doubt beat
- **WHEN** chapter 7 runs with `beat_context=plan`
- **THEN** the doubt beat's prompt lists times 1 and 2 as done, by label only, and itself as
  current with its end condition, served once

### Requirement: Begun answer in the plan context

In `plan`, the beat's question SHALL carry the text already written before
the beat's instruction, the instruction being the last task read; the
model's answer SHALL be begun with the last paragraph already written
followed by a blank line, and only the new text SHALL be kept. The system
prompt SHALL be folded at the head of the question. The run's `prompts.md`
SHALL record the begun answer apart from the question.

#### Scenario: The doubt continues the discovery
- **WHEN** the doubt beat is drawn with `beat_context=plan`
- **THEN** its answer opens on the discovery's last paragraph and the call records it as the
  begun answer

#### Scenario: System prompt with a begun answer
- **WHEN** a call has a begun answer
- **THEN** no system message is sent and the question opens on the French guard and the voice

### Requirement: Progress gate

When `beat_context` is not `blind`, a beat variant sharing two or more
sentences with the text of its entry (the served quotation excepted) SHALL
carry the veto defect « recopie ». In `plan`, a variant of fewer than two
sentences SHALL carry « vide ou trop court », and a variant with no
first-person mark and two or more « elle » SHALL carry « troisième
personne ». When the retained variant of a beat carries a defect, the run
SHALL record that no variant was clean.

#### Scenario: A recopied doubt
- **WHEN** a doubt variant repeats four sentences of the discovery
- **THEN** it carries « recopie » and loses to a variant that continues

#### Scenario: An empty beat
- **WHEN** a plan beat variant comes back empty
- **THEN** it carries « vide ou trop court » and loses to a written variant

#### Scenario: The instruction transposed
- **WHEN** a plan beat variant is written with « elle » and no « je »
- **THEN** it carries « troisième personne »; a variant where « elle » is the line, next to a
  « je », does not

#### Scenario: Production selection
- **WHEN** `beat_context` is `blind`
- **THEN** none of these checks applies
