# ADR-0007 — Three layers; Markdown is canon, ChromaDB is derived

Date: 2026-08-05. Status: accepted.

## Context

The world bible (characters, places, props, scenes) must be edited by a human,
retrieved by the pipeline, and never diverge between the two.

## Decision

Three layers:

- **Storage.** Canonical Markdown in `bible/`, edited by the owner. ChromaDB
  (HTTP server, containerised) is ALWAYS generated from the Markdown, never
  the reverse. Re-indexing is idempotent and purges orphan chunks.
- **Retrieval and orchestration.** LangGraph; the context is assembled per
  request (present characters' sheets, place, relevant previous scenes) into a
  system prompt of 2–3k tokens.
- **Models.** Ollama on the host, reached from containers through
  `host.containers.internal:11434`. Embeddings by `nomic-embed-text` (768
  dimensions, cosine).

Conventions: one chunk per `## ` section, deterministic id `{doc_id}::{slug}`,
chunk prefixed `[doc_id / Title]` before embedding, files `_*.md` never
indexed, HTML comments purged before embedding, scalar metadata only.

## Consequences

- Any state the pipeline needs between chapters is written to Markdown first
  and indexed second (this later applies to roleplay memory, ADR-0015).
- The seven-chunk character sheet (psychology, behaviour, voice, history,
  skills, relations, current narrative state) with only the last chunk updated
  regularly.
- Superseded in part by ADR-0019 (the firewall reshaped what is indexed) and
  by the revamp's per-chapter narrative state (plan §6).
