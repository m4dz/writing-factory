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

- [ ] `factory.settings.Settings` (one object, env overrides) replacing the
      37 `os.environ.get` reads; modules read `settings.*`.
- [ ] One model client object injected into pipeline, QA and roleplay; the
      fake replaces it in one place.
- [ ] French identifiers → English across the package; tests renamed with
      them, aliases removed.
- [ ] `make check` green; snapshots identical.

## Part 3 — nodes and CLI

- [ ] `preflight` and `render` as graph nodes with their spec fields.
- [ ] `factory` CLI: `generate`, `index`, `eval`, `serve`, `doctor`,
      `promote` placeholder; `tooling/` drivers folded or deleted.
- [ ] Runbook rewritten for the CLI; container dependency groups split.
- [ ] `make check` green; snapshots identical.
