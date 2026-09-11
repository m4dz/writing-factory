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

## Parts 2 and 3

Designed when their turn comes, in this file, after part 1 is merged.
