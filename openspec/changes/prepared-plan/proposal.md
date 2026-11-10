# Proposal: prepared-plan

> Lands before `storyboard-density` XP B: its `storyboard` node belongs to
> the prep section this change creates. XP A does not need it.

## Why

What the stage must show is the generation. Everything before the first
written word (gathering the material, planning, checking the plan, the
owner's approval) is workshop preparation: it can happen before the event,
at no stage cost, as long as the stage starts from exactly what was approved.

Today that preparation is small for chapter 7 (`plan: entries-of-brief`
short-circuits the plan node, `narrative_state` makes no model call). It
will not stay small: `storyboard-density` XP B puts a planner model (up to
`qwen3-abliterated-14b`, 9 GB), a swap, a plan veto with one re-plan, and an
`error` ending on a second failure in front of the writing. On stage that is
minutes and a risk of losing the run; before the event it is free, and a
failure only means running the prep again.

The LangGraph audit of 2026-10-18 found the graph used as a plain runner:
no checkpointer, no interrupt, no state history. A prep/live split is
exactly what those primitives exist for, and it is the first step of
committing to LangGraph rather than working around it.

## What changes

- **Checkpointer.** Every `factory` run (CLI and API) compiles the graph with
  a SQLite checkpointer stored in its run directory, `thread_id` = run id,
  durability `sync`. Tests, calibration and `tooling/stage_runner.py` keep
  the plain graph.
- **Leader gate.** A `leader` node after `plan`. With `prepare: true` in the
  state it calls `interrupt()` with the plan and its report; otherwise it
  passes through. The prepared run stops there with status `prepared`.
- **Prepare.** `factory prepare --chapter N` runs gather + plan, shows the
  plan, asks the owner to approve. Approval records the prep fingerprint and
  leaves the run `prepared`; refusal leaves it `cancelled`. Amending the
  plan is out of scope: change the brief or the storyboard and prepare again.
- **Resume as a new run.** `factory generate --from <prepared run>` and
  `POST /generate {chapter, prepared}` create a NEW run seeded from the
  prepared state (`update_state(..., as_node="leader")`, then `invoke(None)`).
  The prepared run is never consumed: rehearsals and the stage resume the
  same approved plan. The new run's manifest records `prepared_from`. The
  seed is drawn fresh at every resume: nobody has read the chapter the stage
  generates, not even the drift draw of a rehearsal.
- **The plan on stage.** The prepared run writes `plan.md` (the plan alone);
  each resumed run carries a copy; `GET /runs/<id>/plan` serves it to the
  deck. `prepared: "latest"` lets the deck resume without a baked-in id.
- **Live preflight.** A `live_preflight` node after `leader` runs the
  machine gate (strict, timer) only on a resumed run. The machine that
  matters is the one on stage, not the one on prep day. `preflight` stays
  the first node for every other run.
- **Fingerprint.** The prep records what its state depends on and the
  checkpoint does not hold: code (commit and a hash of uncommitted changes
  under `src/`), the chapter directory, the resolved configuration, the
  Ollama digests of the models it names, the narrative-state chunk in
  Chroma. Resuming recomputes it and refuses on any difference, naming the
  items, the way a preflight refusal does.

## Relation to storyboard-density

- The XP B `storyboard` node and its plan veto sit between `plan` and
  `leader`. A planner failure ends the PREP run, never a stage run.
- XP B can prepare once per planner arm, then resume each prepared run with
  several seeds: the same list rendered N times separates planner variance
  from rendering variance.
- XP A's hand storyboard is prep state loaded from `chapters/`; the live
  section cannot tell A from B.
- The leader gate passes through in XP B runs (an amended list is no longer
  the model's, doctrine 2); the stage prep uses it.

## Doctrines relied on or challenged

- 13 (one variable between two measurements): relied on. Resuming one
  prepared state with several seeds holds the plan fixed while the writing
  varies; today every run re-plans and mixes both.
- 5 (instruments lie): relied on. A checkpoint resumed against changed code,
  configuration or models would report a run that never existed as such;
  the fingerprint refuses it instead of trusting it.
- 12 (every device creates a defect where it touches): the defects this
  change creates are listed in the design with their guard (stale plan,
  preflight run twice or never, checkpoint deserialization, a gate that
  re-executes on resume, disk growth).
- 2 (warmth is composed): touched only through XP B; the leader gate stays
  open in experiment runs so a generated list stays the model's.

## Single variable

None: this change moves no reading variable. A resumed run must serve the
same prompts as an unsplit run with the same state and seed; a snapshot
scenario checks it.

## Non-goals

- Reserve plans or choosing between plans on stage (owner, 2026-10-19: a plan
  validated before the event is not reconsidered live).
- A fallback chapter served when the factory does not respond (separate
  topic).
- Resuming a crashed or slept live run in place. The checkpointer makes it
  possible; wiring and rehearsing it is a later change.
- Reducers for `warnings` / `metrics` / `scenes`, `stream_mode="custom"`
  replacing the progress sink, skip flags turned into conditional edges.
  They are the rest of the LangGraph migration, each its own change.
- Editing the plan at the leader gate.
- The deck itself: it lives in the talk repository and still speaks the
  keynote contract (see design, "Dependency outside this repo"). Its
  migration is a talk-side change that depends on this one.
