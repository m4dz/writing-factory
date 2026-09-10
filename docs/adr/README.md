# Architecture decision records

One decision per file, dated, append-only. A superseded decision is not
edited: a new record supersedes it and both link to each other. Format:
context, decision, consequences. Numbers are sequential; the slug is English.

Decisions taken before this log existed are being extracted from the former
`CLAUDE.md` (revamp step 3) and dated at the time they were taken.

| # | Title | Date | Status |
|---|-------|------|--------|
| 0001 | [Code in English, author material in French](0001-code-in-english.md) | 2026-09-10 | accepted |
| 0002 | [Single package, chapter knowledge as data](0002-package-layout-and-chapter-specs.md) | 2026-09-10 | accepted |
| 0003 | [Experiments are data kept in the repository](0003-experiments-in-repo.md) | 2026-09-10 | accepted |
| 0004 | [Documentation systems: openspec, ADR, three plain docs](0004-documentation-systems.md) | 2026-09-10 | accepted |
| 0005 | [API: mandatory payload, artifacts per run](0005-api-per-run.md) | 2026-09-10 | accepted |
