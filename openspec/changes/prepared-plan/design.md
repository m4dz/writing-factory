# Design: prepared-plan

## Graph

```
START → preflight → narrative_state → plan → leader ─┬─(prepare)──→ END
                                                     └─(otherwise)→ live_preflight → write → …(unchanged)… → render → END
        └──────────── PREP section ──────────────┘     └──────────── LIVE section ────────────┘
```

- `leader` and `live_preflight` are inserted between `plan` and `write`.
  Both pass through (`return {}`) unless asked, so an unsplit run serves
  the same prompts as today.
- `route_after_leader`: `END` when `prepare` is true, else `live_preflight`.
  A prepared thread FINISHES at the gate; nothing after it can run on it.
- XP B's `storyboard` node (and its plan veto) will be added between `plan`
  and `leader`; this change only reserves the place.

### `leader`

```python
def leader_node(state):
    if not state.get("prepare"):
        return {}
    decision = interrupt({"plan": state["plan"],
                          "plan_report": state["plan_report"]})
    return {"leader": decision}          # {"approved": bool, "by": "owner", "at": iso}
```

The node does nothing else. `interrupt()` re-executes its node from the top
on resume, so the gate must never sit inside a node that calls a model.

### `live_preflight`

Runs `preflight(strict=True, timer=True)` when `prepared_from` is set in
the state, otherwise returns `{}`. On an unsplit run the first `preflight`
already ran; the generation probe (`_probe_generation`, up to 120 s) never
runs twice.

## Persistence

- `langgraph-checkpoint-sqlite` added to the `pipeline` and `test` extras.
- `build_graph(checkpointer=None)`. `None` keeps today's compiled graph:
  tests, calibration, `stage_runner`.
- `factory.runs` opens `SqliteSaver` on `<run dir>/checkpoints.sqlite`;
  config `{"configurable": {"thread_id": run.id}, "recursion_limit": 50}`,
  `durability="sync"`: a checkpoint is on disk before the next node starts.
  One write per node, against minutes of model time.
- Serializer: `JsonPlusSerializer` restricted with `allowed_msgpack_modules`
  to `factory.chapter_spec.model` (the frozen dataclasses in `entry_specs`).
  No pickle fallback. A round-trip test proves the chapter-7 state survives.
- The run directory lives under the runs root, never indexed (firewall
  unchanged). The SQLite file holds the same material `prompts.md` and
  `variants.md` already hold.

### Installed API (verified 2026-11-10)

Checked against `langgraph` 1.2.20, `langgraph-checkpoint` 4.3.1,
`langgraph-checkpoint-sqlite` 3.1.3 (the extras pin `>=3.0`):

- `from langgraph.checkpoint.sqlite import SqliteSaver`;
  `SqliteSaver(conn, *, serde=None)` over a `sqlite3` connection opened
  with `check_same_thread=False` (the API worker runs the graph in its
  thread). A prepared run is read through a `mode=ro` URI connection: the
  resume never writes into the prepared run's file.
- `JsonPlusSerializer(*, pickle_fallback=False, allowed_json_modules=None,
  allowed_msgpack_modules=...)`. **Differs from the design:** the allowlist
  takes `(module, name)` pairs or classes, not a module name. The serializer
  lists the four dataclasses a chapter state holds (`BeatSpec`, `BestOf`,
  `Drift`, `EntrySpec`); a foreign type is blocked and comes back as a plain
  dict, never constructed. Default without an explicit list is permissive
  (warn and allow) unless `LANGGRAPH_STRICT_MSGPACK` is set, hence the
  explicit list.
- **Also not in the design:** msgpack has no tuple; the frozen dataclasses
  came back with lists in their tuple fields, unequal to the loaded spec.
  `BestOf` and `EntrySpec` restore their declared tuples in
  `__post_init__` (the serializer rebuilds dataclasses through their
  constructor), so the round-trip is exact.
- `invoke(input, config, *, durability: "sync" | "async" | "exit" | None)`.
- `interrupt(value, *, response_schema=None)`; `invoke` returns the values
  with `__interrupt__`, `get_state(config).interrupts` holds the payload;
  `Command(resume=...)` re-executes the node from its top.
