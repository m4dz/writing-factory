# Tasks: writer-ministral

- [x] Tag `ministral3-14b-q5` on the stage machine (`ollama cp` of the
      measured tag, digest `87501e5270dc`); Modelfile versioned.
- [x] Default `author_model`; docs; ADR-0029.
- [x] Snapshots: only the gesture calls' `model=` header moves.
- [x] `make check` green.
- [x] Actor-mode check: one `factory chat --character judith` session with
      M (in character, French, memory written and reloaded). Blocked
      2026-11-10: the Podman VM does not start (ssh handshake), so no
      ChromaDB. Done 2026-11-11, owner OK: in character, French, terse;
      memory written then reloaded (throwaway `SESSIONS_DIR` and
      `CHROMA_SESSIONS`, collection deleted after). Defects kept for later:
      Markdown italics, third-person stage directions (« *(Elle feuillette…)* »),
      invented bibliography (a Follain title, a publisher, a verse), one
      summary line giving Judith's offer to the visitor.
