# Proposal: entry1-notebook-checks

## Why

`xp-author-models-2` made M (Ministral 3 14B) the writer. Its best entry 2
(seed 487914) comes with an entry 1 that opens on an invented quotation in
the third person: « « Elle a posé le stylo… » ». The brief forbids both (entry
1 does not quote; the notebook is in the first person), and entry 1 is the
one the speaker reads aloud on stage.

The entry-1 best-of scores one criterion, `names-erasure`. It never looked at
person or quotation. Measured on the 59 retained chapter-7 entries 1 under
`experiments/runs/`: **21 quote** (nemo included), 5 are in the third person
once bounded to their two served sentences (M and S only). All were served.

Cause of the third person: the entry-1 matter is written with « elle »
(`chapters/07-anniversaire/spec.yaml`, `material` and `vetos`), and a model
that recites less than nemo still transposes it.

## What changes

- **B (code).** `scorers.notebook(variant, cites)`, added to the criterion's
  score in every entry best-of:
  - third person: no first-person mark, and two « elle » or a sentence
    opening on « Elle » — −10;
  - quotation, for an entry without anchor (`citation: ""`): a quotation
    opening the entry, or any quoted span of five words or more — −10.
  The beats' first-person and « elle » patterns move to `scorers` and are
  shared.
- **Fix found on the way.** The first-person pattern carried a right word
  boundary after the elided forms, so « j'ai », « m'a » never matched. A
  beat in the first person only through elisions, with two « elle », was
  counted as third person. Fixed; it can change a beat selection under a
  real model, never a served prompt.
- **A (owner).** The entry-1 matter and vetos rewritten without « elle »:
  the owner chose form 2, nominal, without person (`entree-1-proposal.md`),
  applied verbatim on the owner's instruction.

## Variable moved

B moves no served prompt. A moves the entry-1 served prompt: in the `ch7`
snapshot, material 1 and the vetos of the three entry-1 calls (best-of-3);
nothing else.

## Non-goals

- Entry 2's beats keep their own checks (unchanged apart from the shared
  pattern fix).
- A quotation inside an anchored entry stays legal.