- `update_state(config, values, as_node=None, task_id=None)` on a fresh
  thread with `as_node="leader"` evaluates `route_after_leader` on the
  given values: `next == ("live_preflight",)`, then `invoke(None, config)`.

## Prepare

```
factory prepare --chapter 7 [--seed S] [--override K=V …]
```

1. Create a run (slug `prep`), manifest `kind: prepared`, status `preparing`.
2. `invoke(state | {"prepare": True, "preflight": {"strict": False, "timer": False}})`
   until the interrupt.
3. Print the plan and its report; ask `Approuver ce plan ? [o/N]`.
4. `invoke(Command(resume={"approved": …}))`: `leader` returns the
   decision into the state and the conditional edge ends the thread.
5. Approved: write `fingerprint` into the manifest, status `prepared`,
   write `plan.md` (the plan alone: the beats, later the storyboard
   actions; this is what the stage shows) and `plan-report.md` (the check
   report, machinery, never shown). Refused: status `cancelled`.

The prepared thread is finished, never resumed in place; its final state
is the approved plan.

## Resume

```
factory generate --from <prepared run id> [--seed S]
POST /generate {"chapter": 7, "prepared": "<prepared run id>" | "latest", "seed"?: S}
```

`latest` names the newest `prepared` run of that chapter: the deck needs no
run id baked in, and a single validated plan exists before the event.

1. Load the prepared run; refuse unless status `prepared` and the chapter
   matches.
2. Recompute the fingerprint; refuse on difference (below).
3. Create a new run; manifest `prepared_from: <id>`, `fingerprint` copied;
   `plan.md` copied into the new run directory, so the deck reads the plan
   from the run it launched.
4. Read `graph.get_state(prep_config).values`; set `prepare: False`,
   `prepared_from`, `artifacts_dir`, the live `preflight` request, `render`,
   and `seed` when given; `update_state(new_config, values, as_node="leader")`.
   `route_after_leader` then reads `prepare: False`.
5. `invoke(None, new_config)`: the next node is `live_preflight`.

The seed is drawn FRESH at every resume (owner, 2026-10-19: the talk's
premise is that nobody has read this chapter; a rehearsal's draw on stage
would bend it). `--seed` / `seed` pins one, for experiments only. The
manifest records `prepared_seed` and `seed`. The seed drives only the drift
draw (`graph.py:1717`); Ollama sampling is not seeded, so even a pinned
seed never reproduced a text, but a fresh one removes the last shared draw.

## Fingerprint

| item | source | why |
|---|---|---|
| `commit` | `git rev-parse HEAD` | node names and logic |
| `dirty` | sha256 of `git diff HEAD -- src/` | a rehearsal-day fix not yet committed |
| `chapter` | sha256 over `chapters/NN-slug/` files | spec, brief, storyboard |
| `config` | `runs.resolved_config(overrides)` | models, beats, bounds |
| `models` | Ollama `/api/tags` digest of author, QA, gesture, probe models | a re-pulled model is another model |
| `narrative_state` | the chunk id is present in Chroma | the prep indexed it; the live run serves it |

Refusal is a `FingerprintError`, handled where `PreflightError` is: CLI exit
code 1 with each differing item; API `state: error` with the reason, the
operator notified, artifact routes `204`.

## Defects this creates, and their guard (doctrine 12)

