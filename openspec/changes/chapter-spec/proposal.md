# Proposal: chapter-spec

## Why

Chapter knowledge was Python: chapter 7 in a module reading the briefs,
chapter 2 in the constants of a calibration driver, stations, the fall of the
accumulation and the drift bank in dicts keyed `{2, 7}` inside the pipeline.
Writing chapter 3 meant editing three modules. The factory must run any
chapter that has a specification, and the owner must be able to write one
without touching code.

## What changes

Revamp step 5 (plan §5, §8):

- `chapters/NN-slug/spec.yaml` per chapter, loaded by
  `factory.chapter_spec.load_chapter` into a typed `ChapterSpec` /
  `EntrySpec`. The file carries structure, caps and criterion names and
  POINTS at the owner's brief files and the movement table for their text,
  so a brief keeps one truth.
- `spec.state()` builds the `graph.invoke` state; the graph reads
  `stations`, `accumulation_fall`, `drift_bank`, `assembly` and the typed
  entry specs from the state. `STATIONS`, `_IMPOSED_FALL`, `DRIFT_BANK` and
  the chapter 7 module are gone; no chapter number appears in pipeline code.
- Best-of criteria are a registry (`factory.pipeline.scorers`) keyed by the
  name in the spec; the erasure criterion's lexical lists travel with the
  chapter 7 spec.
- The seal test gains a control: no `chapters/` line in any collection.
- The accumulation validator checks the language before the last-attempt
  tolerance (plan §9 gap); the strict xfail flips.

## Doctrines relied on

- 5 (instruments lie): the three prompt snapshots must be byte-identical to
  the golden files after the move — the loader reproduces the former
  states field for field.
- 7 (falsify both ways): the loader refuses a spec that names a bible file,
  serves workshop vocabulary in a literal brief, or carries a bank approach
  its own validator rejects; the drift-bank assertion moved from import time
  to load time.

## Variable moved

None in served prompts. One behaviour change outside prompts: a short
English accumulation is rejected on the last attempt instead of accepted.

## Non-goals

- The per-run API and the run registry (step 6).
- Moving the entry-2 brief's text into the spec: the brief files stay the
  owner's and are pointed at, not copied.
- Specs for chapters 1, 3–6, 8–11: author work, one file each.
