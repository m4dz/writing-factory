# Architecture decision records

One decision per file, dated, append-only. A superseded decision is not
edited: a new record supersedes it and both link to each other. Format:
context, decision, consequences. Numbers are sequential; the slug is English.

Decisions 0006–0020 were taken before this log existed; they are extracted
from the former `CLAUDE.md`, the handover documents and the implementation
notes, and dated at the time they were taken.

| # | Title | Date | Status |
|---|-------|------|--------|
| 0001 | [Code in English, author material in French](0001-code-in-english.md) | 2026-09-10 | accepted |
| 0002 | [Single package, chapter knowledge as data](0002-package-layout-and-chapter-specs.md) | 2026-09-10 | accepted |
| 0003 | [Experiments are data kept in the repository](0003-experiments-in-repo.md) | 2026-09-10 | accepted |
| 0004 | [Documentation systems: openspec, ADR, three plain docs](0004-documentation-systems.md) | 2026-09-10 | accepted |
| 0005 | [API: mandatory payload, artifacts per run](0005-api-per-run.md) | 2026-09-10 | accepted |
| 0006 | [One warm model, coherence from shared external memory](0006-single-model-shared-memory.md) | 2026-08-05 | accepted |
| 0007 | [Three layers; Markdown is canon, ChromaDB is derived](0007-three-layers-markdown-is-canon.md) | 2026-08-05 | accepted, partly superseded |
| 0008 | [Model triage: nemo writes, Qwen checks, one swap](0008-model-triage.md) | 2026-08-06 | accepted |
| 0009 | [Ollama on the host, loopback only, project launchd agent](0009-ollama-on-host-loopback-launchd.md) | 2026-08-06 | accepted |
| 0010 | [Coherence by violation questions, code-verified](0010-coherence-by-violation-questions.md) | 2026-08-06 | accepted |
| 0011 | [Two retrieval strategies; style served by sections](0011-retrieval-strategies-and-served-style.md) | 2026-08-06 | accepted |
| 0012 | [TTS in the same venv, lazy, never fails the job](0012-tts-in-the-same-venv.md) | 2026-08-07 | accepted |
| 0013 | [Audio switch posed by code; reading bounded in seconds](0013-audio-switch-and-bounded-reading.md) | 2026-08-07 | accepted |
| 0014 | [Actor mode: own chat and page, not OpenWebUI](0014-actor-mode-own-chat-not-openwebui.md) | 2026-08-07 | accepted |
| 0015 | [Telegram operator beeper as an accepted exception](0015-telegram-beeper-exception.md) | 2026-08-08 | accepted |
| 0016 | [Preflight gates on measured causes; two clocks](0016-preflight-and-two-clocks.md) | 2026-08-06 → 25 | accepted |
| 0017 | [The indexing firewall](0017-indexing-firewall.md) | 2026-08-22 | accepted |
| 0018 | [The code owns the gestures](0018-code-owns-the-gestures.md) | 2026-08-22 | accepted |
| 0019 | [The movement method](0019-movement-method.md) | 2026-08-27 | accepted |
| 0020 | [Chapter 7: capped beats, best-of-N, pruning](0020-chapter-7-beats-best-of-pruning.md) | 2026-08-29 → 31 | accepted |
