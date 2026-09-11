# retrieval

## Purpose

Current behaviour of indexing (`indexer/index.py`) and context assembly
(`orchestrator/retrieval.py`). Decisions: ADR-0007, ADR-0011, ADR-0017.

## Requirements

### Requirement: The index is derived from the bible under the firewall

Indexing SHALL read only `bible/**/*.md` not starting with `_`, SHALL skip
`profond/` and `style-auteur.md` entirely, SHALL keep only `[SURFACE]` layer
blocks in mixed files and only numbered sections in character sheets, SHALL
copy only whitelisted metadata keys, and SHALL translate the narrator's first
name to "la narratrice" in the indexed text and labels. It SHALL be
idempotent and purge orphan chunks. It SHALL never touch the `sessions`
collection.

#### Scenario: Deep block in a mixed file
- **WHEN** a section contains a `### [PROFOND …]` block
- **THEN** no text of that block appears in any chunk

### Requirement: Chunk identity

A chunk SHALL be one `## ` section, id `{doc_id}::{slug}` with the section
number stripped, document prefixed `[doc_id / Title]`, HTML comments removed.

#### Scenario: A numbered section
- **WHEN** the sheet has `## 1. Voix`
- **THEN** the chunk id is `judith::voix` and its document starts with `[la narratrice / Voix]`

### Requirement: Writing context by deterministic id

The system prompt for writing SHALL include, for each present character, the
`voix`, `etat_narratif_courant` and `psychologie` chunks fetched by id; fact
derivation SHALL use `psychologie`, `histoire`, `relations`; acting SHALL use
the six acting sections. Previous entries SHALL NOT be served during writing.

#### Scenario: Writing prompt
- **WHEN** the system prompt is assembled with RAG for `judith`
- **THEN** it contains the voice and current-state chunks and no history chunk

### Requirement: Style served by sections from disk, examples stripped

The style sheet SHALL be read from disk, never retrieved, and served by named
sections per role (writing: Narration, Lexique et registre, Interdits;
review: Interdits, Phrase et rythme; plan: none), with "Écrire / Ne pas
écrire" example lines removed from the served text only.

#### Scenario: Example line
- **WHEN** a served section contains `**Ne pas écrire :** perplexe…`
- **THEN** the served text keeps the rule and drops the example line

### Requirement: The routing journal

Every collection access SHALL be recorded so that a run can prove which
collections it queried.

#### Scenario: One writing run
- **WHEN** a run completes with RAG
- **THEN** the routing journal lists only the `auteur` collection

### Requirement: The seal is proven, not presumed

The seal test SHALL audit the content of the author collection against a
manifest of allowed sources, a lexicon of leak words and a list of deep
markers, SHALL test the splitter on the narrator sheet, SHALL inject a deep
chunk as a positive witness and require it to come back before removing it,
and SHALL fail explicitly on an empty set.

#### Scenario: Positive witness
- **WHEN** the seal test injects a deep chunk
- **THEN** the queries return it; the test fails if they do not, and the chunk is removed afterwards
