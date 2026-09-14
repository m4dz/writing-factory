# Proposal: author-attack

## Why

A 12B writer follows the register of a prefix far better than an instruction
about register: the header and the anchor are already posed by code and the
model continues them without altering them (ADR-0018). The remaining defect
of the chapter-7 draws is register, not structure. Lever 1 of the quality
campaign lets the owner write the first sentence of each beat, the ATTACK,
and the model continue it. This is author material, meant to be recited.

## What changes

- `BeatSpec.attack` (default empty). Source: a literal `attack:` on the
  beat's cap line in `spec.yaml`, or a `> ` blockquote under the beat's
  heading in the entry brief's §7; the spec literal wins.
- The write node poses the attack as the last line of the "already written"
  block served to the beat, bounds what the model adds to the beat's sentence
  cap minus the attack's sentences (at least one), removes a verbatim or
  paraphrased echo of the attack at the head of the model's segment, scores
  the model's text alone, and concatenates the attack in front of the
  retained variant. A warning names the attack and the remaining cap.
- The loader guards the attack like any served text: no bible file name, no
  workshop or machinery vocabulary.
- Chapter 7's spec carries no attack: the attacks are author work, written
  for run 1 of the protocol.

## Doctrines relied on

- 1 and 6: the attack is posed by code, and it is recited on purpose because
  it is the author's line; the echo filter handles the model reciting it a
  second time.
- 12: the defect it creates is the paraphrased restart; measured in the test
  and stripped.

## Variable moved

Run 1 of the protocol (`docs/plans/2026-09-quality-campaign.md` §3): the
attack, chapter 7 entry 2, nemo unchanged. In this change: no served prompt
moves, the three snapshots are identical because no spec carries an attack.

## Non-goals

- Writing the attacks: author material.
- Attacks on segments or single-call entries: the beat is the unit where the
  register is lost; extend only if run 1 says so.
