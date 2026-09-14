# Quality campaign — from a stage demonstration to a book

Date: 2026-09-14. Status: agreed with the owner (brainstorm session);
execution starts with the instruments, then run 1.

Successor of `2026-09-revamp.md`: the revamp made a pipeline module cheap to
add and to measure; this plan says which modules, in which order, against
which judge. Decisions taken at the same session are ADR-0026 (no time
budget, swaps as needed, one machine).

## 1. Diagnosis

The pipeline is a veto machine. Every device since August removes a named
defect: lints, best-of-N by defect count, pruning, code-posed gestures. It
has reached what vetoes can give. The retained chapter-7 draw still reads
"je me suis approchée, intriguée", "mon cœur s'est mis à battre la chamade",
"les jambes flageolantes": no veto catches that and no veto can produce its
opposite. The three complaints split:

- **Tone and density are the writer's.** nemo 12B writes genre French in
  25-word sentences with participial appositions; the contract wants 8 to 15
  words, inventory lines, verdicts. Selecting among three nemo draws picks the
  least bad nemo.
- **Narrative complexity is author data that does not exist yet.** The
  novel's complexity lives in the double-entry table (citation/commentary
  ratio, verdict migration, objects returning). Chapters 1, 3–6 and 8–11 have
  no spec, no movement, no citation (ADR-0019: about thirty movements to
  write, never generated).
- **The stage constraints chose the model.** Withdrawn for book runs by
  ADR-0026; the 18 GB ceiling remains.

## 2. Levers, ranked by expected gain per cost

| # | Lever | What moves | Why it should work | The defect it will create (doctrine 12) |
|---|-------|-----------|--------------------|------------------------------------------|
| 1 | Author attack per beat | the owner writes the first sentence of each beat; the model continues | a small model follows the register of a prefix better than an instruction about register; the attack is author text, meant to be recited | the model paraphrases the attack as its second sentence (the reattach dedup exists) |
| 2 | Writer swap | `AUTHOR_MODEL`, everything else fixed | ADR-0008 measured mistral-small 24B as better prose, zero leak; rejected on speed alone | a stronger model recites less, so the "no examples served" rule (ADR-0011) may be relaxed for it, in a later run |
| 3 | Write the house | `bible/lieux/maison.md`: rooms, objects per room, provenance, and "what the house does not have" | the style's engine is the named object; the model fills the void with hi-fi and television (doctrine 7) | a longer served context; the firewall check on the new file |
| 4 | Positive style scorer | countable features as a tie-break in best-of-N | selection today counts defects only and cannot prefer the denser variant | over-fitting to the étalons; kept as a tie-break behind the defects, never as a judge |
| 5 | Pairwise local judge | a 24B judge asked "which of these two reads like the étalons", position-swapped | pairwise preference is far more reliable than absolute grading; scales the owner's reading, does not replace it | the judge's own taste; falsified on étalon-versus-journal pairs before use |
| 6 | Demote repair | review emits sentences to cut, code applies; no 7B rewrite | measured twice: Qwen cut the good paragraph and pushed an entry under target | fewer English repairs; the delint net stays |
| 7 | Sampling knobs | temperature, min_p, top_p, repeat penalty in Settings | five hardcoded 0.7 in node code; a clean model swap needs them configurable | none expected; the snapshot proves prompts do not move |
| 8 | LoRA on the owner's corpus | MLX LoRA on 20–30 hand-written or hand-corrected entries | the only lever that produces Judith rather than avoiding non-Judith | needs the corpus that levers 1 and 3 start building; last |

Not done, argued: a new harness (none of the thirty walls in the journal was
the graph); more vetos in the served prompt (doctrines 10 and 12); sentence-
by-sentence generation (fixes density, produces a litany, paid for with the
stations).

## 3. Protocol

Reference: chapter 7, entry 2 (the calibrated entry, its manual grid line
"is the declared movement accomplished?"). One variable per run, three draws
per condition, seeds recorded, `report.md` in the run directory, failures to
the journal (doctrine 13).

| Run | Variable | Constant | Judge |
|-----|----------|----------|-------|
| 1 | author attack per beat (lever 1) | nemo, sampling as today | manual grid line; style scorer offline |
| 2 | writer swapped to the best bench candidate (lever 2) | no attack | same |
| 3 | both | | same |

Run 2 is preceded by the **bench**: `factory bench --models a,b,c --draws 3`
runs the write node of the reference entry per model, records texts, tok/s,
context need, lint line and style score. Candidates must fit under 18 GB
with the QA model unloaded. Bench first, then run 2 on the retained model.

## 4. Instruments (built first, no model needed)

- Lever 7: sampling knobs in Settings and the client; `write_temperature`
  replaces the hardcoded 0.7. Snapshots identical.
- Lever 1: `attack` on a beat (spec literal or brief blockquote); the write
  node prefixes it, bounds the model's sentences minus the attack's, strips a
  paraphrased restart. Chapter 7's spec carries no attack yet: the owner
  writes them (author material).
- Lever 4: `factory.eval.style` — features and composite score; falsified
  offline: the four étalons outrank every journal run and the retained
  2026-08-27 draw. Wired as a tie-break behind the defect scores in both
  best-of selections.
- Bench: `factory bench`, one run directory per invocation with a manifest.

## 5. Author work that gates the book

Independent of every run above, and the real bottleneck:

- `bible/lieux/maison.md` (lever 3), including the section "what the house
  does not have".
- The attacks of chapter 7 entry 2 (three sentences), for run 1.
- Chapter 1's spec and its movements, written by hand: the first entries of
  the reference corpus that levers 5 and 8 need.

## 6. Status

| Step | Status |
|------|--------|
| ADR-0026 | done 2026-09-14 |
| Instruments (§4) | in progress, this branch |
| Bench | tool ready; run on the owner's machine |
| Run 1 | waits for the attacks |
| Run 2 | waits for the bench |
| Run 3 | waits for 1 and 2 |
