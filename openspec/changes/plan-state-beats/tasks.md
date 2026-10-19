# Tasks: plan-state-beats

## 0. First draft (beats-see-movement) — done, kept as evidence

- [x] `beats_see_movement` override, `_movement_map`, test, snapshot ch7
      unchanged (`4b7af6a`).
- [x] Experiment `20261018-beats-see-movement`: B recopies the previous
      beat (doubt 4/4 on 2 runs), density rule fails; not read (`9ce1f8e`).

## 1. Owner

- [x] Drafts of the end conditions written into `brief-entree-2.md` §7 at
      the owner's request (and into the v5 proposal copy).
- [x] Owner validated them as written (2026-10-19).

## 2. Code

- [x] `beat_context` override (`blind` | `map` | `plan`), alias
      `beats_see_movement=true` → `map`; refused values tested.
- [x] Loader: `Finit quand :` → `BeatSpec.ends`, removed from the
      instruction; absent → `""`. Ch7 snapshot identical.
- [x] `_plan_state(sheet, current)`; prompt test per beat (one `→`, done
      times before it, next after it, labels only, no trajectory, guard).
- [x] Progress gate « recopie » (≥ 2 shared sentences with the entry's
      prefix, quotation excluded), on when `beat_context != blind`;
      falsified both ways on arm B's and R's beats.
- [x] All-variants-fail warning in the manifest.
- [x] `make check` green, ch7 snapshot identical.

## 3. Run

- [x] Smoke run v1 (seed 111111, not counted): FAILED, recopy 6/6 (`8c8ac01`).
- [x] v2 (owner's go 2026-10-19): continuation turn in the client, prompt
      order (written text before the task), system folded, `prompts.md`
      records the start of the answer; tests.
- [x] Smoke run v2: FAILED, 6/9 empty variants (`59703ab`).
- [x] v3: begun answer ends on a blank line; « vide ou trop court » in the
      plan selection; end condition in the state line.
- [x] Smoke run v3: passed the mechanical checks (`d2c08b6`).
- [x] P × 3 seeds; blind set R × 3 + P × 3 (shuffle seed 503640).

## 4. Conclude

- [ ] Owner verdicts; rule applied in `report.md`; journal entry.
- [ ] If P holds: `storyboard-density` serves actions through the same
      plan state.
