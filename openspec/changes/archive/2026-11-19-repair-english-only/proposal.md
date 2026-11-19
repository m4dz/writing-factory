# Proposal: repair-english-only

## Why

The language repair (Qwen) is served the whole entry with « corrige TOUT
passage qui n'est pas en français … tu ne changes NI le sens ». It rewrites
French anyway. Measured 2026-11-16 (`experiments/runs/20261116-review-guard/`,
chapter 7 with M), on entries without any English:

- 174597: « J'ai décidé de ne pas allumer les bougies du soir. » → « Je n'ai
  pas allumé les bougies du soir. » — the decision, subject of entry 1, gone;
- 424242: « *le 23 octobre 1987, trois ans, déjà* » → « *23 octobre 1987,
  trois ans déjà* ».

Its only guard looks at length.

## What changes

- `text.english_leaks`: the lint's English detection (suspect words,
  corrupted tokens), shared with `delint`.
- `qa.repair_leaks`: split the entry at the sentence ends the project uses
  (`sentence_ends`), serve to the repair ONLY the sentences with a detected
  leak, one call each, and put each answer back in place; every other byte
  is kept. A sentence answer that is empty or spans paragraphs is refused
  (original kept, warned). An entry without a leak costs no call.
- `repair_node` uses it; the whole-entry length guard stays.
- Owner's choice (2026-11-16): repair only detected English, not a guard on
  a whole-entry rewrite.

## Variable moved

The repair's input: a sentence instead of an entry. Served prompts moved
(named): every `qa.repair` call disappears from the three snapshot
scenarios, whose fake texts carry no English; the chapters are unchanged.

## Risk

The detection is the lint's, minimal (`the`, `and`, `with`, … and glued
tokens). English it does not see is no longer repaired; before, the repair
saw everything and rewrote French with it. `delint` still warns on residual
English after the repair.
