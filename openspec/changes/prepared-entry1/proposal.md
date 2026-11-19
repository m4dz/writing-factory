# Proposal: prepared-entry1

## Why

Entry 1 of chapter 7 is the one the speaker reads with the bare voice. On
stage it is a draw: `entry1-decision` measured that the selection takes the
decision whenever a draft holds it, but that only ~27 % of M's drafts hold
it in their two served sentences (best-of-3 ≈ 61 %, best-of-6 ≈ 85 %). The
remaining risk is not something code can score away. The owner decided
(2026-11-19): entry 1 is written the day before, the owner picks among six
drafts, and the stage writes entry 2 only.

## What changes

- **Spec.** `prepared: true` on an entry (the first, of a chapter of two
  entries or more, with `best_of.n ≥ 2`; the loader refuses anything else).
  Chapter 7 entry 1 carries it.
- **Graph.** After an approved plan, a prep whose first entry is prepared
  goes on: `leader → write → prep_pick → accumulate → drift → review →
  repair → END`. `write` draws the drafts and leaves them in
  `entry_draws`, ranked by the selection, without finishing any.
  `prep_pick` interrupts with the drafts (variant, score, defects, the two
  served sentences), takes the owner's variant number (any other answer:
  the first ranked), finishes the chosen draft exactly as `write` finishes a
  winner (`_finish_entry`, extracted), marks it winner in `variants.md`.
  The thread ends after its repair. A refused plan still ends at the gate,
  with no draw.
- **Resume.** `seed_resumed` sets `frozen` to the number of entries the prep
  wrote. `review` and `repair` keep frozen entries as the prep left them.
  The stage enters `live_preflight → write` at `idx = 1`: entry 2 only.
- **CLI.** `factory prepare` asks a second question after « Approuver ce
  plan ? »: the ranked drafts, « Brouillon retenu ? [1-6, Entrée = 1] ».
  Enter or end of input keeps the first ranked; anything that is not a rank
  is asked again. The pick is recorded in the manifest (`entry_pick`).
- **API.** Unchanged: the API never prepares; `/generate {prepared}` resumes.

## Variable moved

Where entry 1 is written: the day before, the owner's pick, instead of on
stage. No served prompt moves: an unsplit run is unchanged (snapshots `ch7`,
`ch2` byte-equal). A prepared run serves the same calls as `ch7`, in
another order (entry 1's review before entry 2's writing); with the
default pick its chapter is `ch7`'s byte for byte.

## Consequences

- The stage run is shorter by entry 1's six drafts, their cleanup, and
  entry 1's review and repair (measure: task 4).
- The progress bar of the stage run starts « Écriture » at entry 2 of 2 —
  half the band is skipped. Accepted; to read at R1.
- `prompts.md` of a stage run no longer holds entry 1's prompts: they are in
  the prepared run's, with its `variants.md`.
- Supersedes the clause of ADR-0028 « a prepared thread never writes » for
  chapters with a prepared entry (ADR-0030).

## Non-goals

- No amendment of the drafts: the owner picks, never edits. To change
  entry 1, prepare again.
- No prepared entry beyond the first, no prepared chapter.
