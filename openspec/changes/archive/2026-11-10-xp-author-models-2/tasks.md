# Tasks: xp-author-models-2

## 1. Setup

- [x] Branch from `beat-guard-model-text` (guard fix in).
- [x] Pull Mistral Small 3.2 24B Q3_K_M; template checked (no default
      system prompt, begun answer continued); Modelfile if needed.
- [x] Smoke S, seed 111111.

## 2. Run

- [x] N, M, S × 731667, 139026, 487914.
- [x] Table: recital, third person, defects, words, time.
- [x] Blind set: entry 2 of the nine chapters, shuffled, key closed.

## 3. Conclude

- [x] Owner verdicts; rule applied; journal entry (with the guard-fix line
      for `beat-guard-model-text`, M/781771 as trigger).
- [x] Canon-leak check against `bible/profond/` (no 4-gram outside served
      text).
- [x] Decision: W = M (owner, 2026-11-10). Follow-ups in their own changes:
      entry-1 matter in the first person (owner), entry-1 best-of (code),
      ADR for the writer, actor-mode check, default `author_model`.
