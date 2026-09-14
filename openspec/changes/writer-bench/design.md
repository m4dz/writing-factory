# Design: writer-bench

## Sampling

`Settings.sampling_options()` returns the optional knobs that are set;
`OllamaClient.chat_turns` merges them into `options` after temperature,
`num_predict`, `num_ctx`. `validate_overrides` casts an optional knob to
float, or keeps `None`. The graph's four writing calls pass
`settings.write_temperature`; plan (0.5) and review (0.5) keep their own.

## Bench

`run_bench(models, draws, chapter, entry, seed, root)`: `load_chapter`,
refuse a chapter without `imposed_plan` or an entry out of range; for each
model, `unload(previous)`, set `settings.author_model`, then per draw build
the write state (`plan`, `idx`, empty previous scenes, empty metrics and
warnings), record the client's calls, run `write_node`, summarise (words,
write-node metrics summed, tok/s, `ctx_need` max, `done_reason: length`
count, `style.score`, lint failure keys, the entry's warnings) and write the
draw file. `settings.author_model` is restored in a `finally`. Aggregates per
model: means of words, tok/s, wall, style; style min; `ctx_need` max; cuts;
lint failures. The report has the table, the empty judge table, then every
draw with its warnings folded.

## What the fixtures and snapshots show

`tests/unit/test_sampling.py`: the options payload with and without knobs
(the request body is captured through `urlopen`), env parsing, overrides,
and the beat calls carrying the configured temperature.
`tests/unit/test_bench.py`: two models, two draws on the fake model, the
directory, manifest, draw files, report and prompts, the registry ignoring
the bench, the author model restored, the two refusals. Snapshots identical.
