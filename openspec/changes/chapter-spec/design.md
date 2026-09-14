# Design: chapter-spec

## Model

`ChapterSpec` (frozen dataclass): chapter, slug, narrator, brief,
entry_count, calendar, verdict, active_objects, prefix, stations,
accumulation_fall, drift_bank, assembly, defaults (rag, micro_nodes,
segments), entries, imposed_plan, entry_brief, workshop_terms.
`EntrySpec`: weekday, number, weather, words, sentences_max, citation (None:
chapter prefix; "": none), gestures, strategy (single | segments | beats |
None), beats (BeatSpec: name, num_predict, sentences_max, instruction),
best_of (BestOf: n, criterion, names, drift), movement, trajectory,
material, vetos, form, fall, drift (Drift: text, position). `EMPTY_ENTRY`
stands for an entry the spec does not describe.

## Loader

`load_spec(path)` reads YAML, then resolves pointers: `brief: {file,
section}` → blockquote of that section, fabrication notes stripped;
`plan: entries-of-brief` → one beat per `**Entrée N`; entry `source:` →
sections `## 1. Intention`, `## 2. Trajectoire`, `## 3. Matière`,
`## 4. Glissement`, `## 7.` beats of the entry brief; `movement: {entry: N}`
→ one row of the deep table. Assertions: no `*.md` in served text, no
workshop or machinery term in a literal brief (the former stage-runner
assertion), bank approaches pass `approach_valid`, beat caps and beat
instructions match one to one, `entry_count` agrees with `entries` and with
the imposed plan. Workshop terms found in the owner's brief file are
reported on the spec, not rewritten (the chapter 7 brief carries
« matériau »; that is the author's call).

## State

`spec.state(seed, brief, entry_count, rag, micro_nodes, segments, prefix)`
returns the former `ch7_state()` / stage-S7 dict plus `stations`,
`accumulation_fall`, `drift_bank`. Verified field by field against the former
constructions before the chapter 7 module was deleted; the golden snapshots
did not move.

## Graph

`write_node`, `_movement_prompt`, `_gestures_allowed`, `_entry_target`,
`assemble_node`, `drift_node` read `EntrySpec` attributes; `state.get(
"chapter") or 2` defaults become `or 0` (the lint's chapter scope only);
`draw_approach(bank, drawn, seed)` takes the bank from the state.

## What the snapshots show

`tests/snapshots/scenarios.py` builds both chapters through the loader;
`prompts.md`, `chapter.md` and `warnings.txt` of the three scenarios are
unchanged. `test_chapter_spec.py` covers discovery, pointers, the state
builder, minimal specs and the refusals; `test_seal_chapters.py` the new
control; the gesture tests take the bank from the chapter 2 spec.
