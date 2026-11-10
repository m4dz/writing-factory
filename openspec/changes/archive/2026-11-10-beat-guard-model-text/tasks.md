# Tasks: beat-guard-model-text

## 1. Owner

- [x] Go on the scope (2026-10-20). Open question not answered: the proposed
      default applies (model-written terms are not scored; lint reports them).

## 2. Code

- [x] `_prompt_beat`: scan the served pieces only; the model-written text is excluded.
- [x] `_movement_prompt` (segments path): same.
- [x] Tests, both directions per site: served term raises; model-written
      « la grille du four » passes.
- [x] `make check` green, snapshots identical.

## 3. Close

- [x] ~~Journal line linking `xp-author-models` M/781771 as the triggering run~~:
      moved to `xp-author-models-2` task 4 (its journal entry, the first run
      under the fix).
