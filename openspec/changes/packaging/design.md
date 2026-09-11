# Design: packaging

## Module map (part 1)

| before | after |
|---|---|
| `orchestrator/llm.py` | `factory/infra/ollama.py` |
| `orchestrator/preflight.py`, `notify.py`, `progress.py`, `tts.py` | `factory/infra/…` |
| `orchestrator/style.py` | `factory/text.py` |
| `orchestrator/retrieval.py` | `factory/retrieval/context.py` |
| `indexer/index.py`, `query_test.py` | `factory/retrieval/indexer.py`, `query.py` |
| `orchestrator/graph.py`, `gestes.py`, `chapitre.py`, `qa.py` | `factory/pipeline/graph.py`, `gestures.py`, `assembly.py`, `qa.py` |
| `orchestrator/ch7.py`, `outillage/build_etat_narratif.py` | `factory/chapter_spec/chapter7.py`, `narrative_state.py` |
| `orchestrator/roleplay.py`, `chat_character.py` | `factory/roleplay/session.py`, `cli.py` |
| `orchestrator/api.py`, `static/` | `factory/api/server.py`, `static/` |
| `outillage/lint_style.py`, `grille_session.py`, `etancheite.py`, `journal_des_murs.py`, `*.txt`, `grille-lint.md` | `factory/eval/lint.py`, `grid.py`, `seal.py`, `journal.py`, `data/` |
| `outillage/run_*.py`, `xp_resolution.py`, `build_modelfile.py`, `orchestrator/run_chapter.py` | `factory/tooling/…` |
| `indexer/Dockerfile` | `docker/indexer.Dockerfile` (installs the package) |

Imports: `from X import y` → `from factory.<pkg>.<module> import y`; a bare
`import X` becomes `from factory.<pkg> import <module> as X` so call sites
are untouched in part 1. Every `sys.path` line is removed.

## Paths

`factory.paths` resolves `REPO_ROOT` from the package location (two levels
up in an editable install) or `FACTORY_ROOT`. Data files of the lint
(`lexique-fuite.txt`, `manifeste-auteur.txt`, `marqueurs-profonds.txt`)
travel with the package as `factory/eval/data/` and are addressed from
`paths.DATA_DIR`, never from the working directory. Defaults that were
cwd-relative strings (`bible/style-auteur.md`, the pilot table, the
experiment reports) become repository-absolute.

## Snapshot invariant

The three prompt snapshots and the lint snapshot compare against the golden
files of step 2 without regeneration after each part. The test `conftest.py`
loses its path wiring, its `chdir`, and its `BIBLE_DIR` environment: the
suite now runs from any directory.

## Container

The indexer image installs the package (`pip install .`) and runs
`python -m factory.retrieval.indexer` with `FACTORY_ROOT=/app`; the bible is
mounted at `/bible` and `BIBLE_DIR` still points there. The image carries
LangGraph it does not need; splitting the dependency groups is deferred
until the CLI exists (part 3).

## Part 2 — settings and identifiers

`factory.settings.Settings` is a dataclass with every knob and its default;
`Settings.from_env()` applies the environment once; the module singleton
`settings` is read at call time (`settings.qa_model`), never bound at import,
so tests monkeypatch a field and see it applied. Formerly French variables are
renamed (table in the module docstring and runbook §1.6).

`factory.infra.ollama.OllamaClient` holds the HTTP calls; `client` is the one
instance and `chat` / `chat_turns` / `unload` delegate to it, so the fake
replaces three methods in one place.

Identifiers were renamed with a tokenizer pass (same French word → same
English word everywhere, f-string expressions and format placeholders
included), verified by the prompt snapshots. Data keys stay: run frontmatter,
lint report keys, entry-spec dicts (step 5 makes them YAML), the deck's JSON.
ChapterState keys are English; graph nodes `glisse` and `poser_gestes` became
`drift` and `place_gestures`.

## Part 3 — nodes and CLI

The graph is `preflight → plan → … → coherence → render`. Both machine nodes
are driven by state fields so that calibration runs and the snapshot suite,
which do not set them, never probe `vm_stat` or load the voice model:

- `preflight: true | {strict, timer}` — runs `infra.preflight.preflight`,
  notes warnings, returns `preflight_warnings`; a refusal raises out of
  `graph.invoke` (the API turns it into `phase: error`, the CLI into exit 1).
- `assembly: dict` — kwargs of `assembly.assemble`, chapter knowledge
  (`ch7_state` carries `{on_second_header, fall}`); the node always produces
  `chapter_md`.
- `render: bool` — writes `chapitre.md`, unloads the QA model, renders the
  WAV; `audio` is the metrics dict or None on an ordinary voice failure.

`GET /status` takes its `tts` phase from the progress sink (the render node
enters the `Restitution` band) rather than from a job state.

`factory.cli` dispatches subcommands onto module `main(argv)` functions with
lazy pipeline imports. Dependency groups: core (chromadb-client, frontmatter,
httpx, pyyaml) for `index`/`query`/`eval`, `pipeline` for LangGraph, `tts`,
`test`. The indexer image installs core and runs `factory index`.
