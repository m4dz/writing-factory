# Tasks: safety-net

- [x] `pyproject.toml` with the test extra, ruff rules (repo: bug-class only;
      tests: E, F, I, W), pytest markers; `Makefile` with `check`, `lint`,
      `test`, `snapshots`; `.gitignore` for the venv and caches.
- [x] `tests/conftest.py`: path wiring of the current layout, cwd at repo root,
      Telegram disabled, fixtures `fake_model`, `fake_chroma`, `bible_chroma`,
      `quiet_progress`, option `--update-snapshots`.
- [x] `tests/fakes/llm.py` dispatcher; `tests/fakes/fixtures.py` nominal and
      failing texts; `tests/fakes/chroma.py` from the indexer chunker.
- [x] `tests/unit/test_fixtures.py`: every fixture through its validator,
      failing twins trip theirs.
- [x] Unit tests: `style`, `chapitre`, graph helpers, `gestes`, `qa`,
      `notify`, `roleplay`, `ch7`, `indexer`.
- [x] Lint snapshot over `journal-des-murs/*.md` and `runs-ch7/*.md`
      (34 files, non-empty corpus asserted).
- [x] `tests/snapshots/scenarios.py` (ch7, ch2-s7-score, ch2-s7-chapter) and
      `test_snapshots.py`; golden files generated from the current code.
- [x] Stage tests: preflight gate, render with fake synthesizer, API in-process,
      retrieval assembly.
- [x] Record the findings (plan §9): validator ordering gap as strict xfail,
      header-as-two-sentences, name binding.
- [x] `make check` green; second run identical (snapshots stable).
- [ ] Owner: run `make venv && make check` on the stage machine once, to
      confirm the suite is machine-independent (no macOS or Ollama needed).
