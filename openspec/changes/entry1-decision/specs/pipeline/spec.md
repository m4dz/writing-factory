# pipeline

## ADDED Requirements

### Requirement: Entry 1 keeps its decision

For an entry without anchor, the best-of SHALL remove the quotation marks
(and the emphasis inside them) of an opening line that is the narrator's
own — a first-person mark, no second person, closed on a sentence end —
before scoring, and SHALL serve the unquoted variant, with a warning. Any
other quotation SHALL be scored as today. When the entry's `best_of`
carries a `decision` list, a variant whose served sentences hold none of
its terms SHALL score lower, with the defect named. An entry whose
`form.verdict` is `absent` SHALL score lower when it writes the chapter's
verdict word, and a review that adds that word SHALL be rejected. Every
variant of the entry's best-of SHALL be recorded in `variants.md`.

#### Scenario: The decision in the anchor's dress
- **WHEN** a draw of entry 1 opens on « « J'ai décidé que ce jour n'aurait pas lieu. » » followed by the list
- **THEN** the variant scored and served opens on « J'ai décidé que ce jour n'aurait pas lieu. », without marks

#### Scenario: Somebody else's line
- **WHEN** a draw opens on « "Nous sommes invincibles", disait-elle »
- **THEN** the marks stay and the variant is rejected as a quotation

#### Scenario: The doorstep against the decision
- **WHEN** the decision list is set, one draw opens on a key turned in a lock and a drawer, another on the decision and the erasure list
- **THEN** the second is retained

#### Scenario: The day's word
- **WHEN** entry 1 (verdict absent) writes « anniversaire »
- **THEN** the variant scores lower with « écrit le mot du jour (« anniversaire ») »
