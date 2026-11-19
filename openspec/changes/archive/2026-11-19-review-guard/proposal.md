# Proposal: review-guard

## Why

`entry1-notebook-checks` scores entry 1 at selection, before the review.
Measured on the stage machine with M, chapter 7, 4 runs (2026-11-11,
`experiments/runs/20261111-measure-prepared-plan/report.md`): selection holds
on 3 of 4 (first person, two sentences, no quotation), then the review — M,
temperature 0.5, « RÉÉCRIS INTÉGRALEMENT … resserrer » — is served the entry
without its sheet and:

- grows it: two sentences to up to eleven paragraphs, with contradicting
  facts (« Les photos ne sont pas dans le tiroir. Elles sont toujours sur la
  table de nuit. »);
- opens it on a quotation (2 of 4);
- rewrites the header's weather (« Ciel dégagé. », « Ciel blanc. » for
  « Beau temps. »; 2 of 4).

The existing guard (`_acceptable_cut`) only rejects cuts. Nothing checks a
review against the entry's bounds, and the header the code composes is not
the code's any more once reviewed.

## What changes

- **Header.** After the review, the code puts back the header it composed;
  a header the review produced is removed and the change is warned.
- **Bounds.** A review that ADDS a defect the entry did not have before it
  is rejected and the text from before the review is kept, with a warning.
  Defects: more sentences than `sentences_max`, more words than the top of
  `words`, and the notebook's vetoes (`scorers.notebook`: third person;
  quotation for an entry without anchor). The anchor quotation is read out
  before the check: its « je » would hide a body gone to « elle ». A defect
  already present before the review is the writing's and does not reject.
- Owner's choice (2026-11-16): this guard, not skipping the review for
  bounded entries.

## Variable moved

One: the review's output may now be replaced by its input. No served prompt
moves (the guard runs after the call); the repair prompts move only when the
guard fires, never in the fake-model snapshots.

## Measure

Chapter 7 with M, three seeds: count the guard's rejections and header
restorations; entry 1 of `chapitre.md` read by the owner (this closes
`entry1-notebook-checks` task 3).
