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

## Served prompt v2 — question + start of the answer (after the smoke run)

Smoke run v1 (seed 111111, `f3e5ac6`): discovery 3/3 and doubt 3/3 variants
recopied the entry (2–4 sentences); the plan list was not echoed. The more
context before the prefix, the more nemo opens by copying it; the « ne
réécris pas » instruction does not hold. Owner's choice (2026-10-19): a
hybrid of « continue the answer » and « instruction last ».

- **Question (user turn)**, in this order: voice (folded in, see below) →
  map with states → the text already written, as a reference block → CE
  TEMPS-CI + `Il finit quand :` → beat suffix. The task is the last thing
  read before the answer.
- **Start of the answer (assistant turn)**: the last paragraph already
  written (for beat A: the served quotation). nemo continues it; Ollama
  returns only the new tokens. Done steps live in the history, not in an
  instruction.
- **System prompt folded into the question.** nemo's template drops
  `$.System` unless the last message is the user's; it renders it at the
  head of the last `[INST]` otherwise. Folding `FRENCH_GUARD + system` at
  the head of the user turn reproduces R's rendering of that turn.
- Probe (6 calls, no voice): 0/6 recopies; 2/3 continuations of a text
  ending on a full stop answered as an assistant (« Je vais corriger
  cela. Voici… »). Watched in the smoke run; a check is added only if it
  shows there.
- `prompts.md` records the question and, apart, the start of the answer.
- `map` is unchanged (arm B evidence); `plan` now means v2. The smoke run
  v1 is replayable at its commit only.

## Served prompt v3 (after smoke v2)

Smoke v2 (`695b197`): no recopy, but 6/9 variants empty — the begun answer
ended on a full stop and nemo closed at once (probe: 3/3 empty; with a blank
line after it, 3/3 written); empty variants scored 0, no defect; the doubt
wrote its end condition into the text. v3 (owner's go):

- the begun answer ends with a blank line;
- `plan` selection: fewer than 2 sentences → « vide ou trop court », −10;
- the end condition moves into the state line of the current time
  (`→ 2. CE TEMPS-CI (ci-dessous) — il finit quand : …`), no longer served
  after the task.

Measured, not checked: beats paraphrasing their instruction in the first
person; to be compared across R and P at the reading.

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
