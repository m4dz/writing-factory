# ADR-0010 — Coherence: facts → violation questions → per-scene answers, code-verified

Date: 2026-08-06. Status: accepted.

## Context

Three failures shaped the protocol. (a) Checking facts on the whole chapter
(~2000 words) turns Qwen into a workshop critic. (b) A YES/NO on a fact files
"not mentioned" under NO: false positives everywhere; an ABSENT label helps
but is not enough. (c) Classifying an ABSTRACT, especially NEGATIVE fact
("Élara does not know that…", "Kael never confesses") is beyond a 7B: it read
the full confession and classed it CONFORMING to "Élara does not know". That
is entailment, not reading.

## Decision

- Each fact is converted into an EVENT question whose YES means violation
  ("Does the text show Élara discovering that…?"), then asked scene by scene.
  Answering "does this text show X?" IS reading.
- Every YES must cite the text, and the CODE checks the citation is really in
  the scene (the model sometimes copies the fact instead); otherwise the
  finding is demoted to "check by hand", never counted as a violation.
- Two filters born of real false positives: `derive_facts` excludes the
  TRANSIENT state of the sheets (what the chapter exists to change); every
  YES gets a COUNTER-CALL (`_confirm`) asking the single question alone, in
  severe mode, one-word answer. Cost ~8 s.
- Negative world facts ("nobody else enters the house") are ADDED, never
  derived: a model summarising sheets states what is, not what is excluded.
- The same protocol checks the PLAN before writing: a plan that contradicts
  the bible condemns fourteen minutes of writing in advance.

## Consequences

- General lesson, reused for the actor mode: give the small model a READING
  task, never an INFERENCE task.
- Chapter-level facts are derived once by the plan node and reused by the
  coherence node, so the chapter is judged by the rules the plan received.
