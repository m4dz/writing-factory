# chapter-spec

## MODIFIED Requirements

### Requirement: Per-entry structure is data

An entry SHALL be able to declare weekday and number, weather, word range,
sentence cap, anchor quotation (possibly none), gestures on or off, strategy
(`single`, `segments`, `beats` with names, token caps, sentence caps and an
optional author ATTACK per beat), best-of with its criterion name and lexical
lists, movement, trajectory, material, served vetos, form (accumulation,
verdict), drift passage with its frontier, imposed fall. A beat's attack
SHALL come from the spec literal or from the `> ` blockquote under the beat's
heading in the entry brief, the literal winning, and SHALL be guarded like
served text. Absent fields SHALL leave the default pipeline behaviour
unchanged (`EntrySpec()` is the empty entry).

#### Scenario: Two entries the same day
- **WHEN** the entry specs fix `Samedi 14` on both entries, the first without anchor and gestures
- **THEN** both headers read `Samedi 14. Beau temps.`, the anchor opens the second only, and no gesture call is made for the first

#### Scenario: An attack under a beat heading
- **WHEN** the entry brief's §7 carries `> Je relis la ligne, le crayon levé.` under `### Beat A`
- **THEN** the beat's `attack` is that sentence and its instruction is the plain text only

#### Scenario: An attack naming a bible file
- **WHEN** a spec beat carries `attack: "Voir fiche-romane.md."`
- **THEN** the loader raises `ChapterSpecError`
