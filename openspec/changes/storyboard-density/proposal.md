# Proposal: storyboard-density

## Why

Two observations from the owner's other projects:

- Role-play generation (another project, a large cloud model): a chapter cut
  into beats, each beat served as a list of 10 to 12 concrete actions, gave
  dense, good prose with no tone tuning. The format probably carried as much
  as the model, and the format transfers.
- Image generation (another project): an abliterated model, used to write
  prompts for another model, wrote them without the smoothing an aligned model
  applies.

The journal already says why the first should work here. Doctrine 7: a void
in the served matter always fills. Every ghost, adultery, day out and
recursion came from a gap the model filled with the nearest genre. Today a
beat of entry 2 carries one instruction and a cap of 4 to 5 sentences: an
order of magnitude less matter than 10 to 12 actions. Our previous plans
failed for reasons that do not apply to this format: in S4 the plan was nemo
writing it (slow, poor); in CH7 the uncut plan made nemo write prose instead
of planning.

Hypothesis: **density removes the void.** A beat served as an ordered list of
concrete actions leaves the model no room to invent, so fewer inventions,
with no loss on the owner's reading.

## What changes

Three experiments, in this order, each gated by the previous one:

| XP | Single variable | Arms |
|----|-----------------|------|
| A — hand storyboard | entry 2 beats served as an action list written by the owner, instead of one instruction per beat | R (production, after `scaffold-ablation` decides the scaffolding), S (storyboard) |
| B — generated storyboard | who writes the list | owner (A's list), `mistral-nemo` 12B, `qwen2.5:7b`, `qwen3:8b`, `qwen3-abliterated-8b`, `qwen3-abliterated-14b` |
| C — rendering grain | one call per beat vs one call per action | per-beat, per-action |

A runs only after `scaffold-ablation` concludes: the reference is whatever
scaffolding survives. B runs only if A is not worse than R (if density does
not help when written by hand, no planner will rescue it). C runs on the
winning list of B.

`qwen3:8b` (standard) is the control of `qwen3-abliterated-8b`: same family,
same size. Without it, abliteration and model family are confounded.
`qwen2.5:7b` is the QA model already in the triage (ADR-0008).

Code:

- Spec: a beat may carry `actions:` instead of (not in addition to) its
  instruction, as a pointer `{file, section}` into an owner-owned storyboard
  file in `chapters/NN-slug/`. Caps per beat derive from the list
  (`sentences_max` defaults to the number of actions), so the list and its
  caps move as one variable, declared as such.
- Served form: the actions as a numbered list of facts, headed by one line of
  the common veto. No example line, no workshop vocabulary beyond the brief's
  dose.
- `storyboard` node (XP B only): before `write`, a planner model receives the
  beat's brief text (§7 labels), the trajectory (§2), the material (§3) and
  the vetos, and returns the list. The author model is unloaded during
  planning and reloaded after: one swap per chapter, as for QA (ADR-0008).
- Plan veto: every generated action goes through the existing material
  interdicts and reading checks (names, outing, presence, sound, forbidden
  decor, resolution) before any prose is written. A rejected action triggers
  one re-plan with the defect named; a second failure ends the run as
  `error` with the list kept for the journal.
- Recopy measure: per action, the most similar sentence of the rendered beat
  (the same similarity measure as the movement method's 0.94 → 0). Rendering
  an action is expected; quoting it verbatim is reported.

## Single variable

A: the served form of the entry 2 beats (instruction → action list, caps
derived from the list). B: the author of the list. C: the call grain.

## Doctrines relied on or challenged

- 7 (a void always fills): relied on; this is the hypothesis.
- 1 (the model supplies matter, the code holds the gesture): extended. The
  list holds the gesture at a finer grain; the drift, the fall and the
  quotation stay posed by code.
- 2 (warmth is composed): relied on for A, where the list is the owner's.
  Challenged by B: a generated list is warm matter written by a model.
- 6 (shown is recited): challenged. The actions are served so that they come
  back rendered; the recopy measure says whether they come back quoted.
- 8 (an instruction that describes decisions produces a character who
  describes decisions): every action states a fact or a gesture, never an
  intention. The plan veto counts « elle décide », « elle veut ».
- 12 (every device creates a defect where it touches): the expected new
  defects are a litany (twelve actions of the same kind, as with stations), a
  flat trajectory (a list does not climb, the doubt must), and choppy prose
  (one sentence per action). Each has a measure in the design.
- C5 (`experiments/runs/20260831-xp-resolution-c5/`): the brief's trajectory
  names weakening verdicts. Serving them as actions re-serves verdict
  machinery, which C5 showed causes the resolution. The draft list keeps
  attempted verdicts that fail and ends with none; whether to keep them at
  all is an owner decision before A runs.

## Non-goals

- Running any cloud model. The role-play result is an observation about the
  format; the model used there is out of scope by the local-only invariant.
- Using an abliterated model to write prose (only to plan, in B). A prose arm
  can be proposed later as its own change.
- Chapter 2, entry 1 of chapter 7, the voice.
- Editing `chapters/`: the storyboard file is the owner's. The draft in this
  change folder is a proposal for the owner to correct and move.
