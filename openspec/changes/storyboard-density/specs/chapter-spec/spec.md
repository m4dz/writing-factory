# chapter-spec

## ADDED Requirements

### Requirement: A beat may be served as an action list

A beat MAY carry `actions: {file, section}` pointing at an owner-owned
storyboard file in its chapter directory, instead of its instruction. The
loader SHALL refuse an action naming a bible file, carrying workshop
vocabulary or an intention verb, and a list shorter than 6 or longer than 14.
`sentences_max` SHALL default to the number of actions.

#### Scenario: Intention verb

- **WHEN** an action reads « Elle décide de ranger les photos. »
- **THEN** loading the spec raises `ChapterSpecError` naming the action
