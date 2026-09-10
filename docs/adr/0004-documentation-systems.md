# ADR-0004 — Documentation systems: openspec, ADR, three plain docs

Date: 2026-09-10. Status: accepted.

## Context

`CLAUDE.md` grew to 657 lines and 43 KB. About a third of it is measurement
history, a quarter is decision records, an eighth is operating procedure, and
about 15 % is actual instruction to the assistant. The doctrines are stated
in full both there and in `docs/passation-generale.md`. Four of the seven
files in `docs/` are referenced by nothing. The README describes a frontend
that was rejected a month ago.

The talk repository freezes the API contract with openspec. The owner asked
for PRD, ADRs and runbooks, and questioned whether openspec specs would
duplicate a PRD.

## Decision

Four systems, one role each:

1. **openspec** (`openspec/`, CLI 1.13, schema `spec-driven`). `config.yaml`
   carries the project context: purpose, invariants, conventions. This is the
   PRD's job, so there is no separate PRD. `specs/<capability>/spec.md`
   describes current behaviour as requirements and scenarios, one per
   capability: api, pipeline, chapter-spec, retrieval, eval, roleplay, render.
   `changes/<name>/` holds proposals with design and tasks, archived into
   `specs/` when done. One change per revamp step, then one per experiment.
2. **ADR** (`docs/adr/`). Decisions with context and consequences, dated,
   append-only. openspec has no durable decision log (a change's `design.md`
   is archived with it), so ADRs are kept. Decisions taken before this log
   are extracted from `CLAUDE.md` with their original dates.
3. **Plain docs** (`docs/`): `architecture.md` (one map: package, graph, data
   flows), `runbook.md` (operations, followed under pressure), `doctrines.md`
   (the doctrines and the falsification rule, one home), `plans/`.
4. **Experiments** (`experiments/`): data, see ADR-0003.

`CLAUDE.md` becomes routing and agent conventions, at most 60 lines.
`README.md` becomes an entry point for a newcomer. Outdated documents are
deleted once their surviving content has a new home; nothing is archived for
its own sake.

## Consequences

- The openspec CLI is a Node tool. It collects anonymous usage statistics by
  default; the runbook sets `OPENSPEC_TELEMETRY=0` on the machine, in line
  with the local-only rule.
- The generated Claude Code skills and commands under `.claude/` are
  versioned; `.gitignore` excludes only the harness worktrees.
- A change that alters served prompts, the API or the chapter spec schema
  must come with its openspec change; a code-only refactor needs none.
- Duplicated statements are resolved by deletion, not by cross-reference:
  the doctrines exist once.
