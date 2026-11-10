# Proposal: sampling-knobs

> Ported from `writer-bench` on `claude/narrative-improvement-brainstorm-4ip7lw`
> (roadmap v3, item 2.1): the sampling part only. The bench itself is not
> ported.

## Why

The writing calls' temperature is a constant `0.7` in four places of
`write_node`, and `min_p`, `top_p`, `repeat_penalty` cannot be set at all.
Comparing writers (Phase 3, `xp-abliterated`; any writer change after the
stage) needs the sampling to be configuration that a run records, not node
code: doctrine 13 asks that the one variable moved be visible in the
manifest.

## What changes

- **Settings.** `write_temperature` (default `0.7`, the former constant),
  `min_p`, `top_p`, `repeat_penalty` (default unset). Env `WRITE_TEMPERATURE`,
  `MIN_P`, `TOP_P`, `REPEAT_PENALTY`. `Settings.sampling_options()` returns
  the optional ones that are set.
- **Run overrides.** All four are in `runs.OVERRIDABLE` and in the resolved
  configuration of every manifest; an optional knob is cast to float or kept
  `None`.
- **Client.** `chat`, `chat_continue`, `chat_turns` take `options`, merged
  into the request after `temperature`, `num_predict`, `num_ctx`, and
  recorded in `prompts.md` when present.
- **Graph.** The four writing calls of `write_node` read
  `settings.write_temperature` and pass `settings.sampling_options()` through
  `_generate_whole` (continuations included).

### Departure from the narrative branch

There, the client merged the knobs into **every** request. That would move
the plan call, the review rewrite, the QA model's checks and the gestures
whenever a knob is set for the writer: two variables instead of one, and the
QA model (another family) sampled with a penalty tuned for the writer. Here
the knobs are passed explicitly by the writing calls only; the client never
injects them.

## Variable moved

None. With no knob set, the request options are byte-identical; the three
snapshots are unchanged.

## Non-goals

- `factory bench` (the writer bench): not ported.
- Sampling of plan (0.5), review (0.5), QA and gestures
  (`gesture_temperature`): unchanged.
