# Design: style-scorer

## Marks

Per 100 words where it is a count; shares where it is a regime. Positive:
`short_share` (3–16 words, cleavers included), `concrete_verbs`, `figures`,
`inventory_lines` (object, colon, state), `closing_cleavers`. Negative:
`long_share` (> 25 words, the accumulation exempt through the lint's own
thresholds), `genre_physiology`, `emotion_nouns`, `telling`, `surprise`,
`questions`, `mental_states` (the lint's pattern), `mental_narration`,
`tics` (the lint's AI tics and pastiche). Positive marks are capped so a
litany of figures cannot buy back a genre body. Quotations (« », “ ”, and
straight quotes of 15+ characters) are blanked: the notebook is the
author's voice.

## Where it sits

`factory.eval.style` imports the lint's lists (ADR-0023: reading knowledge
stays in the eval package). The graph imports it for the tie-break only.

## What the fixtures and snapshots show

The fake model's beat and entry fixtures are identical across variants, so
the tie-break never fires and `tests/snapshots/*` are byte-identical.
`test_tiebreak_reaches_the_beat_selection` feeds a genre variant and two dry
ones: the genre one loses on defects, the two dry ones tie on both counts,
no tie-break note. `test_style_breaks_ties_only_behind_the_defect_score`
shows the sort order and the note's wording.

## The honest limit

A journal run that failed on STRUCTURE (no accumulation, an English leak,
"je décide de") may score well: the module reads register, the lint owns
structure. The test asserts what the instrument claims, not more.
