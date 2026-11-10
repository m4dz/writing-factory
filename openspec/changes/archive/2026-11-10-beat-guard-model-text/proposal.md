# Proposal: beat-guard-model-text

## Why

`xp-author-models`, run M/781771 (2026-10-19): the run died after 3 minutes on
the entry guard of `_prompt_beat` (`graph.py:1413`,
`AssertionError: ... ['grille']`). The model had written « grille » (ordinary
French: the oven rack) in an earlier beat; that text is re-served as the
prefix of the next beat (`already`), and the guard reads the whole assembled
prompt, model text included.

The guard exists to keep OUR machinery and workshop words out of what we
serve (doctrine 6; it caught « matériau » in session 6 and `fiche-romane.md`
in session 7). It was written when the served assembly held only owner and
code material. Since the prefixing doctrine, it also holds the model's own
text, and the term lists overlap ordinary French: `grille`, `le code`,
`ancres`, `matériaux`, `squelettes`, `bloquants`. A legitimate word in the
prose crashes the run.

The defect is not Ministral's: nemo can write « la grille du four » or « le
code de la porte » on any seed. Two sites carry it:

- `_prompt_beat` (beats path, production for chapter 7 entry 2), via `block`;
- `_movement_prompt` (segments path), via `prefix_block` built from the same
  `already` (`graph.py:827`).

## What changes

- Both guards check what the CODE serves, not what the model wrote: the
  instruction, the plan state or movement map, the block wrapper, the suffix,
  the code-posed prefix (quotation anchor, owner canon). The model-written
  part of `already` (`text`) is excluded from the scan.
- Model-written workshop terms stay visible where they already are: the
  output lint (`lint.md`) reports them on the final text. No new selection
  rule in this change.
- Falsified both ways (doctrine 4), one test per site:
  - a served instruction carrying « grille » still raises;
  - model text carrying « la grille du four » in `already` does not.
- Snapshots: no served prompt moves (the scan changes, not the assembly);
  `tests/snapshots` must stay identical.

## Open question for the owner

Should a beat variant whose own text carries a workshop term be scored as a
named defect in `_score_beat` (non-veto), so the best-of prefers a clean
variant? It would make « grille du four » cost a variant. Proposed: no, the
lint report is enough until a run shows a real workshop leak in model text.

## Out of scope

The term lists themselves (narrowing `grille` to a context would be a lint
arbitration, owner's call); re-drawing M/781771 (`xp-author-models` is
concluded by its rule).
