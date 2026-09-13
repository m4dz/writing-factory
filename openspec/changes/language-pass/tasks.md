# Tasks: language-pass

- [x] `src/factory/pipeline/graph.py` comments and docstrings in English.
- [x] `src/factory/eval/lint.py`.
- [x] `src/factory/pipeline/{gestures,assembly,qa,scorers}.py`, `nodes/`.
- [x] `src/factory/api/server.py`, `src/factory/infra/*`.
- [x] `src/factory/eval/{grid,seal,journal}.py`, `tooling/*`, `cli.py`, `runs.py`.
- [x] `src/factory/retrieval/*`, `roleplay/*`, `text.py`, `chapter_spec/*`,
      `settings.py`, `paths.py`, `tests/**`.
- [x] `tests/unit/test_language.py`: the audit as a test, falsified both ways.
- [x] `conftest.py` without `sys.path`; `pythonpath` in `pyproject.toml`.
- [x] Docs: architecture note, plan step table, ADR-0001 closed; ADR-0021 to
      ADR-0025 record the arbitrations that lived only in comments.
- [x] Three stale string literals corrected (named here, outside prompts): the
      session file header (`factory.roleplay.session`), the grid report footer
      (`factory eval grid`), the resolution experiment's journal path
      (`experiments/journal/`).
- [x] `make check` green; snapshots identical; the language audit passes over `src/factory/` and `tests/`.
