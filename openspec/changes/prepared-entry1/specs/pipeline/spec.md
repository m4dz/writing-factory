# pipeline

## ADDED Requirements

### Requirement: A prepared entry is picked the day before

A chapter spec MAY mark its first entry `prepared`, only in a chapter of two
entries or more and with a best-of of at least two drafts; the loader SHALL
refuse any other use. When the owner approves the plan of a prep whose first
entry is prepared, the prep SHALL draw that entry's drafts and SHALL stop
before finishing any, presenting them ranked by the selection. The owner's
answer SHALL choose the draft; an answer that names no draft SHALL keep the
first ranked. The chosen draft SHALL be finished, reviewed and repaired as
the live run would, and the prep SHALL then end, writing no other entry. A
refused plan SHALL draw nothing.

A run resumed from such a prep SHALL keep the prepared entry as the prep
left it — not rewritten, not reviewed, not repaired again — and SHALL write
the remaining entries only.

#### Scenario: The owner picks the third draft

- **WHEN** the owner approves the plan of chapter 7 and answers 3 at the pick
- **THEN** entry 1 of the prepared state is the third ranked draft, finished
  and repaired, and the manifest records the pick

#### Scenario: The stage writes entry 2 only

- **WHEN** the stage resumes that prepared run
- **THEN** no entry-1 draft is drawn, entry 1 is neither reviewed nor
  repaired, and the chapter's entry 1 is the prepared one

#### Scenario: An unsplit run is unchanged

- **WHEN** chapter 7 is generated without `prepare`
- **THEN** its served prompts are byte-equal to the `ch7` snapshot

#### Scenario: A refused plan draws nothing

- **WHEN** the owner refuses the plan of chapter 7
- **THEN** the prep ends at the leader gate with no draft drawn
