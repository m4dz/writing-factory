# Tasks: sampling-knobs

- [x] Settings: `write_temperature`, `min_p`, `top_p`, `repeat_penalty`,
      `sampling_options()`, env table.
- [x] Client: `options` on `chat`, `chat_continue`, `chat_turns`; recorded
      when present; `prompts.md` shows them.
- [x] Graph: the four writing calls read `write_temperature` and pass the
      options through `_generate_whole`.
- [x] Run overrides and resolved configuration.
- [x] `tests/unit/test_sampling.py`; fake model takes `options`.
- [x] Runbook variable table.
- [x] `make check` green, three snapshots byte-identical.
