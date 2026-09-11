# Doctrines

Fourteen working rules established over seven measurement sessions (August
2026), each paid for by a failed run. They are the project's most valuable
asset and the first thing a change is checked against. The French mottos are
kept: they are how the rules are named in the journal and the grids.

This is their only home. `CLAUDE.md` points here; the ADRs cite them by number.

## The rules

1. **The model supplies the matter, the code holds the gesture.** *Le modèle
   fournit la matière, le code tient le geste.* Fall line, anchor quotation,
   dated headers, drift passage, assembly, audio switch: composed by code,
   never requested from the model. Three draws in a row missed the fall line;
   the code has posed it since.

2. **Warmth is not generated, it is composed.** *La chaleur ne se génère pas,
   elle se compose.* The firewall starves the model of warm material by
   construction, so its spontaneous warmth is invented, always in the warm
   passages (first names, ghosts, the chapter-7 quartet). Everything warm in
   the novel is written by hand and injected: quotations, drift passages,
   movements.

3. **Counting is not reading.** *Compter n'est pas lire.* The automatic grid is
   a veto (leaks, anchors, interdicts, bounds); the judge is the owner reading
   aloud, now embodied in the single manual grid line "is the declared
   movement accomplished?". An accumulation in English once passed every
   counter.

4. **Falsify in both directions.** A check must fail on a known defect AND
   accept the reference. Four checks that looked right refused the reference
   or the bank: `CHAMP_DEPART` required the word of the departure in a
   sentence whose point is to stop before it; the "verbal clauses" criterion
   rejected the reference accumulation, nominal at 88 %; word similarity would
   have removed the accumulation itself; a length filter hid the only real
   duplicate.

5. **Instruments lie.** A phantom lint (computed, never wired to the grid), a
   message reporting something other than what the gate measured, a stopwatch
   that stops during sleep (`time.monotonic()` on macOS), a missing grid line.
   No detector without its grid line; no figure without its clock.

6. **Shown is recited.** *Montré = récité.* Reference excerpts, examples,
   counter-examples, the words of our own instructions: anything served can
   come back verbatim ("perplexe" was the counter-example; "Couperet :" came
   from the served skeleton; an opening instruction came back at 0.94
   similarity). Instances live in the tooling; served context carries only
   categories and attitudes.

7. **A void in the served matter always fills.** With the model's generic
   world (work, television, handbag) or with a borrowing from another chapter
   (the "coquille" verdict at chapter 7). The void is written: the section
   "what the house does not have", "no verdict is rendered tonight".

8. **An instruction that describes what the character decides produces a
   character who describes their decisions.** Instructions state facts and
   trajectories, never intentions. "Je décide de" ×7 on one run, and it was
   our instruction.

9. **The exception is declared in data, never as a loosened rule.**
   `entrees_spec` carries chapter 7's two same-day entries. Corollary: every
   validator written before a structure existed reads that structure as an
   anomaly (three occurrences: drift, review guard, chapter-7 headers).

10. **The interdict alone displaces the defect.** The sheet says what the
    character does *instead* (she writes it down; the body, one line).

11. **Any nested fiction is a tunnel under the lexical firewall.** The inner
    novel of run B′C.

12. **Every device that fixes a defect creates one where it touches.** Look
    for it there, systematically. Segmentation fixed the mass and made three
    arcs; stations fixed the floor and made a litany.

13. **One variable between two measurements; failed runs are material.**
    `experiments/journal/`, one entry per cause: the knife blow, the inner
    novel, the fabricated dinner, the nominal summary, "Finalement, j'ai
    compris", the saga of six draws, "the clone said everything except the
    sentence it speaks for".

14. **The archive lint runs on the FINAL set, just before shipping.** Two
    archives left with an unchecked file: the README had been written after
    the lint pass. Lint, then add, then ship, is not having linted.

## The method rule: an instrument is falsified before it serves

Before trusting a check, require it to FAIL on a known case: inject the
defect, or replay the check on outputs already known by hand to be faulty. A
check that never failed has proven nothing: it may run on an empty set, test
an impossible condition, or be disconnected from its report.

The **phantom lint**, a correct detector whose result never reaches the grid,
is the most expensive form, because it reads as a success.

Three times the check was GREEN before it was falsified:

- **Seal test (session 4).** It queried the author collection to verify that
  no deep chunk came out, but the deep layer lived in another collection: it
  passed by construction. The remedy is the positive witness: a deep chunk is
  deliberately injected and MUST come back.
- **Splitter (session 4).** The check filtered chunks by id prefix, and a
  `doc_id` mismatch left it running on zero chunks. Green on the empty set. It
  now fails explicitly when the set is empty.
- **Grid (session 5).** Five detectors existed in the lint and none had a line
  in the grid. They computed, the result was thrown away; an attractor went a
  whole run without a cross.

Corollary: **automating a check and making it blocking are two decisions.**
Confusing them fails a run on a minor tic while the criteria that matter pass.

## How they are used

- An openspec proposal names the doctrines it relies on or challenges.
- A change that adds a validator ships with the case it must reject and the
  reference it must accept (doctrine 4), and with its grid line (doctrine 5).
- A change that adds served text ships with the check that it carries no
  workshop vocabulary and no example line (doctrine 6).
- A run that fails goes to `experiments/journal/` with its cause (doctrine 13).
- A new doctrine is added here, numbered, with the run that established it.