| defect | guard |
|---|---|
| a plan resumed against changed code, config or models | fingerprint refusal |
| preflight skipped on stage (prep's lenient gate stands in for it) | `live_preflight` on every resumed run, strict + timer |
| preflight run twice on an unsplit run | `live_preflight` acts only with `prepared_from` |
| the gate re-executes on resume | `leader` holds nothing but the interrupt |
| arbitrary code on checkpoint load | `allowed_msgpack_modules`, no pickle |
| the prepared plan consumed by its first resume | resume = new thread via `update_state`, prepared thread untouched |
| a prepared thread that goes on writing after approval | `route_after_leader` ends it; the `ch7-prepared` test asserts no `write` call in the prep run |
| disk growth (state copied at each node, best-of variants inside) | measured on a chapter-7 run, reported in tasks; pruning is a later decision |
| the stage resumes a plan nobody read | `plan.md` in the prepared run; `prepared` only after an explicit yes |

## Acceptance (fake model, snapshots)

- **Snapshots unchanged.** The three existing scenarios pass byte-identical:
  `leader` and `live_preflight` pass through.
- **New scenario `ch7-prepared`.** Fake model: prepare chapter 7, approve,
  resume with the same seed. Its served prompts SHALL equal the `ch7`
  scenario's, byte for byte. This is the single test that the split moves
  nothing.
- **Fingerprint falsified both ways** (doctrine 4): a resume with nothing
  changed passes; one changed config key, one edited chapter file, one
  differing model digest (fake `/api/tags`), one missing chunk each refuse
  and name the item.
- **Gate**: refusing at the leader leaves the run `cancelled` with no
  `write` call recorded.
- **Two resumes of one prepared run** produce two runs, each
  `prepared_from` it; the prepared run stays `prepared`.
- **Round-trip**: the chapter-7 state, `entry_specs` included, survives the
  restricted serializer.
- **API**: `POST /generate` with an unknown, non-prepared or other-chapter
  `prepared` id answers `400` with the reason.

## Implementation notes (2026-11-10)

Where the implementation departs from or adds to the text above, and why.

- **Fingerprint check inside the new run.** The resume creates the new run
  first, then checks the fingerprint as the first act of its execution
  (before any node). A refusal is recorded in that run's manifest
  (`status: error`, the items in `error`), as a preflight refusal is; for
  the API this is what the spec asks (`202`, then `state: error`). Nothing
  of a refused resume is thrown away.
- **`dirty`** hashes `git diff HEAD -- src/factory` plus the untracked files
  under `src/factory` (a rehearsal-day fix may be a new module). `src/`
  as a whole would include `writing_factory.egg-info`, which `pip install
  -e` rewrites without any code change.
- **`chapter`** is recorded file by file (`{path: sha256}`), so the refusal
  names the file that moved (`brief.md`), not only "chapter".
- **`narrative_state`** records a hash of the chunk's document, not its
  mere presence: a regenerated chunk with other content is another served
  prompt. A missing chunk is still reported as "absent de Chroma". Recorded
  only when the prep indexed one (`narrative_state_path`).
- **`models`**: an unreachable Ollama is itself a refusal (item `models`);
  at approval it fails the prep (`error`), since no digest can be recorded.
  The embedding model is not in the list, as in the table above.
- **Prep flags.** `factory prepare` also takes `--no-preflight`,
  `--no-narrative-state`, `--quiet`, `--runs-dir` (tests, a machine without
  Chroma). The run is `preparing` while it runs; `kind: prepared` manifests
  are listed by the registry like `kind: run`.
- **Live gate request.** `live_preflight` runs the run's `preflight`
  request: the API and a plain `generate --from` ask strict and timed;
  `--skip-preflight` / `--no-preflight` lower it on the command line for
  development, as for any `generate`.
- **Prepared run untouched.** It is read through a `mode=ro` SQLite
  connection: its database, `-wal`, manifest and plan files are
  byte-identical after two resumes. SQLite's `-shm` (shared-memory read
  marks) is updated by any reader of a WAL database and is not data; the
  test excludes it.
- **`TERMINAL`** includes `prepared`: a prepared run never moves again, and
  its event stream must close.
- **Atomic manifest writes.** The API tests exposed a race older than this
  change: a status poll reading `manifest.yaml` mid-rewrite saw an empty
  file and answered `404` for a live run. `write_manifest` now writes a
  temporary file and renames it.

## Decisions (owner, 2026-10-19)

1. Stage seed: fresh at every resume; pinned only on demand.
2. The deck shows the plan on stage, fetched from the API
   (`GET /runs/<id>/plan` on the run it launched).

## Dependency outside this repo

The deck (`talk/slides/lib/genClient.ts`, talk `main` at `79598cf`) still
speaks the keynote contract: `POST /generate` without a body, `/status`,
`/events`, `/chapter`, `/audio`. The factory answers `400` to the first and
`410` to the others since ADR-0005. With `VITE_MOCK=0` the deck would
silently arm its embedded fallback chapter at every launch. Migrating the
deck to the run-based contract, plus `prepared: "latest"` and the plan
display, is a change in the talk repository; this change only fixes the
API it will call.
