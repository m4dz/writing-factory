# Tasks: storyboard-density

## 0. Gates

- [ ] `scaffold-ablation` concluded; reference configuration fixed.
- [ ] Owner corrects the draft (`storyboard-draft-ch7-entree-2.md` in this
      folder) and moves it to `chapters/07-anniversaire/storyboard-entree-2.md`.
- [ ] Owner decides whether the attempted verdicts stay in the list (C5 risk).

## 1. XP A — hand storyboard

- [ ] Spec model and loader: beat `actions` pointer, refusals, derived caps.
- [ ] Served form; snapshot scenario `ch7-storyboard` added (the only
      snapshot that moves).
- [ ] Measures: action matching, recopy, litany, sentence-length slope.
- [ ] Variant spec for arm S under the experiment directory (`--spec-file`
      from `scaffold-ablation`).
- [ ] 10 runs (R, S × 5 paired seeds); blind set to the owner; report.

## 2. XP B — generated storyboard (only if A: S not worse than R)

- [ ] `storyboard` node, planner model as a setting, one swap.
- [ ] Plan veto with one re-plan; fake-model tests.
- [ ] 18 lists (6 planners × 3 seeds); owner reads the lists; render those
      that pass; report.

## 3. XP C — rendering grain

- [ ] Per-action rendering strategy; 6 runs; report.

## 4. Conclude

- [ ] ADR proposal; journal entries for failed draws; `make check` green.
