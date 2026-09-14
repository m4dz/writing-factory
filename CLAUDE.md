# CLAUDE.md — writing-factory

Routing and conventions for the assistant. Everything else lives in the
documents below; do not restate them here.

## Read first

- `docs/doctrines.md` — the working rules. Every change is checked against them.
- `docs/architecture.md` — one map of what runs.
- `docs/plans/2026-09-quality-campaign.md` — the current plan: the levers on
  the prose, the run protocol, the status table. `2026-09-revamp.md` is the
  restructuring that preceded it, done.
- `openspec/config.yaml` — project context and invariants; `openspec/specs/`
  the current behaviour; `openspec/changes/` the proposals.
- `docs/adr/` — decisions, with dates. `docs/runbook.md` — operations.

## Non-negotiable

- Local only. No cloud API, no external logging (ADR-0015 is the one exception).
- The firewall: `bible/profond/`, `experiments/`, `docs/` are never indexed,
  never served, never named to the model. The seal test is re-proven at each
  reindex, never presumed.
- The owner owns canon and author material: `bible/`, `chapters/`, every
  served quotation, movement or drift passage, the doctrines. Propose, never edit.
- The model supplies matter; the code holds the gesture. Shown is recited.

## Conventions

- Code, comments, docstrings, identifiers, file names, engineering docs:
  English (ADR-0001). Prompts, bible, chapter specs, journal: French.
- `make check` green before any task is declared done. Served prompts are
  frozen in `tests/snapshots/`; regenerate only when the change intends it,
  and name the prompt moved in the openspec proposal.
- One openspec change per revamp step and per experiment; one ADR per
  decision, append-only.
- Chapter knowledge is data (`chapters/`), configuration is a settings object,
  neither lives in pipeline code.
- Runs go to `experiments/runs/<date>-<slug>/` with a manifest; failed runs to
  `experiments/journal/`. Nothing is thrown away, nothing is duplicated.
- Never conclude on one run. One variable between two measurements.

## Working with the owner

Challenge proposals rather than agree. Explain the architectural why. Verify
before implementing; contest received specs. Look for the defect each fix
creates where it touches. Author decisions (canon, served phrases, grid
arbitrations, the final pass, the public framing) are raised as questions,
never taken. Direct, factual, dense prose; argued disagreement over
comfortable agreement. A "go" means the validated scope, nothing more.
