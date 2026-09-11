# ADR-0006 — One warm model, coherence from shared external memory

Date: 2026-08-05. Status: accepted.

## Context

The demonstrator serves two roles (author writing chapters, actor answering in
character) for several characters. One design puts one model instance per
character to keep each voice consistent.

## Decision

Multi-instance is rejected. Coherence comes from a shared external memory
(the bible in Markdown, indexed in ChromaDB), not from multiplying models. The
models are *readers* of a truth stored outside them. Author and actor share
the same warm model (`mistral-nemo`); what changes is the system prompt and
the shape of the context.

## Consequences

- One 13 GB model in memory at a time; the machine (18 GB unified) holds no
  more (see ADR-0008 on the QA model swap).
- Character voice is data: the sheet's "voice" chunk with typical lines and
  counter-examples, served by deterministic id.
- The actor mode cannot run during a generation: same model, one slot
  (`409` on chat while generating).
