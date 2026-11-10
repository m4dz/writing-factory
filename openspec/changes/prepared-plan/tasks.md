# Tasks: prepared-plan

## 0. Owner

- [ ] Go on the scope (proposal, non-goals).
- [x] Stage seed: fresh at every resume (2026-10-19).
- [x] The deck shows the plan, fetched from the API (2026-10-19).

## 1. Plumbing

- [ ] Add `langgraph-checkpoint-sqlite` to the `pipeline` and `test`
      extras; `make venv`.
- [ ] Verify against the installed versions: `SqliteSaver` import path,
      `allowed_msgpack_modules` signature, `durability` argument,
      `update_state(..., as_node=)` on a finished thread.
- [ ] `build_graph(checkpointer=None)`; `None` keeps today's graph.
- [ ] Restricted serializer; round-trip test on the chapter-7 state.
- [ ] `factory.runs`: open the per-run saver, run config with `thread_id`.
- [ ] `make check` green, three snapshots byte-identical.

## 2. Gate and split

- [ ] `leader_node` (interrupt only with `prepare`), `route_after_leader`.
- [ ] `live_preflight_node` (acts only with `prepared_from`).
- [ ] State fields: `prepare`, `prepared_from`, `leader`.
- [ ] Tests: unsplit run unchanged; prepared thread has no `write` call;
      refusal → `cancelled`; no second probe on an unsplit run.

## 3. Fingerprint

- [ ] `factory.runs.fingerprint(run, state)` and `FingerprintError`.
- [ ] Falsified both ways: unchanged passes; changed config key, edited
      chapter file, differing digest (fake `/api/tags`), missing chunk each
      refuse and name the item.

## 4. Commands

- [ ] `factory prepare --chapter N [--seed] [--override]`: run, show the
      plan, ask, write `plan.md`, fingerprint, status.
- [ ] `factory generate --from <id> [--seed]`: checks, new run,
      `update_state(as_node="leader")`, `invoke(None)`.
- [ ] Snapshot scenario `ch7-prepared` (fake model): prompts equal `ch7`'s.
- [ ] Two resumes of one prepared run: two runs, prepared run unchanged.

## 5. API

- [ ] `POST /generate` accepts `prepared` (id or `latest`); `400` cases
      tested; seed random unless given.
- [ ] `state: prepared` in listings and status.
- [ ] `plan.md` (plan alone) and `plan-report.md`; copy into resumed runs;
      `GET /runs/<id>/plan` (`200` prepared and resumed, `204` otherwise).
- [ ] Fingerprint refusal → `state: error`, operator notified.

## 5b. Talk repository (separate change, depends on this one)

- [ ] Owner: open a talk-side change migrating `genClient.ts` to the
      run-based contract (`POST /generate {chapter, prepared: "latest"}`,
      `/runs/<id>/status|events|chapter|audio|plan`) and showing the plan.

## 6. Measure and document

- [ ] One real chapter-7 prep + resume on the stage machine: time saved,
      `checkpoints.sqlite` size, served prompts equal to an unsplit run's.
- [ ] ADR: prep/live split, resume as a new run, fingerprint.
- [ ] `docs/architecture.md` (graph, sections), `docs/runbook.md`
      (prepare the day before; resume on stage; what a refusal means).
- [ ] `storyboard-density` design: place the `storyboard` node between
      `plan` and `leader` (owner's go on that edit).
