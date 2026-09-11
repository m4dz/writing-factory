# Design: safety-net

## The boundary that is frozen

The model boundary is `llm.chat` / `llm.chat_turns`. At step 2 every module
bound the function by name at import (`from llm import chat`), so the fake was
installed in each binding (`graph`, `qa`, `roleplay`, `llm`), plus `unload`;
since step 4 part 2 the functions delegate to one `ollama.client` and the fake
replaces its three methods. The fake
records `(role, system, user, model, num_predict, temperature, reply)` for
every call. The snapshot renders the ordered list of `(system, user)` pairs.

Recognition is by prompt identity for the QA and gesture nodes (their system
prompts are module constants) and by prompt shape for plan, review,
continuation and the write strategies (segment headers, the beat suffix, the
entry instruction). Best-of-N beats are served by call order:
`fx.BEATS[(k // BEATS_N) % 3]`.

## Why crafted text and not recordings

The protected invariant is the prompts served, not the model's answers. Model
answers only need to (a) be deterministic and (b) keep the graph on its nominal
path. Crafted fixtures do both and remove the dependency on the owner's
machine. `tests/unit/test_fixtures.py` runs each fixture through the validator
that will judge it (`valider_accumulation`, `_scorer_beat`,
`_scorer_entree1`, `delint`, `interdits_materiels`, sentence bounds), so a
fixture drifting out of conformance fails there with a name, not inside a
2,000-line snapshot diff.

## Retrieval without Chroma

`indexer/index.py::index_file` is a pure function of a bible file. The fake
client runs it over `bible/` (skipping `_*.md` and `exclu()` paths) and serves
`get(ids=…)`, `get(where=…)`, `query`, `upsert`, `delete`. Embeddings are
never computed: `retrieval.embed` and `roleplay.embed` return zeros. Semantic
retrieval is disabled during writing in the real pipeline, so this loses
nothing the snapshot needs.

## Scenarios

Three, chosen to cover every strategy and both plan paths:

| scenario | plan | write strategy | gestures | coherence |
|---|---|---|---|---|
| `ch7` | imposed by the brief | entry 1 single + best-of-3; entry 2 beats × best-of-3 | entry 2, drift passage from brief, fall by code | facts derived, 2 scenes |
| `ch2-s7-score` | short-circuited (mono) | 3 segments with stations | accumulation + bank drift | 1 scene |
| `ch2-s7-chapter` | plan node, facts, plan check | 3 segments × 3 entries | bank drift × 3 | 3 scenes |

The chapter 2 state reproduces the dict of `outillage/run_s4.py` for stage
S7; the chapter 7 state is `ch7.etat_ch7(graine=SEED)`. Both constructions
are what step 5 replaces with the spec loader.

## Golden files

`prompts.md`, `chapter.md`, `warnings.txt` per scenario; `lint/<file>.txt`
per journal file. `make snapshots` regenerates; a regeneration is a change
that must be named in its openspec proposal.

## Acceptance

- `make check` green on the current code; a second run yields identical
  golden files (determinism).
- Each failing fixture trips its validator (`test_failing_fixtures_do_fail`).
- Every preflight blocking rule fires on its case and is silent on a healthy
  machine.
- The API test starts the real `ThreadingHTTPServer` in-process with the
  graph, preflight, TTS and unload replaced.
