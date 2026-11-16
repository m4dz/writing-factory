# pipeline

## ADDED Requirements

### Requirement: The review keeps the entry's header and bounds

After the review call, the code SHALL restore the header it composed for the
entry and SHALL remove any header the review produced. A review that adds a
defect the entry did not have before it SHALL be rejected and the entry
before the review kept, with a warning naming the defect. Defects: more
sentences than the entry's `sentences_max`, more words than the top of its
`words`, third person, and for an entry without anchor a quotation; the
anchor quotation SHALL be removed from the text before the check.

#### Scenario: The review grows entry 1
- **WHEN** the review returns entry 1 (two sentences, no quotation) as several paragraphs opening on a quotation
- **THEN** the entry before the review is kept and the warning names both defects

#### Scenario: The review rewrites the weather
- **WHEN** the review returns « Samedi 14. Ciel blanc. » over an entry headed « Samedi 14. Beau temps. »
- **THEN** the reviewed body is kept under « Samedi 14. Beau temps. » and the restoration is warned

#### Scenario: A defect already there
- **WHEN** the entry before the review already opens on a quotation and the review keeps it
- **THEN** the review is accepted
