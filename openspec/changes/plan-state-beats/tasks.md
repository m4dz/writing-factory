# Tasks: plan-state-beats

## 0. First draft (beats-see-movement) — done, kept as evidence

- [x] `beats_see_movement` override, `_movement_map`, test, snapshot ch7
      unchanged (`4b7af6a`).
- [x] Experiment `20261018-beats-see-movement`: B recopies the previous
      beat (doubt 4/4 on 2 runs), density rule fails; not read (`9ce1f8e`).

## 1. Owner

- [x] Drafts of the end conditions written into `brief-entree-2.md` §7 at
      the owner's request (and into the v5 proposal copy).
- [ ] Owner corrects them.

## 2. Code

- [ ] `beat_context` override (`blind` | `map` | `plan`), alias
      `beats_see_movement=true` → `map`; refused values tested.
- [x] Loader: `Finit quand :` → `BeatSpec.ends`, removed from the
      instruction; absent → `""`. Ch7 snapshot identical.
- [ ] `_plan_state(sheet, current)`; prompt test per beat (one `→`, done
      times before it, next after it, labels only, no trajectory, guard).
- [ ] Progress gate « recopie » (≥ 2 shared sentences with the entry's
      prefix, quotation excluded), on when `beat_context != blind`;
      falsified both ways on arm B's and R's beats.
- [ ] All-variants-fail warning in the manifest.
- [ ] `make check` green, ch7 snapshot identical.

## 3. Run

- [ ] Smoke run (seed 111111, not counted).
- [ ] P × 3 seeds; blind set R × 3 + P × 3.

## 4. Conclude

- [ ] Owner verdicts; rule applied in `report.md`; journal entry.
- [ ] If P holds: `storyboard-density` serves actions through the same
      plan state.
