# Proposal: plan-state-beats

Supersedes the first draft `beats-see-movement` (same directory history; its
override and experiment stay, as evidence).

## Why

Two failures, one cause each, both known from coding-agent harnesses:

- **Blind beats invent** (`scaffold-ablation`, owner's blind reading:
  "invents" on 6 of 12 beat entries, 0 of 3 single-call ones). A sub-task
  served without its brief fills what it cannot see.
- **Beats that see the whole entry recopy** (`20261018-beats-see-movement`,
  arm B): the doubt beat rewrote the discovery word for word on 2 runs of 3
  and restarted it on the third; the doubt was written in no B entry. A
  sub-task served the whole plan without its state starts over.

A coding harness solves both the same way: the plan is an object the CODE
owns, each step is served with the plan's state (done / current / next),
the current step carries a completion criterion, and every step is checked
before the next one starts. This change applies that discipline to the
beats, so that `storyboard-density` can reuse it at the action grain.

## What changes

- **Plan state, rendered by code.** With `beat_context: plan`, each beat is
  served: the movement and the matter (as B), then the list of times with
  their state — `déjà écrit, plus haut — ne pas reprendre` (label only),
  `CE TEMPS-CI` (instruction + its end condition), `écrit ensuite — ne pas
  écrire` (label only) — then the prefix and the beat suffix. No trajectory.
- **End condition per beat.** Optional `Finit quand :` line under each beat
  of the brief's §7, owner-written; absent, nothing is rendered.
- **Progress gate.** A beat variant that recopies its prefix (shared
  sentences) or restarts an earlier time scores as a veto defect; the
  best-of redraws around it. If every variant fails, the least bad is kept
  and the run says so (re-plan: note and move on, never loop).
- **One override instead of a flag:** `beat_context` ∈ `blind` (production,
  default), `map` (= the first draft's B; `beats_see_movement=true` stays
  as an alias so that experiment replays), `plan`.
- **Experiment** `20261018-plan-state-beats`: smoke run, then arm P × 3
  seeds against the three unread R runs of `20261018-beats-see-movement`.

## Owner material needed before the runs

End conditions for the three beats of chapter 7 entry 2 (brief §7). Drafts
in `design.md`; the owner writes the canon.

## Out of scope

`chapters/07-anniversaire/spec.yaml`; merging `detector-fixes` (the arms
keep the old selection, as R was drawn); the LangGraph question (separate
session).
