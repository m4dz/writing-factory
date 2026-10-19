# Tasks: beat-guard-model-text

## 1. Owner

- [ ] Go on the scope; answer the open question (score model-written terms or not).

## 2. Code

- [ ] `_prompt_beat`: scan the served pieces only; the model-written text is excluded.
- [ ] `_movement_prompt` (segments path): same.
- [ ] Tests, both directions per site: served term raises; model-written
      « la grille du four » passes.
- [ ] `make check` green, snapshots identical.

## 3. Close

- [ ] Journal line linking `xp-author-models` M/781771 as the triggering run.
