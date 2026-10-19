# Design: storyboard-density

## Shape of a storyboard

Owner-owned file `chapters/07-anniversaire/storyboard-entree-2.md`, one
section per beat (`### Beat A — la relève` …), one numbered action per line.
The spec points at it:

```yaml
beats:
  - name: relève
    actions: {file: storyboard-entree-2.md, section: "### Beat A — la relève"}
    words_per_paragraph: [80, 160]   # owner setting; num_predict derived from it
```

With 33 actions at 80–160 words, entry 2 lands around 2,600–5,300 words.
The range is an owner setting, not a constant of this change.

An action is one dramatic unit, developed by the model into one paragraph:
a gesture or a finding with the concrete matter it carries (objects, hours,
the trade's gestures, the body), in the third person (as today's beat
instructions, so person is not a second variable), present tense. It states
facts, never an intention, and carries no example line to recopy.

The loader refuses: an action containing a bible file name or
workshop vocabulary (existing anti-leak assertions), an intention verb
(`décide`, `veut`, `va` + infinitive), a list shorter than 6 or longer than 14.

## Served prompt (S arm)

```
<common veto line, unchanged>
Ce qui se passe, dans l'ordre — un paragraphe par ligne, développé avec la matière qu'elle porte, rien d'autre :
1. …
2. …
```

The section heading line and the brief's §7 instruction are not served in
the S arm: the list replaces the instruction. Snapshot: a new scenario
`ch7-storyboard` (fake model) freezes the S prompts; `ch7` stays unchanged.

## Measures

| Measure | Why |
|---------|-----|
| Reading-check defects in the final entry 2, and before selection if best-of survived the ablation | the hypothesis (fewer inventions) |
| Plan veto hits per planner (XP B) | the cheapest place to catch a ghost |
| Actions rendered / dropped / added: each action matched to its closest sentence, sentences matched to no action counted as additions | density kept, void refilled |
| Verbatim recopy per action (similarity > 0.8) | doctrine 6 |
| Litany: share of sentences opening on the same construction; repeated discoveries | doctrine 12 |
| Mean sentence length per beat, first vs last third | the trajectory must shorten (brief §2) |
| Words per paragraph against the per-paragraph range; paragraphs that restate the previous one | developed, not padded |
| Owner's grid line: complexity (layers held at once: the line, the proof, the trade, the body) | the density the project is after, not only the absence of defects |
| Planner time + swap (XP B), write time | record only; time is not a criterion of this change |
| **Is the declared movement accomplished?** | owner, aloud, blind |

## Runs

- XP A: arms R, R-long and S, 5 paired seeds each (15 runs). R-long uses
  today's beat instructions with the bounds raised to S's (a variant spec);
  it is the v4 condition that padded, now measured instead of remembered.
  Defect counts are compared per 1,000 words as well as in absolute terms.
- XP B: 6 planners × 3 seeds (18 lists). Lists are vetted and read by the
  owner BEFORE rendering (a list is 30 lines; reading them is cheap). Only
  the lists that pass the veto are rendered, by nemo, with S's served form.
- XP C: per-beat vs per-action on B's best list, 3 seeds each.

## Memory

Planner then writer, never co-resident: `keep_alive: 0` on the planner, then
nemo loads (ADR-0008 pattern). The 14B abliterated model is 9 GB, nemo 13 GB:
co-residence would be 22 GB on 18 GB unified, so the swap is mandatory, not a
choice. The preflight's two-warm-models rule already blocks the unsafe case.

## Firewall

The planner is served exactly what the writer would be: the surface chunks
(retrieval by id) and the brief sections listed above. No deep chunk, no
`chapters/` file other than the brief sections already served today. The
seal test's control 6 already proves `chapters/` is in no collection;
nothing new is indexed. A generated list is a run artifact, never indexed.

## Tests

- Loader: the refusals above, each with its failing case and the draft list
  as the accepting reference (doctrine 4).
- Fake model: a nominal rendering fixture that renders each action, a failing
  fixture that adds a presence (must be caught by the reading checks), a
  planner fixture with one vetoed action (must trigger one re-plan).
- Snapshot `ch7-storyboard` added; `ch7`, `ch2-s7-*` unchanged.
