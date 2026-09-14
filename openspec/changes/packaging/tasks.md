# Tasks: packaging

## Part 1 — skeleton and moves

- [x] `src/factory/` package with sub-packages and `paths.py`.
- [x] Every module moved with `git mv` to its English module name.
- [x] Imports rewritten to absolute package imports; `sys.path` lines and
      `noqa: E402` removed; unused `sys`/`Path` imports dropped.
- [x] Repository paths resolved through `factory.paths`; lint data files as
      package data; cwd-relative defaults made repository-absolute.
- [x] `pyproject.toml`: runtime dependencies, `tts` extra, `src` layout,
      package data, isort first-party.
- [x] `docker/indexer.Dockerfile` installs the package; compose updated;
      `requirements.txt` files removed.
- [x] Tests: imports repointed (aliases keep bodies unchanged); `conftest.py`
      without path wiring or `chdir`.
- [x] Docs: architecture layout, runbook commands, README, specs' purposes.
- [x] `make check` green; snapshots identical.

## Part 2 — settings and identifiers

- [x] `factory.settings.Settings` (one object, env overrides) replacing the
      37 `os.environ.get` reads; modules read `settings.*`.
- [x] One model client object injected into pipeline, QA and roleplay; the
      fake replaces it in one place.
- [x] French identifiers → English across the package; tests renamed with
      them, aliases removed. Graph nodes `glisse` → `drift`, `poser_gestes`
      → `place_gestures`; ChapterState keys English; data keys (run
      frontmatter, lint reports, entry-spec dicts, deck JSON) unchanged.
- [x] `make check` green; snapshots identical.

## Part 3 — nodes and CLI

- [x] `preflight` and `render` as graph nodes (`pipeline/nodes/`), driven by
      the state fields `preflight`, `render`, `assembly`; the API job is the
      graph and nothing around it.
- [x] `factory` CLI (`factory.cli`, `[project.scripts]`): `doctor`, `index`,
      `query`, `generate`, `calibrate`, `eval lint|grid|seal|journal`,
      `serve`, `chat`, `promote` placeholder. Drivers deleted: `run_chapter`
      (folded into `generate`), `ch2_runner`, `scene_runner`, `modelfile`
      (pre-graph sessions; their protocols and results are in
      `experiments/`, their code at `v0-keynote`). Kept in `tooling/`:
      `stage_runner` (`factory calibrate`, chapter 2 constants → step 5),
      `interviews` (demo assets), `resolution_xp` (an experiment's recipe).
- [x] English CLI flags (`--stage`, `--only`, `--seed`, `--references`,
      `--sheet`); entry points take `argv`.
- [x] Runbook rewritten for the CLI; dependency groups: core, `pipeline`,
      `tts`, `test`; the indexer image installs core and runs `factory index`.
- [x] `make check` green; snapshots identical.
