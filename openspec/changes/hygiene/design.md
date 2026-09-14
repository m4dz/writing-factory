# Design: hygiene

## Moves keep history

Every move is a `git mv`; content is byte-identical, `git log --follow`
works. Removals are `git rm` of files whose content survives elsewhere
(hash-verified) or of launch logs; the list is committed in
`experiments/REMOVED.txt`.

## Manifest reconstruction

Each run directory's `manifest.yaml` is built from the frontmatter of its
`run-*.md` files with a field map (French key → English key, values
verbatim), plus the commit that ADDED the artifacts (not necessarily the code
that produced them) and the list of dropped files with reasons. It is marked
`reconstructed: true` and says so in a note. Seeds and clocks exist only
where the frontmatter of the time recorded them.

## Discarded draws

The five discarded chapter-7 draws in the handover packet are byte-for-byte
the bodies of five journal entries (the journal prefixes a grid header). They
are removed; the journal keeps them with their cause.

## Documents: extract, then delete

Each deleted document's surviving content has a named home (plan §3 table).
The doctrines get one file; decisions get one ADR each with the original
date; procedures go to the runbook; the API contract becomes the `api` spec.
`CLAUDE.md` keeps only what tells the assistant where to look and how to
behave.

## Verification

- `make check` green; the three prompt snapshots identical (the briefs moved,
  their content did not).
- The lint snapshot's 34 sources found at their new paths, golden file names
  unchanged.
- No document references a removed path (grep over `docs/`, `README.md`,
  `CLAUDE.md`, `openspec/`).
