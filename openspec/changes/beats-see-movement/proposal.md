# Proposal: beats-see-movement

## Why

`scaffold-ablation`, owner's blind reading: production (code-capped beats)
accomplished chapter 7 entry 2's movement on no seed of three; the single
call did on two. The owner noted inventions on six of the twelve beat
entries, none on the single-call ones. Each beat is served alone
(`_prompt_beat`), without the movement, the matter or the other times. But
the single call also differs by four other things (no pruning, verdict step
served, no beat veto suffix, no sentence cap), so the reading does not say
which difference counts.

## What changes

- Run override `beats_see_movement` (env `BEATS_MOVEMENT`, default off):
  each beat is served the whole entry as a map — movement, matter, its
  times with its own marked, vetos — then its own instruction. The
  trajectory is not served (« trois arcs »). Off, prompts are unchanged.
- Experiment `20261018-beats-see-movement`: arm B (override on) and arm R
  (production, fresh draws), same three seeds, blind reading.

## Out of scope

Changing `chapters/07-anniversaire/spec.yaml` (owner); merging
`detector-fixes` (the arms share the old selection, as R did).
