# Design: plan-state-beats

## The harness principles, and where each lands

| harness | here |
|---|---|
| plan approved before execution | brief §7 beats (later: the storyboard), owner canon |
| code owns the task list and its states | `_plan_state(sheet, current)`: states computed from the beat index, never from model output |
| one task in progress | one beat per call (unchanged) |
| completion criterion per task | `Finit quand :` per beat, owner-written |
| verify each step before the next | progress gate in `_score_beat` (+ existing checks) |
| done steps summarized, not replayed | done times shown by their label (first sentence of the instruction; later the storyboard action); the text itself is the prefix, already served |
| re-plan on failure, no infinite loop | best-of redraws; all variants failing → keep the least bad, warning in the manifest |

## Served prompt (`beat_context: plan`), discovery beat

```
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.
Ce que l'entrée accomplit : <movement>
Ce qui est là, à ta disposition, jamais une liste à épuiser : <matter>
Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  → 2. CE TEMPS-CI (ci-dessous)
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas
Ce que le texte ne fait pas : <vetos>

CE TEMPS-CI :
<instruction>
Il finit quand : <end condition>      (only if the brief gives one)

L'entrée est DÉJÀ COMMENCÉE par ce texte… (prefix, unchanged)

<beat suffix, unchanged>
```

The `✓ / → / ○` marks are code glyphs, not workshop words; the entry guard
(`META_TERMS`, `MACHINERY`) runs on the assembled prompt as today. Risk
named: nemo may echo the list (« Je passe maintenant à… »); the lint's
meta-commentary checks and the reading catch it.

## End conditions — drafts for the owner (brief §7)

The last sentence of each instruction already reads as one; the owner
decides whether to make it explicit:

- Beat A — la relève: *Finit quand : elle a nommé l'écart — la ligne dit
  qu'elle a mis les couverts, elle ne s'en souvient pas.*
- Beat B — la découverte: *Finit quand : elle a commencé à ranger ; les
  quatre objets ont été trouvés, chacun une fois.*
- Beat C — le doute: *Finit quand : elle repose le crayon.*

Loader: a line starting `Finit quand :` under a `### Beat` heading becomes
`BeatSpec.ends` and is removed from the instruction. Absent → `""`, no line
served; the `blind` and `map` prompts never serve it, so production is
unchanged even after the owner adds the lines.

## Progress gate

Measured on arm B: the recopying beats shared 4/4 sentences with the
previous beat; R's beats shared 0–1 of 3–4.

- **Recopy**: ≥ 2 sentences of the variant (normalized: case, spaces,
  quotes) already present in the prefix of THIS entry → defect « recopie »,
  −10 (veto weight, as a resolution). The served quotation [CIT-2] is
  excluded (relève legitimately reads it).
- **Restart of an earlier time**: measured only (reported in
  `variants.md`), not scored: naming an object again is legitimate in the
  doubt beat; the reading decides first.
- Applies in every `beat_context`: in `blind` it changes production
  selection. To keep R comparable, the gate is ON only when
  `beat_context != blind` for this experiment; making it production-wide
  is a separate decision after the reading.
- With `beats_n = 1` there is nothing to redraw: the gate only warns. The
  experiment keeps `beats_n = 3`, as R.

## Arms

| arm | command | runs |
|---|---|---|
| R | (drawn) `20261018-beats-see-movement` R × 3, never read | reused |
| P | `--chapter 7 --override beat_context=plan` | seeds 395959, 528559, 781771 |

Smoke run first, seed 111111, not counted: checks that the doubt beat is no
longer recopied and the list is not echoed. If it fails, stop and report.

R reuse is valid: production prompts are byte-identical across the commits
since (ch7 snapshot), selection unchanged (`detector-fixes` not merged).

## Decision rule (written before the runs)

P becomes the beat mechanism for `storyboard-density` when, on the owner's
blind reading of R × 3 + P × 3: P is better than R on ≥ 2 seeds of 3, AND
P's entries carry fewer "invents" notes than R's, AND no veto defect (old
checks + « recopie ») appears in P that R does not have, AND P's mean
entry-2 length is ≥ R's (365 words). P is rejected when worse than R on
≥ 2 seeds, or when the doubt is missing or recopied in ≥ 2 final entries.
Otherwise inconclusive.
