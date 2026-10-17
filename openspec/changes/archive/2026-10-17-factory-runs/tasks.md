# Tasks: factory-runs

- [x] `factory.runs`: run directories, manifests, whitelisted ids, listing,
      result recording (`prompts.md`, `lint.md`); `Settings.runs_dir`,
      `Settings.generated_dir`; `OllamaClient.recording`.
- [x] `Worker` with a queue replaces `Job`; per-run routes; `410` on the
      keynote's routes; `/health` lists chapters and queue.
- [x] `narrative_state` node (`pipeline/nodes/narrative_state.py`),
      `chapter_spec.narrative_state` rewritten as functions; indexer
      `chapter` metadata and `::chNN` ids; retrieval prefers the chapter chunk.
- [x] Render node writes into `artifacts_dir`.
- [x] `factory generate --chapters`, `factory runs`, `factory promote`.
- [x] Seal manifest globs; control 6 exempts promoted scenes.
- [x] Tests: API, runs, narrative state, CLI; `fake_chroma` per test.
- [x] Docs: runbook, architecture, README, plan; specs api/pipeline/retrieval.
- [x] `make check` green; snapshots identical.
