# Tasks: beat-instruction-form

## 1. Owner

- [x] Correct and validate the three nominal forms (proposal), then their
      writing into `brief-entree-2.md` §7 under each beat.
- [x] Validate the predictions and the decision rule (`report.md`).

## 2. Code

- [x] Loader: `Nominal :` / `Finit quand (nominal) :` read apart
      (`BeatSpec.nominal`, `.ends_nominal`); prose instruction untouched.
- [x] Override `beat_form` (`prose` | `nominal`), closed set; recorded in the
      run config.
- [x] `_served_beat`: instruction, plan-state labels and end condition in the
      served form; a beat without nominal form refuses the run.
- [x] Tests (loader, served form, plan state, prompt, override); `make check`
      green (344), ch7 snapshot identical.
- [x] `recital.py`: recital over every drawn variant, against both forms;
      baseline measured on xp-author-models.

## 3. Run

- [x] Smoke F, seed 111111: mechanical checks (no « elle » copy, no empty
      variants, person held, guard).
- [x] R, F × 140419, 602237, 913085.
- [x] Table: recital, third person, short sentences, veto defects, words.
- [x] Blind set: entry 2 of the six chapters, shuffled, key closed.

## 4. Conclude

- [ ] Owner verdicts; rule applied; journal entry.
- [ ] Conclusive → `xp-author-models` follow-up (Ministral and/or Mistral
      Small) on the winning form.
