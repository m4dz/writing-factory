# Proposal: style-scorer

## Why

Best-of-N selects by defect count only (ADR-0020): among three acceptable
draws it keeps the first, and it cannot prefer the denser, drier one. The
retained chapter-7 draw of 2026-08-27 passed every counter and reads as
genre French ("battre la chamade", "les jambes flageolantes", "alors" ×6).
The quality campaign (`docs/plans/2026-09-quality-campaign.md`, lever 4)
needs an instrument that ranks register among acceptable variants and that
is falsified offline before it serves.

## What changes

- `factory.eval.style`: countable marks of the style contract (sentence
  regime with the accumulation exempt, concrete verbs, exact figures,
  inventory lines, closing cleavers) and of the genre's furniture (thriller
  physiology, named emotions, telling the strange, surprise adverbs,
  rhetorical questions, named mental states, the narrated mind, AI tics),
  a composite `score(text)` and `features(text)`; `factory eval style
  <files>` prints them.
- Both best-of selections (beats, whole entry) sort on the defect score
  first, the style score second, the draw index third. A warning names the
  tie-break when the marks, not the defects, chose.
- Falsification in `tests/unit/test_style_score.py`: every étalon of the
  style sheet outranks the drafts read aloud as generic (the 2026-08-27
  retained draw, the inner novel, the eight-header chapter, stage A draw 1),
  the étalons' mean outranks the journal's mean, a genre paragraph scores
  below a dry one, the conforming fixtures score high, and the tie-break
  never overrides a defect score.

## Doctrines relied on

- 3 (counting is not reading): the scorer is a selector among draws that
  already passed the vetoes; the judge remains the manual grid line.
- 4 (falsify both ways): the ranking test is the instrument's proof, run on
  the 33 journal files and the four étalons with no model.
- 12: the defect it creates is over-fitting to the étalons; kept behind the
  defect score and never blocking.

## Variable moved

None in served prompts. The selection among equal-defect variants may change:
the three snapshots are unchanged because their fixture variants are
identical texts.

## Non-goals

- Grading prose or replacing the reading aloud.
- Making the style score blocking anywhere.
