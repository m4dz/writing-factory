# ADR-0028 — Prepared plan: a prep/live split, resumed as new runs

Date: 2026-10-19 → 2026-11-10. Status: accepted (implementation; the
real-machine measurement of `prepared-plan` section 6 is open).

## Context

What the stage must show is the generation. Everything before the first
written word (gathering, planning, checking the plan, the owner's approval)
is workshop preparation: it can happen before the event at no stage cost,
as long as the stage starts from exactly what was approved. For chapter 7
that prep is small today (the brief imposes the plan); `storyboard-density`
XP B puts a planner model, a swap, a plan veto and an `error` ending in
front of the writing. On stage that is minutes and a risk of losing the run;
before the event a failure only means preparing again.

The LangGraph audit of 2026-10-18 found the graph used as a plain runner:
no checkpointer, no interrupt, no state history. A prep/live split is what
those primitives are for (openspec change `prepared-plan`).

## Decision

1. **Every run is checkpointed in its directory.** `factory generate`,
   `factory prepare` and the API compile the graph with a SQLite saver on
   `<run dir>/checkpoints.sqlite`, `thread_id` = run id, durability `sync`.
   Tests, calibration and `stage_runner` keep the plain graph
   (`build_graph()` without a checkpointer). The serializer deserializes
   only the four chapter-spec dataclasses a state holds, no pickle
   fallback: loading a checkpoint is never a way to run code.
2. **A leader gate closes the prep section.** `leader` sits after `plan`
   (after the storyboard and its veto once they exist). With `prepare` in
   the state it interrupts with the plan and its report, stores the owner's
   answer, and the conditional edge ends the thread: a prepared thread never
   writes. Otherwise it passes through. The node holds nothing but the
   interrupt, because LangGraph re-executes it on resume.
3. **Approval happens at the terminal, never through the API.** `factory
   prepare` shows the plan; only an explicit yes leaves the run `prepared`,
   with its fingerprint, `plan.md` (the plan alone, what the stage shows)
   and `plan-report.md` (the check, never shown). Anything else leaves it
   `cancelled`. Amending the plan at the gate is out: change the brief and
   prepare again.
4. **Resume is a new run.** `factory generate --from <id|latest>` and
   `POST /generate {chapter, prepared}` create a NEW run with the prepared
   configuration, read the prepared state read-only, seed the new thread
   with `update_state(..., as_node="leader")` and run the live section. The
   prepared run is never consumed: rehearsals and the stage resume the same
   approved plan. The seed is drawn fresh at every resume (owner,
   2026-10-19: nobody has read the chapter the stage generates, not even a
   rehearsal's drift draw); `--seed` pins one for experiments.
5. **The stage machine is checked, not the prep machine.** The prep runs a
   lenient, untimed gate; `live_preflight`, after `leader`, runs the strict,
   timed gate on a resumed run only. An unsplit run probes once.
6. **A fingerprint guards the resume.** The prep records what its state
   depends on and the checkpoint does not hold: commit, uncommitted changes
   under `src/factory`, the chapter directory file by file, the resolved
   configuration, the Ollama digests of the author, QA, gesture and probe
   models, the narrative-state chunk. A resume recomputes it before any
   node and refuses on any difference, naming each item: CLI exit 1, API
   `state: error` with the operator notified, as a preflight refusal.

## Alternatives rejected

- **Resume the prepared thread in place.** One rehearsal would consume the
  plan the stage needs; a second resume would start from a written chapter.
- **Trust the checkpoint.** A plan resumed against re-pulled models or a
  rehearsal-day edit would report a run that never existed as such
  (doctrine 5).
- **Default serializer.** It warns and constructs any class found in the
  file; the permissive default is due to be removed upstream anyway.
- **Reserve plans, choosing between plans on stage** (owner, 2026-10-19): a
  plan validated before the event is not reconsidered live.

## Consequences

- An unsplit run serves the same prompts: `leader` and `live_preflight`
  pass through, the three snapshots are byte-identical, and the scenario
  `ch7-prepared` (prepare, approve, resume with the same seed) equals `ch7`
  byte for byte.
- `GET /runs/<id>/plan` serves the approved plan for a prepared run and for
  every run resumed from it; the deck shows it while the chapter is written.
  The deck itself still speaks the keynote contract: its migration is a
  talk-side change (`prepared-plan` task 5b).
- Two new run states: `preparing` (at the terminal) and `prepared`
  (terminal, never ready). Manifests of prepared runs carry `kind: prepared`,
  `leader` and `fingerprint`; resumed runs carry `prepared_from`,
  `prepared_seed` and a copy of the fingerprint.
- XP B can prepare once per planner arm and resume each prepared run with
  several seeds: planner variance and rendering variance separate
  (doctrine 13).
- Each run directory gains a checkpoint file holding the material
  `prompts.md` and `variants.md` already hold; its size on a real chapter-7
  run is measured in section 6, pruning is a later decision.
- Out of this decision, each its own change: resuming a crashed live run in
  place, reducers for `warnings` / `metrics` / `scenes`,
  `stream_mode="custom"` for the progress sink, skip flags as conditional
  edges.
